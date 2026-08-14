# PACE Personal Website

This is the public personal website project for Dr. Shenglai Yin.

The website is built with [Quarto](https://quarto.org/). Only content in this directory is included in the website build and deployment process; other repository materials are not automatically published on the website.

## Editing the Website

The primary files are:

- `index.qmd`: Home page and personal introduction
- `research.qmd`: Research topics, toolkit, and funding projects
- `publications.qmd`: Publications
- `contact.qmd`: Contact information
- `_quarto.yml`: Navigation and site-wide settings
- `pace-site.css`: Visual styles

To preview the website from this directory:

```sh
quarto preview
```

To build the website:

```sh
quarto render
```

The rendered website is saved in `website/_site/`.

## Publishing

The GitHub Pages workflow is located at `.github/workflows/pages.yml` in the repository root. It builds and deploys the website when changes are pushed to `main`, and it can also be run manually.

For an optional Cloudflare Pages deployment:

1. Set the project root directory to `website`.
2. Set the build command to `bash scripts/cloudflare-build.sh`.
3. Set the output directory to `_site`.

## Prepublication Check

Before publishing a university, department, office address, or other institutional information, confirm that it is accurate and appropriate for public release.
