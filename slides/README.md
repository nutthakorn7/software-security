# Slides

Lecture slides live here. Two supported workflows — pick one (or mix):

## Option A — Markdown slides with Marp (version-controlled, recommended)

Write each lecture as a Markdown file and render to HTML/PDF/PPTX with [Marp](https://marp.app/).

```bash
# install once
npm i -g @marp-team/marp-cli

# render a deck
marp slides/week01.md -o slides/out/week01.html   # HTML
marp slides/week01.md --pdf                         # PDF
marp slides/week01.md --pptx                        # PowerPoint
```

A deck file starts with front-matter:

```markdown
---
marp: true
theme: default
paginate: true
---

# Week 1 — Security Mindset & Threat Modeling
Software Security · <Your Name>

---

## What does "secure" mean?
- CIA triad
- Trust boundaries
- Attack surface
```

Decks can be published automatically to **GitHub Pages** so students view them in the browser (no download). See `.github/workflows/` to add a Pages build step when ready.

## Option B — Google Slides (link out)

Author in Google Slides and link the deck per week below. Good for image-heavy decks and quick edits; not version-controlled.

| Week | Deck link |
|------|-----------|
| 1 | _add link_ |
| 2 | _add link_ |
| … | … |

> Decision pending — keep both rows until you choose. For a security course where OWASP content changes yearly, Marp keeps slides in sync with the labs.
