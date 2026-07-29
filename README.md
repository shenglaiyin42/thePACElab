# PACE Lab website

Public website for **PACE Lab — Pathogens, Animal Movement, Changes, and Ecology**.

The site is built with [Quarto](https://quarto.org/) and is designed to be straightforward to update without web-development experience.

## Edit the site

Each public page is a plain-text `.qmd` file:

- `index.qmd` — home page and lab overview
- `people.qmd` — PI profile and future lab members
- `publications.qmd` — publication list
- `contact.qmd` — contact and affiliation details
- `_quarto.yml` — navigation, footer, and site-wide settings
- `styles.css` — visual styling

To update a page, edit its text, save the file, and preview the result with:

```sh
quarto preview
```

To build the publishable site:

```sh
quarto render
```

Quarto writes the finished website to `_site/`.

## Publish with GitHub and Cloudflare Pages

After creating a GitHub repository and pushing this folder:

1. In Cloudflare Pages, choose **Create a project** and connect the GitHub repository.
2. Choose no framework preset.
3. Use `bash scripts/cloudflare-build.sh` as the build command.
4. Use `_site` as the build output directory.
5. Leave the root directory at the repository root.

The build script downloads a pinned stable Quarto release inside Cloudflare’s temporary build environment, then renders the site. To change that version later, set a `QUARTO_VERSION` environment variable in the Cloudflare Pages project settings.

Cloudflare will create a preview for repository branches and update the public site whenever the production branch changes.

## Before the first public launch

Review these intentional placeholders:

- `_quarto.yml` — footer university and department line
- `contact.qmd` — affiliation and mailing-address section

Do not publish university, department, or mailing-address details until they are confirmed.
