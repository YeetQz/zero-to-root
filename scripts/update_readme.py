#!/usr/bin/env python3
"""🤖 Redraws the live sections of README.md from progress.yml, logs/ and writeups/.

Run locally with:  python scripts/update_readme.py
The GitHub Action runs it on every push and once a day.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
PROGRESS = ROOT / "progress.yml"
LOGS = ROOT / "logs"
WRITEUPS = ROOT / "writeups"

STATUS_ICON = {"done": "✅", "next": "🔥", "later": "🔒"}
LOG_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


# ---------- data ----------

def load_progress() -> dict:
    data = yaml.safe_load(PROGRESS.read_text(encoding="utf-8")) or {}
    for phase in data.get("phases", []):
        for skill in phase.get("skills", []) or []:
            status = str(skill.get("status", "later")).strip().lower()
            skill["status"] = status if status in STATUS_ICON else "later"
            skill["core"] = bool(skill.get("core", False))
    return data


def log_dates() -> list[dt.date]:
    dates = []
    if LOGS.is_dir():
        for f in LOGS.iterdir():
            m = LOG_NAME.match(f.name)
            if m:
                try:
                    dates.append(dt.date.fromisoformat(m.group(1)))
                except ValueError:
                    pass
    return sorted(dates)


def streak(dates: list[dt.date], today: dt.date) -> int:
    """Days in a row with a log, ending today or yesterday."""
    if not dates:
        return 0
    have = set(dates)
    day = today if today in have else today - dt.timedelta(days=1)
    count = 0
    while day in have:
        count += 1
        day -= dt.timedelta(days=1)
    return count


def count_boxes() -> int:
    if not WRITEUPS.is_dir():
        return 0
    return sum(
        1
        for f in WRITEUPS.rglob("*.md")
        if f.parent != WRITEUPS and not f.name.startswith("_") and f.name.lower() != "readme.md"
    )


def phase_state(phase: dict) -> str:
    skills = phase.get("skills") or []
    if skills and all(s["status"] == "done" for s in skills):
        return "done"
    if any(s["status"] in ("done", "next") for s in skills):
        return "active"
    return "locked"


# ---------- rendering helpers ----------

def bar(done: int, total: int, width: int) -> str:
    if total <= 0:
        return "░" * width
    filled = round(done / total * width)
    return "█" * filled + "░" * (width - filled)


def shield(label: str, message: str, color: str, logo: str | None = None) -> str:
    def esc(s: str) -> str:
        return quote(s.replace("-", "--").replace("_", "__"), safe="")

    url = f"https://img.shields.io/badge/{esc(label)}-{esc(message)}-{color}?style=for-the-badge"
    if logo:
        url += f"&logo={logo}&logoColor=white"
    return f'<img src="{url}" alt="{label}: {message}" />'


def mermaid_text(s: str) -> str:
    return s.replace('"', "'")


# ---------- sections ----------

def section_badges(data, stats) -> str:
    phases = data.get("phases", [])
    current = next((p for p in phases if phase_state(p) != "done"), None)
    phase_label = f"{current.get('emoji', '')} {current['name']}".strip() if current else "👑 All done"
    badges = [
        shield("Kali Linux", "2026.3", "367BF0", "kalilinux"),
        shield("Day", str(stats["day"]), "6E40C9"),
        shield("Skills", f"{stats['done']}/{stats['total']}", "2EA043"),
        shield("Phase", phase_label, "D29922"),
        shield("Boxes pwned", f"{stats['boxes']} 💀", "CF222E"),
        shield("Streak", f"{stats['streak']} day{'s' if stats['streak'] != 1 else ''} 🔥", "FB8500"),
        shield("Achievements", f"{stats['ach_done']}/{stats['ach_total']} 🏅", "8957E5"),
    ]
    return "\n".join(badges)


def section_progress(data, stats) -> str:
    pct = round(stats["done"] / stats["total"] * 100) if stats["total"] else 0
    core_pct = round(stats["core_done"] / stats["core_total"] * 100) if stats["core_total"] else 0
    lines = [
        "```text",
        f"Overall      {bar(stats['done'], stats['total'], 30)}  {pct:>3}%  ({stats['done']}/{stats['total']} skills)",
        f"Must-knows ⭐ {bar(stats['core_done'], stats['core_total'], 30)}  {core_pct:>3}%  ({stats['core_done']}/{stats['core_total']})",
        f"In progress  🔥 {stats['next']} skill{'s' if stats['next'] != 1 else ''}",
        "```",
        "",
        "| | Phase | Progress | | Status |",
        "|---|---|---|---|---|",
    ]
    label = {"done": "✅ Complete", "active": "🔥 In progress", "locked": "🔒 Locked"}
    for i, p in enumerate(data.get("phases", []), 1):
        skills = p.get("skills") or []
        d = sum(1 for s in skills if s["status"] == "done")
        lines.append(
            f"| {p.get('emoji', '')} | **{i}. {p['name']}** | `{bar(d, len(skills), 10)}` | {d}/{len(skills)} | {label[phase_state(p)]} |"
        )
    return "\n".join(lines)


def section_roadmap(data) -> str:
    phases = data.get("phases", [])
    out = ["```mermaid", "flowchart LR"]
    for p in phases:
        skills = p.get("skills") or []
        d = sum(1 for s in skills if s["status"] == "done")
        text = mermaid_text(f"{p.get('emoji', '')} {p['name']}<br/>{d}/{len(skills)}")
        out.append(f'    {p["id"]}["{text}"]:::{phase_state(p)}')
    for a, b in zip(phases, phases[1:]):
        out.append(f"    {a['id']} --> {b['id']}")
    out += [
        "    root((\"👑 root\")):::locked" if any(phase_state(p) != "done" for p in phases) else "    root((\"👑 root\")):::done",
    ]
    if phases:
        out.append(f"    {phases[-1]['id']} --> root")
    out += [
        "    classDef done fill:#2ea043,stroke:#1a7f37,color:#ffffff",
        "    classDef active fill:#d29922,stroke:#9a6700,color:#ffffff",
        "    classDef locked fill:#30363d,stroke:#6e7681,color:#c9d1d9",
        "```",
        "",
        "<sub>🟩 complete · 🟨 in progress · ⬛ locked</sub>",
        "",
        "<details>",
        "<summary><b>📋 Every skill</b> (✅ done · 🔥 working on it · 🔒 later · ⭐ must-know)</summary>",
        "",
    ]
    for i, p in enumerate(phases, 1):
        out.append(f"**{p.get('emoji', '')} {i}. {p['name']}**")
        out.append("")
        for s in p.get("skills") or []:
            star = " ⭐" if s["core"] else ""
            out.append(f"- {STATUS_ICON[s['status']]} {s['name']}{star}")
        out.append("")
    out.append("</details>")
    return "\n".join(out)


def achievements(data, stats) -> list[tuple[dict, bool]]:
    done_skills = {s["name"] for p in data.get("phases", []) for s in (p.get("skills") or []) if s["status"] == "done"}
    phase_done = {p["id"] for p in data.get("phases", []) if phase_state(p) == "done"}
    result = []
    for a in data.get("achievements", []) or []:
        if "skill" in a:
            ok = a["skill"] in done_skills
        elif "phase" in a:
            ok = a["phase"] in phase_done
        elif "boxes" in a:
            ok = stats["boxes"] >= int(a["boxes"])
        elif "streak" in a:
            ok = stats["best_streak"] >= int(a["streak"])
        elif "logs" in a:
            ok = stats["logs"] >= int(a["logs"])
        else:
            ok = False
        result.append((a, ok))
    return result


def section_achievements(achs) -> str:
    unlocked = [a for a, ok in achs if ok]
    locked = [a for a, ok in achs if not ok]
    lines = [f"**{len(unlocked)} of {len(achs)} unlocked**", "", "| | Achievement | |", "|---|---|---|"]
    for a in unlocked:
        lines.append(f"| {a.get('emoji', '🏅')} | **{a['name']}** | {a.get('desc', '')} |")
    for a in locked:
        lines.append(f"| 🔒 | {a['name']} | _{a.get('desc', '')}_ |")
    return "\n".join(lines)


def section_latest_log(dates) -> str:
    if not dates:
        return "_No logs yet. Copy `logs/_template.md` to `logs/YYYY-MM-DD.md` to start the diary._"
    latest = dates[-1]
    path = LOGS / f"{latest.isoformat()}.md"
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_match.group(1).strip() if title_match else latest.isoformat()
    learned = re.search(r"^##[^\n]*learned[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    body = learned.group(1).strip() if learned else ""
    body_lines = body.splitlines()[:10]
    lines = [f"### [{title}](logs/{path.name})", ""]
    if body_lines:
        lines += ["**🧠 What I learned:**", ""] + body_lines
    lines += ["", f"<sub>📚 {len(dates)} log entr{'y' if len(dates) == 1 else 'ies'} so far · [read them all](logs/)</sub>"]
    return "\n".join(lines)


def replace_section(readme: str, name: str, content: str) -> str:
    pattern = re.compile(rf"(<!--{name}:START-->)(.*?)(<!--{name}:END-->)", re.S)
    if not pattern.search(readme):
        print(f"⚠️  marker {name} not found in README.md", file=sys.stderr)
        return readme
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", readme)


def best_streak(dates: list[dt.date]) -> int:
    best = run = 0
    prev = None
    for d in dates:
        run = run + 1 if prev and (d - prev).days == 1 else 1
        best = max(best, run)
        prev = d
    return best


def main() -> None:
    data = load_progress()
    today = dt.datetime.now(dt.timezone.utc).date()
    skills = [s for p in data.get("phases", []) for s in (p.get("skills") or [])]
    dates = log_dates()
    started = data.get("started")
    if isinstance(started, str):
        started = dt.date.fromisoformat(started)
    day = (today - started).days + 1 if isinstance(started, dt.date) else len(dates)

    stats = {
        "total": len(skills),
        "done": sum(s["status"] == "done" for s in skills),
        "next": sum(s["status"] == "next" for s in skills),
        "core_total": sum(s["core"] for s in skills),
        "core_done": sum(s["core"] and s["status"] == "done" for s in skills),
        "boxes": count_boxes(),
        "logs": len(dates),
        "streak": streak(dates, today),
        "best_streak": best_streak(dates),
        "day": max(day, 1),
    }
    achs = achievements(data, stats)
    stats["ach_done"] = sum(ok for _, ok in achs)
    stats["ach_total"] = len(achs)

    readme = README.read_text(encoding="utf-8")
    readme = replace_section(readme, "BADGES", section_badges(data, stats))
    readme = replace_section(readme, "PROGRESS", section_progress(data, stats))
    readme = replace_section(readme, "ROADMAP", section_roadmap(data))
    readme = replace_section(readme, "ACHIEVEMENTS", section_achievements(achs))
    readme = replace_section(readme, "LATEST_LOG", section_latest_log(dates))
    README.write_text(readme, encoding="utf-8")

    print(f"✅ README updated: {stats['done']}/{stats['total']} skills, {stats['ach_done']} achievements, "
          f"{stats['boxes']} boxes, streak {stats['streak']}")


if __name__ == "__main__":
    main()
