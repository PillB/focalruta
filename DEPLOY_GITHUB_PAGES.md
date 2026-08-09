# Deploy FocalRuta to GitHub Pages

The generated tree at `dist/canon6d_sota_hosted` includes `.github/workflows/pages.yml` for an artifact-based Pages deployment.

## Publish

1. Run `python3 scripts/build_dual_release.py` and put the contents of `dist/canon6d_sota_hosted` at the root of the intended GitHub repository.
2. In **Settings → Pages**, select **GitHub Actions** as the source.
3. Push to `main` (or change the workflow trigger if needed), or run the workflow manually.
4. The workflow uploads that already-clean runtime tree and deploys it.

## Runtime files

The published artifact includes the main site, Field Card, six standalone plan pages, local CSS/icon, canonical data, teaching/plan diagrams, manifest and service worker. Python generators, QA artifacts and internal notes are not published.

## Hosted/PWA behavior

- `manifest.webmanifest` provides install metadata.
- `sw.js` provides a small app-shell cache plus runtime caching for local resources.
- Service-worker registration is guarded to HTTP/HTTPS and therefore does not interfere with the self-contained `file://` iPhone artifact.
- The main experience remains usable if service workers are unsupported; offline installation is an enhancement, not the only execution path.

## Production principles

- No Tailwind Play CDN runtime dependency.
- No required third-party font/icon dependency.
- Relative local paths for GitHub project Pages subpaths.
- `.nojekyll` included.
- Touch controls target at least a comfortable mobile footprint; modal and bottom-nav controls are designed above the WCAG 2.2 minimum target-size threshold.
- Public artifacts do not expose the residential street number.

The release tree and workflow are ready for publication. The remaining external prerequisite is an authenticated GitHub CLI session and the destination repository; after authentication, publish the contents of `dist/canon6d_sota_hosted` on `main`, enable GitHub Actions as the Pages source, and validate the resulting public URL with the same Playwright gates.
