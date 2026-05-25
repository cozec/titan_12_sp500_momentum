"""Export the local dashboard as static Cloudflare Pages assets."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from run_webapp import build_dashboard_payload  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export dashboard static assets.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "public",
        help="Directory to write static site assets into.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    static_dir = PROJECT_ROOT / "webapp" / "static"
    chart_dir = PROJECT_ROOT / "outputs" / "charts"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(static_dir, output_dir)

    if chart_dir.exists():
        shutil.copytree(chart_dir, output_dir / "charts")

    payload = build_dashboard_payload()
    dashboard_json = json.dumps(payload, indent=2, sort_keys=True)
    (output_dir / "dashboard.json").write_text(dashboard_json + "\n", encoding="utf-8")
    print(f"Wrote static dashboard to {output_dir}")


if __name__ == "__main__":
    main()
