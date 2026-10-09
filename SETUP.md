# Setup (5 minutes)

## 1. Create the profile repository
GitHub shows a README on your profile only if the repo name **equals your username**.
Create a **public** repo named `ShivamSunny26` (so: `github.com/ShivamSunny26/ShivamSunny26`).

## 2. Upload this folder
Upload everything in this folder (keep the structure, including the hidden `.github` folder) to the `main` branch.

```bash
cd ShivamSunny26
git init -b main
git add .
git commit -m "Add auto-updating profile dashboard"
git remote add origin https://github.com/ShivamSunny26/ShivamSunny26.git
git push -u origin main
```

## 3. Allow the workflow to push
Repo → **Settings → Actions → General → Workflow permissions → Read and write permissions → Save**.

## 4. Run it once
Repo → **Actions → "Update profile dashboard" → Run workflow**.
After ~30 seconds `data/stats.json` and `assets/dashboard.svg` are replaced with your real numbers.
(The numbers shipped in this zip are SAMPLE values only.)
From then on it refreshes every 6 hours, and again whenever you edit `config.json` or `scripts/`.

## 5. (Optional) Count private activity
The built-in token only sees public data. To include private repos/commits:
1. Create a **personal access token (classic)** with scopes `read:user` and `repo`.
2. Repo → Settings → Secrets and variables → Actions → New secret → name `PROFILE_TOKEN`.
3. Set `"include_private": true` in `config.json`.
4. On your GitHub profile, tick **"Include private contributions on my profile"** (profile → Contribution settings).

## What each number means
| Card | Source |
|---|---|
| Commits (3 months) | commits made in the last 90 days (default branches) |
| Total Issues | issues you have opened, all time |
| Contributions (1 yr) | the same total shown on your profile's contribution graph, last 12 months |
| Current / longest streak | computed from the 12-month contribution calendar |
| Most Used Languages | bytes of code across your own, non-fork repositories |

## Customising
Everything visible (name, about text, tech stack, projects, links, email) lives in `config.json`.
Edit it, commit, and the workflow redraws the image.
To test locally: `GH_TOKEN=<token> python scripts/fetch_stats.py && python scripts/render_dashboard.py`.

Notes: GitHub may pause scheduled workflows after 60 days of no repo activity — the bot's stat commits normally keep it alive, but you can always press "Run workflow".
