# Guy Rofe — Static Rebuild

This repository contains a static rebuild of Guy Rofe's photography portfolio based on the Wix exports gathered in `/guy`. The new site is handcrafted for GitHub Pages, with local assets, modular CSS/JS, and accessible HTML.

## Structure

```
├── index.html        # Home / editorial landing
├── sports.html       # Sports archive grid
├── events.html       # Events & culture coverage
├── how-they-feel.html# Feature story prototype
├── scripts/
│   ├── css/          # Base + page-level styles
│   └── js/           # Site utilities and page scripts
└── src/
	├── home/        # Hero + editorial assets
	├── sports/      # Sports gallery images
	├── events/      # Event gallery images
	└── stories/     # Long-form article assets
```

## Development

1. Serve the site locally:

```bash
cd /Users/nathanbrown-bennett/TildeSec/GuyRofe/GuyRofe
python -m http.server 8000
```

2. Visit `http://localhost:8000` to preview the pages. The modular CSS/JS files are plain ES5 and require no build tooling.

## Next steps

- Translate remaining long-form article pages from the Wix export, mirroring any additional inline imagery under `src/`.
- Add performance optimisations (responsive `srcset`, AVIF/WebP variants, minified bundles) once the visual QA is complete.
- Wire analytics or form handlers if required by the production brief.
