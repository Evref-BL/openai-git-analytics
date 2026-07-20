# Manual OpenAI/Codex Analytics Capture

Use this process while you do not have access to the official Analytics API.

## Firefox HAR Capture

1. Open `https://chatgpt.com/codex/cloud/settings/analytics`.
2. Open Developer Tools with `Cmd+Opt+I`.
3. Go to the Network tab.
4. Enable persistent logging if Firefox shows a `Persist Logs` option.
5. Clear the network log.
6. Reload the analytics page.
7. Set the desired date range.
8. Visit every dashboard tab or section you want to preserve.
9. Right-click the Network request list.
10. Choose `Save All As HAR`.
11. Save the file into `data/raw/har/`.

Recommended filename pattern:

```text
chatgpt-codex-analytics_YYYY-MM-DD_HHMM.har
```

## Rebuild

```bash
python3 scripts/build_report.py --start 2026-04-23
```

## Quality Check

After rebuilding, inspect:

```text
data/processed/manifest.json
```

Confirm:

- the new HAR is listed under `inputs`
- expected endpoints are present
- row counts did not unexpectedly shrink

