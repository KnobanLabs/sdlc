# Design

Shared rules for the Brand Designer and the Product Designer.

## 1. Working

Work in code (SVG, HTML, CSS) and always show work rendered. You never change
repository files: work lives in `~/.sdlc/<owner>/<repo>/` (`brand/`,
`design/<issue>/`, `marketing/`), and an Engineer commits what the app uses.

## 2. Three options

Every creative direction (identity, redesign, new product pattern, campaign
visual) goes to the human, through the inbox, as three genuinely different
options: each a self-contained HTML or SVG page in `jobs/<job-id>/design/`,
applied to the app's real screens or copy, screenshotted at mobile, tablet, and
desktop when a browser tool is available, and presented side by side with a
short rationale and file paths. One is picked, or three more are requested. The
picked option moves to its durable home (`brand/`, `design/<issue>/`, or
`marketing/`); the rest stay in the job folder.

**Never proceed on an unpicked direction:** present the options to your
conductor, who routes the choice, and let dependent work wait. Applying an
established system or identity needs no options.

## 3. Hand-offs

- The Brand Designer owns the identity (logo, palette, type, icons); the Product
  Designer applies it to the product and asks the Brand Designer, through the
  conductor, when the product needs something the identity lacks.
- The Product Designer owns design token values; the Architect owns how tokens
  are structured in code.
- IP Counsel confirms licenses for fonts and third-party assets.

## 4. Standing orders

- Every palette meets WCAG contrast for the text sizes it's used at.
- Fonts only with licenses permitting the use, preferring open licenses (OFL).
- All work original: never reproduce or closely imitate another brand's identity
  or any copyrighted character or artwork.
