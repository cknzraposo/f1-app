# Publish this tutorial with GitHub Pages

This guide is for the repository owner or an instructor publishing a fork.
You need permission to push the site files and configure repository Pages
settings. Nothing in a local build automatically makes the site live.

## What gets published

The site uses [MkDocs](https://www.mkdocs.org/) to render the existing tutorial
Markdown into a static landing page and navigable lessons. There is no separate
copy of each guide to maintain.

- Source: [tutorial landing page](./index.md) and the existing lesson Markdown.
- Configuration: [mkdocs.yml](../../mkdocs.yml).
- Styling: [tutorial.css](./assets/tutorial.css).
- Layout: [custom motorsport theme](../../theme/main.html), with responsive
  course navigation, light/dark mode, local search, and copyable code examples.
- Deployment: [Pages workflow](../../.github/workflows/pages.yml).
- Optional build dependencies: [requirements-pages.txt](../../requirements-pages.txt).

Only the generated `site/` directory is uploaded. Application code, data,
configuration, and executable acceptance checks are not copied into the site.
Links to source files and older documents open those resources on GitHub.
Those links do not make a private repository readable to the public.

**GitHub Pages does not run Python servers.** Students read the tutorial online,
clone the repository, and run FastAPI locally. Hosting a live F1 API would be a
separate deployment with separate operational and security requirements.

## 1. Preview locally

From the repository root, activate a Python environment, then run:

```bash
python -m pip install -r requirements-pages.txt
python -m unittest discover -s tests_pages -v
python -m mkdocs build --strict
python -m mkdocs serve --dev-addr 127.0.0.1:8001
```

Open the address printed by MkDocs. With the supplied project URL, it includes
`/f1-app/`: normally `http://127.0.0.1:8001/f1-app/`.
Port 8001 avoids the F1 API's usual port 8000. Stop the preview with Ctrl+C.
The publishing dependencies are not needed to run the application.

Check the landing page on desktop and a narrow/mobile viewport. Follow setup,
both paths, both labs, and assessment. Try search, lesson navigation, a code
link, and an in-page heading link.

## 2. Check repository-specific settings

For `cknzraposo/f1-app`, the expected default address is:

**https://cknzraposo.github.io/f1-app/**

This is the expected address, not a claim that deployment has already happened.

When publishing a fork or a renamed repository:

1. Change `site_url` and `repo_url` in [mkdocs.yml](../../mkdocs.yml).
2. Change its `edit_uri` if your default branch is not `master`.
3. Change the workflow's two branch filters and deployment condition from
   `master` to your publishing branch. They must agree.
4. Keep a project repository's path in `site_url`, for example
   `https://YOUR-ACCOUNT.github.io/YOUR-REPOSITORY/`.

Actions supplies the current repository and commit to the source-link hook.
Local builds use the configured repository and `master` by default. To inspect
another ref locally, set `PAGES_SOURCE_REF` explicitly. On Actions, source links
point to the built commit, not a potentially newer branch state.

## 3. Push the changes

Review `git status` and your diff. Commit the intended tutorial/site files, then
push to `master`, or merge them through your normal PR process.
Do not add `.env`, private configuration, credentials, virtual environments, or
generated `site/` output. The generated directory is already ignored.

The workflow builds and tests site changes on pull requests but deploys only
from `master` or a manual run targeting `master`. A PR build does not publish a
preview website.

## 4. Enable Pages in GitHub

1. Open the repository on GitHub.
2. Select **Settings > Pages**.
3. Under **Build and deployment**, choose **Source: GitHub Actions**.
4. If GitHub shows starter workflow suggestions, do not add another workflow:
   this repository already provides one.
5. If your organization restricts Actions or Pages, have an administrator allow
   the required actions and publication first.

Use **GitHub Actions**, not "Deploy from a branch": this site needs the Markdown
build and link processing before publication.

If the first push ran before Pages was enabled and deployment failed, enable
Pages, then run the workflow again in the next step.

## 5. Run and inspect the deployment

1. Open **Actions**.
2. Select **Publish tutorial to GitHub Pages**.
3. Choose **Run workflow**, select `master`, and run it.
4. Wait for the **build** and **deploy** jobs to finish.
5. Open the URL shown in the deploy job's `github-pages` environment, or return
   to **Settings > Pages** for the published address.

The build installs only documentation dependencies, runs site checks, and
performs a strict build. The deploy job alone gets Pages publishing permissions.
If environment protection requires approval, an authorized reviewer must
approve the deployment.

## 6. Verify the public student experience

- Open the site in a signed-out/private browser session.
- Follow **Start with setup**, both path cards, both lab links, and assessment.
- Refresh a lesson URL directly, not just the landing page.
- Test search and keyboard navigation on desktop and mobile.
- Follow source links: they should open GitHub, not broken paths beneath
  `github.io/f1-app/`.
- Confirm that the site does not imply the FastAPI app is hosted on Pages.
- Complete the [instructor pilot](./assessment.md#instructor-pilot-checklist)
  before describing the course as classroom-tested.

For a private repository, confirm Pages availability under your account/plan
and your organization's policy. Do not assume a private repository means a
private Pages website. Review the rendered content before publishing it.

## 7. Maintain the site

Edit the existing tutorial Markdown, not generated HTML. Layout changes belong
in `theme/`; visual assets and browser interactions live in `assets/` beside
the guides. The racing artwork is original SVG, not an official F1/team asset.
No frontend bundler or external font service is needed. After a successful
merge to `master`, relevant changes trigger a fresh build and deployment.
Keep the tested capabilities, dates, and instructor observations up to date.

To roll back content, revert the relevant source change through normal review
and let Actions redeploy it. Do not edit the deployed artifact manually.
Custom domains are optional; first verify the default `github.io` address.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| No workflow run | Was it pushed to the publishing branch, did a watched path change, and are Actions enabled? Try manual dispatch |
| Strict build fails | Read the first missing-link/configuration error; fix the source instead of disabling strict mode |
| Deploy fails | Pages source must be GitHub Actions; check environment approvals, permissions, and organization policy |
| Public URL returns 404 | Check deployment success, repository name/path, Pages settings, and allow time for publication |
| Styles or lesson URLs fail on a fork | Recheck `site_url`, branch settings, and project-path behavior; use the build tests |
| A source link is inaccessible | The linked repository or file may require authentication; Pages does not bypass repository access |
| You expect `/api/...` to work on Pages | Run FastAPI locally; a static Pages site cannot execute it |

Official references:

- [Create a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [Configure the publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/)
