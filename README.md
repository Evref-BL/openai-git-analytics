# OpenAI/Git Analytics Project Template

Template for a private analytics archive built on top of the generic `openai-git-charts` project.

This repository is intended to be copied for each person's private data. It should keep:

- browser HAR captures from OpenAI/Codex analytics
- generated normalized CSV/JSON data
- generated HTML reports
- optional local Git repository configuration

The reusable code lives in:

```text
vendor/openai-git-charts
```

That folder is expected to be a Git submodule in real use.

## Setup

If this project was cloned without submodules:

```bash
git submodule update --init --recursive
```

Copy the example Git config if you want Git history charts:

```bash
cp config/git_repos.example.json config/git_repos.json
```

Then edit `config/git_repos.json`.

## Capture OpenAI Analytics

Save Firefox/Chrome HAR files into:

```text
data/raw/har/
```

See [docs/manual-capture.md](docs/manual-capture.md).

## Build Report

```bash
python3 scripts/build_report.py --start 2026-04-23
```

Open:

```text
reports/personal-analytics.html
```

## Merge Policy

HAR files are sorted by modification time. For the same endpoint and date, the newest row wins.

Overlapping captures are safe and recommended.

