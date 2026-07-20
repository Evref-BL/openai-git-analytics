#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERIC_ROOT = PROJECT_ROOT / "vendor" / "openai-git-charts"
sys.path.insert(0, str(GENERIC_ROOT))

from openai_git_charts import openai_har  # noqa: E402
from openai_git_charts.daily_chart import make_report_html, parse_date  # noqa: E402
from openai_git_charts.git_history import RepoSpec, build_git_history_section  # noqa: E402


def find_hars(path: Path) -> list[Path]:
    path = path.expanduser().resolve()
    if path.is_file():
        return [path]
    return sorted(path.glob("*.har"), key=lambda item: (item.stat().st_mtime, str(item)))


def write_manifest(path: Path, hars: list[Path], extracted: openai_har.Extracted) -> None:
    manifest = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generic_project": str(GENERIC_ROOT),
        "inputs": [
            {
                "path": str(har),
                "size_bytes": har.stat().st_size,
                "mtime": datetime.fromtimestamp(har.stat().st_mtime, UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            }
            for har in hars
        ],
        "endpoints": {
            endpoint: {
                "rows": len(payload.get("data", [])),
                "group_by": payload.get("group_by"),
                "units": payload.get("units"),
            }
            for endpoint, payload in sorted(extracted.endpoints.items())
        },
        "merge_policy": "HAR files are ordered by mtime. For the same endpoint/date, the later row wins.",
    }
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def optional_git_section(config_path: Path):
    if not config_path.exists():
        return None
    config = json.loads(config_path.read_text(encoding="utf-8"))
    repos = [
        RepoSpec(Path(item["path"]).expanduser().resolve(), item["name"])
        for item in config.get("repositories", [])
        if item.get("path") and item.get("path") != "/absolute/path/to/git/repository"
    ]
    if not repos:
        return None
    start = parse_date(config["start"]) if config.get("start") else None
    end = parse_date(config["end"]) if config.get("end") else None
    return build_git_history_section(repos, start, end, bool(config.get("include_merges")))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a private OpenAI/Git analytics report.")
    parser.add_argument("--har-dir", type=Path, default=PROJECT_ROOT / "data" / "raw" / "har")
    parser.add_argument("--git-config", type=Path, default=PROJECT_ROOT / "config" / "git_repos.json")
    parser.add_argument("--start", type=parse_date)
    parser.add_argument("--end", type=parse_date)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--processed-dir", type=Path, default=PROJECT_ROOT / "data" / "processed")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "reports" / "personal-analytics.html")
    args = parser.parse_args()

    hars = find_hars(args.har_dir)
    if not hars:
        raise SystemExit("no HAR files found in data/raw/har")
    extracted = openai_har.merge_extracted([openai_har.extract_har(path) for path in hars])
    if not extracted.endpoints:
        raise SystemExit("no OpenAI analytics responses found in HAR files")

    processed_dir = args.processed_dir.expanduser().resolve()
    report = args.report.expanduser().resolve()
    processed_dir.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    openai_har.write_normalized_files(extracted, processed_dir)
    write_manifest(processed_dir / "manifest.json", hars, extracted)

    sections = openai_har.build_sections(extracted, args.start, args.end, args.top)
    git_section = optional_git_section(args.git_config.expanduser().resolve())
    if git_section:
        sections.append(git_section)

    report.write_text(
        make_report_html("OpenAI and Git analytics", sections, "Built from local HAR captures and optional local Git repositories."),
        encoding="utf-8",
    )
    print(f"merged {len(hars)} HAR file(s)")
    print(f"wrote processed data: {processed_dir}")
    print(f"wrote report: {report}")


if __name__ == "__main__":
    main()
