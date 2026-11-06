#!/usr/bin/env python3
"""Validate every program file and build the README table and the website data.

    python scripts/build.py           # validate, then write README.md table and site/programs.json
    python scripts/build.py --check   # validate and fail if README.md is out of date (used in CI)
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
PROGRAMS = ROOT / "programs"
SCHEMA = json.loads((ROOT / "schema" / "program.schema.json").read_text(encoding="utf-8"))
DISCIPLINES = json.loads((ROOT / "schema" / "disciplines.json").read_text(encoding="utf-8"))
README = ROOT / "README.md"
SITE_DATA = ROOT / "site" / "programs.json"
START, END = "<!-- programs:start -->", "<!-- programs:end -->"


def _plain(value):
    """YAML reads dates as date objects; the schema expects strings."""
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def load_programs() -> tuple[list[dict], list[str]]:
    validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
    programs, errors = [], []
    for path in sorted(PROGRAMS.glob("*.yml")):
        name = path.relative_to(ROOT).as_posix()
        try:
            record = _plain(yaml.safe_load(path.read_text(encoding="utf-8")))
        except yaml.YAMLError as exc:
            errors.append(f"{name}: not valid YAML ({exc})")
            continue
        if not isinstance(record, dict):
            errors.append(f"{name}: expected a mapping of fields")
            continue
        for err in sorted(validator.iter_errors(record), key=lambda e: list(e.path)):
            where = ".".join(str(p) for p in err.path) or "(top level)"
            errors.append(f"{name}: {where}: {err.message}")
        if record.get("id") != path.stem:
            errors.append(f"{name}: id must match the file name ({path.stem!r})")
        for d in record.get("disciplines") or []:
            if d not in DISCIPLINES:
                errors.append(f"{name}: unknown discipline {d!r}; use one of {sorted(DISCIPLINES)} "
                              "or propose a new one in schema/disciplines.json")
        programs.append(record)
    seen: dict[tuple, str] = {}
    for r in programs:
        key = ((r.get("institution") or {}).get("name"), (r.get("home_department") or "").lower(),
               tuple(r.get("disciplines") or []))
        if key in seen:
            errors.append(f"programs/{r.get('id')}.yml duplicates programs/{seen[key]}.yml")
        seen[key] = r.get("id")
    return programs, errors


def _md(text: str) -> str:
    return text.replace("|", "\\|")


def readme_table(programs: list[dict]) -> str:
    rows = ["| Institution | Home department | Degrees | Discipline | DBER faculty |",
            "|---|---|---|---|---|"]
    for r in sorted(programs, key=lambda r: (r["institution"]["name"], r["id"])):
        inst = _md(r["institution"]["name"])
        if r.get("url"):
            inst = f"[{inst}]({r['url']})"
        inst += f"<br><sub>{_md(r['institution']['country'])}</sub>"
        dept = _md(r["home_department"]) + (" ⚠️" if "home_department" in r.get("needs_check", []) else "")
        degrees = ", ".join(r["degree_types"]) + (" ⚠️" if "degree_types" in r.get("needs_check", []) else "")
        disc = ", ".join(DISCIPLINES[d] for d in r["disciplines"])
        faculty = ", ".join(_md(f["name"]) for f in r["dber_faculty"])
        rows.append(f"| {inst} | {dept} | {degrees} | {disc} | {faculty} |")
    count = f"{len(programs)} program{'s' if len(programs) != 1 else ''}."
    note = " ⚠️ marks details still to be confirmed with the program." if any(
        r.get("needs_check") for r in programs) else ""
    return f"{START}\n_Generated from `programs/` by `scripts/build.py`; edit the program files, not this table. {count}{note}_\n\n" \
           + "\n".join(rows) + f"\n{END}"


def updated_readme(programs: list[dict]) -> str:
    text = README.read_text(encoding="utf-8")
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    return before + readme_table(programs) + after


def site_data(programs: list[dict]) -> dict:
    return {
        "generated": dt.date.today().isoformat(),
        "disciplines": DISCIPLINES,
        "programs": sorted(programs, key=lambda r: (r["institution"]["name"], r["id"])),
    }


def main() -> int:
    programs, errors = load_programs()
    if errors:
        print(f"{len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    new_readme = updated_readme(programs)
    if "--check" in sys.argv:
        if new_readme != README.read_text(encoding="utf-8"):
            print("README.md table is out of date: run python scripts/build.py and commit the result.")
            return 1
        print(f"OK: {len(programs)} programs valid; README.md is up to date.")
        return 0
    README.write_text(new_readme, encoding="utf-8")
    SITE_DATA.parent.mkdir(exist_ok=True)
    SITE_DATA.write_text(json.dumps(site_data(programs), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: {len(programs)} programs valid; wrote README.md table and {SITE_DATA.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
