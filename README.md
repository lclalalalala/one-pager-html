# one-pager-html

A [Codex / Agent skill](https://github.com/vercel-labs/skills) for building **single-file, self-contained HTML one-pagers**.

A one-pager communicates fast without losing richness. Every page ships three layers in one `.html` file:

1. **Text source** — a Markdown block embedded in `<head>`, the single source of truth for the message.
2. **Visual body** — a hand-built projection of the text; layout, charts, and styling are yours to decide.
3. **Appendix** — depth collapsed in `<details>`, available on demand without cluttering the page.

The file works offline with zero external requests, so it survives being passed around in chat or email without losing information.

## Install

```sh
npx skills add <owner>/one-pager-html --skill one-pager-html
```

Then ask your agent for a one-pager on any topic.

## What the skill provides

- `assets/template.html` — a starter skeleton with responsive layout primitives, neutral design tokens, a plain-text viewer dialog, and appendix wiring. Every part is replaceable.
- `scripts/validate.py` — checks self-containment, text/visual section coverage, appendix wiring, and file size.

## Layout

| Dir | Purpose |
| --- | --- |
| `release/` | Published skill, installable via `npx skills` |
