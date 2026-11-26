#!/usr/bin/env python3
"""Validate a one-pager HTML file: self-containment, text/visual coverage, wiring.

Usage: python validate.py <file.html> [--max-size-mb 5]
Exit code 1 if any ERROR is found.
"""

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SOURCE_ID = "onepager-source"
SIZE_WARN_MB = 5.0


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.source_text = None
        self._in_source = False
        self.visual_sections = []
        self.appendices = []
        self.appendix_ids = set()
        self.external_refs = []
        self.has_viewport = False
        self.ids = set()
        self.anchor_hrefs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "script" and attrs.get("id") == SOURCE_ID:
            self._in_source = True
            self.source_text = ""
        if tag == "meta" and attrs.get("name", "").lower() == "viewport":
            self.has_viewport = True
        if tag == "section" and "data-source" in attrs:
            self.visual_sections.append(attrs["data-source"])
        if tag == "details" and "data-source" in attrs:
            self.appendices.append(attrs["data-source"])
            if "id" in attrs:
                self.appendix_ids.add(attrs["id"])
        if tag == "a":
            href = attrs.get("href", "")
            if href.startswith("#"):
                self.anchor_hrefs.append(href[1:])
        for attr in ("src", "href", "poster"):
            value = attrs.get(attr, "")
            if re.match(r"^(https?:)?//", value.strip(), re.IGNORECASE):
                self.external_refs.append(f"<{tag} {attr}={value!r}>")
        if tag == "link" and attrs.get("rel", "").lower() in ("stylesheet", "preconnect", "preload", "dns-prefetch"):
            self.external_refs.append(f"<link rel={attrs.get('rel')} href={attrs.get('href', '')!r}>")

    def handle_endtag(self, tag):
        if tag == "script" and self._in_source:
            self._in_source = False

    def handle_data(self, data):
        if self._in_source:
            self.source_text += data


def parse_source_sections(markdown):
    visual, appendix = [], []
    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = match.group(1)
        if re.search(r"\[appendix\]\s*$", heading):
            appendix.append(re.sub(r"\s*\[appendix\]\s*$", "", heading))
        else:
            visual.append(heading)
    return visual, appendix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--max-size-mb", type=float, default=SIZE_WARN_MB)
    args = parser.parse_args()

    errors, warnings = [], []
    raw = args.file.read_bytes()
    html = raw.decode("utf-8", errors="replace")

    size_mb = len(raw) / 1024 / 1024
    if size_mb > args.max_size_mb:
        warnings.append(f"file size {size_mb:.1f} MB exceeds {args.max_size_mb} MB; chat/email transfer may struggle")

    collector = Collector()
    collector.feed(html)
    collector.close()

    if collector.source_text is None:
        errors.append(f'missing <script type="text/markdown" id="{SOURCE_ID}"> in the document')
        visual_src, appendix_src = [], []
    else:
        if "</script" in collector.source_text.lower():
            errors.append("source block contains '</script' — it breaks the HTML")
        if not re.search(r"^#\s+\S", collector.source_text, re.MULTILINE):
            errors.append("source block has no '# Title' heading")
        visual_src, appendix_src = parse_source_sections(collector.source_text)
        if not visual_src:
            errors.append("source block has no '## ' visual sections")

    for ref in collector.external_refs:
        errors.append(f"external reference breaks self-containment: {ref}")
    for match in re.finditer(r"""(?:url\(\s*['"]?)(https?://[^)'"]+)""", html, re.IGNORECASE):
        errors.append(f"external reference breaks self-containment: CSS url({match.group(1)})")
    for match in re.finditer(r"""@import\s+['"]?(https?://[^'";)]+)""", html, re.IGNORECASE):
        errors.append(f"external reference breaks self-containment: @import {match.group(1)}")

    if not collector.has_viewport:
        errors.append('missing <meta name="viewport"> — mobile rendering will break')

    for heading in visual_src:
        if heading not in collector.visual_sections:
            errors.append(f'text section "## {heading}" has no visual <section data-source="{heading}">')
    for heading in collector.visual_sections:
        if heading not in visual_src:
            errors.append(f'visual section data-source="{heading}" has no matching text section')
    for heading in appendix_src:
        if heading not in collector.appendices:
            errors.append(f'appendix section "## {heading} [appendix]" has no <details data-source="{heading}">')
    for heading in collector.appendices:
        if heading not in appendix_src:
            errors.append(f'appendix data-source="{heading}" has no matching [appendix] text section')

    duplicates = {h for h in collector.visual_sections if collector.visual_sections.count(h) > 1}
    for heading in sorted(duplicates):
        warnings.append(f'duplicate visual sections for data-source="{heading}"')

    for target in collector.anchor_hrefs:
        if target and target not in collector.ids:
            warnings.append(f'anchor href="#{target}" points to a missing id')

    if SOURCE_ID in collector.ids and "plain-text-dialog" not in collector.ids:
        warnings.append("no plain-text dialog found; readers lose the copy-as-text path")

    print(f"Checked: {args.file} ({size_mb:.2f} MB)")
    print(f"  text sections: {len(visual_src)} visual, {len(appendix_src)} appendix")
    print(f"  visual coverage: {len(collector.visual_sections)} sections, {len(collector.appendices)} appendices")
    for warning in warnings:
        print(f"  WARN: {warning}")
    for error in errors:
        print(f"  ERROR: {error}")
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
