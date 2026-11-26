---
name: one-pager-html
description: >
  Create single-file, self-contained HTML one-pagers: concise visual briefing pages with a
  plain-text Markdown source embedded in the head, a visually optimized body, and collapsible
  detail appendices. Use whenever the user wants a one-pager, 单页说明, 一页纸报告, briefing page,
  shareable summary document, or asks to turn notes/data into a single HTML file for sharing
  via chat or email — even if they don't say "one-pager" explicitly.
---

# One-Pager HTML

A one-pager communicates fast without losing richness. This skill produces ONE `.html` file
with three layers, built in strict order: text first, visuals second, appendix third.

## Architecture

```
<head>
  <script type="text/markdown" id="onepager-source">   ← Layer 1: the source of truth
    # Title
    ## Section            ← each maps to one visual section
    ## Detail [appendix]  ← maps to a <details> block
  </script>
</head>
<body>
  visual sections         ← Layer 2: projection of Layer 1, style is free
  <details> appendices    ← Layer 3: depth, collapsed by default
  "view plain text" dialog
</body>
```

The text layer is invisible on the page. It lives at the top of the file so a human or agent
can read, diff, and edit the entire message within the first screenful. The visual layer is a
hand-built projection of it — not a runtime render — so visual freedom is unlimited, but the
text always leads.

## Hard constraints (never break these)

1. **Single file, zero external requests.** No CDN, no external fonts/images/scripts/styles.
   System font stacks; inline SVG or data-URI images. A recipient must be able to double-click
   the file offline and lose nothing.
2. **No large media.** Images and tables are the norm. Embedding video as data URI bloats the
   file ~33% and breaks chat/email transfer — avoid it; external media links are forbidden
   regardless. The validator warns above 5 MB.
3. **Text layer stays in `<head>`** inside `<script type="text/markdown" id="onepager-source">`.
   Never place the literal string `</script>` inside it.
4. **Every visual section carries `data-source="<exact ## heading>"`** pointing back to its
   text section. This is how drift is detected.

## Workflow

Copy `assets/template.html` to start. It provides the skeleton, responsive layout primitives,
neutral design tokens, the plain-text dialog, and appendix wiring — every part is replaceable.

### Step 1 — Fix the text (do not touch visuals yet)

Iterate with the user on the Markdown inside `#onepager-source` until the content is agreed:

- One `#` document title.
- Each `##` becomes one visual section. Keep headings short and stable — they are IDs.
- Recommended: make the first line under each `##` a one-sentence takeaway, then supporting
  facts. Skip this when the page presents facts without conclusions.
- Mark depth sections with a trailing ` [appendix]` in the heading. Their content belongs in
  Layer 3, not the main flow.
- Aim for a page readable in ~2 minutes; push detail into `[appendix]` sections rather than
  deleting it. Rich information stays in the file, just not on display.

### Step 2 — Build the visuals

Project each `##` section into a visual `<section data-source="...">`. Style is the user's
call: ask for direction (or propose one), then express it by editing design tokens
(`--color-*`, `--font-*`, radii, shadows) and decoration. Keep the layout skeleton:

- Charts: generate inline SVG by default (`viewBox`, scales with container). Static is fine;
  add small vanilla-JS interaction only when it earns its place.
- Tables: use the template's `.table-wrap` (scrollable region, sticky headers, stacks into
  cards on narrow screens).
- Key figures/conclusions should visually dominate; supporting text recedes.
- Link from a visual claim to its appendix with `<a href="#appendix-...">详情 →</a>`.

### Step 3 — Wire the appendices

Each `[appendix]` text section becomes a `<details class="appendix" data-source="...">` with
a `<summary>` naming the topic. Collapsed by default; no print handling needed.

### Step 4 — Validate

```sh
python3 scripts/validate.py <file.html>   # or: uv run --no-project python scripts/validate.py <file.html>
```

Checks: zero external references, source block present and intact, every non-appendix text
section covered by a visual section (and vice versa), appendix wiring, viewport meta, file
size. Fix every ERROR before delivering. Then view the page at 375 px and desktop width:
no horizontal scroll, body text ≥16 px, tap targets ≥44 px.

## Editing an existing one-pager

Always in this order — it prevents text/visual drift:

1. Edit the Markdown in `#onepager-source` first.
2. Sync the affected visual sections / appendices.
3. Re-run the validator.

To extract the text for review or forwarding:

```sh
sed -n '/id="onepager-source"/,/<\/script>/p' file.html | sed '1d;$d'
```

The page also has a corner button opening a dialog with the plain text and a copy button —
readers use it to forward the content as text.

## Extension protocol (for creators and other skills)

This skill provides the baseline; richer content is the creator's choice. Rules for anything
embedded (interactive charts, animations, flow diagrams, controls):

- Mount inside a visual section at `<div data-embed="<name>" data-source="<heading>">`.
- Everything inline: `<svg>`, `<style>`, `<script>`, data URIs. No network fetches at runtime.
- Keep `data-source` traceability intact; the validator only checks section-level coverage,
  so wording inside visuals may differ from the text.
- Respect the mobile baseline: scale to container, no fixed pixel widths that overflow 375 px.
- Heavy interactivity is allowed but should degrade gracefully (content understandable with
  JS disabled is a plus, not a requirement).

## What the template does NOT decide

Color palette, typography personality, spacing rhythm, chart aesthetics, iconography, motion.
The tokens ship with neutral defaults so the skeleton is usable immediately, but a styled
one-pager should replace them. Two one-pagers from this skill should not look alike unless
their creators chose the same style.
