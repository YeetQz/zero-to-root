#!/usr/bin/env python3
"""🤖 The README bot. Redraws every live section of README.md and assets/status.svg.

Run locally with:  python3 scripts/update_readme.py
The GitHub Action runs it on every push and once a day.

How it works: README.md contains marker pairs like <!--PROGRESS:START--> ... <!--PROGRESS:END-->.
Everything between a pair gets replaced with freshly generated markdown.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import status_svg  # noqa: E402
import system  # noqa: E402

README = system.ROOT / "README.md"


def shield(label: str, message: str, color: str, logo: str | None = None) -> str:
    """A shields.io badge. Dashes and underscores are doubled because shields uses them as separators."""
    def esc(s: str) -> str:
        return quote(s.replace("-", "--").replace("_", "__"), safe="")
    url = f"https://img.shields.io/badge/{esc(label)}-{esc(message)}-{color}?style=for-the-badge"
    if logo:
        url += f"&logo={logo}&logoColor=white"
    return f'<img src="{url}" alt="{label}: {message}" />'


def section_badges(h) -> str:
    return "\n".join([
        shield("Kali Linux", "2026.3", "367BF0", "kalilinux"),
        shield("Rank", f"{h.rank}-Rank {h.job}", "1F6BFF"),
        shield("Level", str(h.level), "6E40C9"),
        shield("XP", str(h.xp), "0EA5E9"),
        shield("Boxes pwned", f"{h.boxes} 💀", "CF222E"),
        shield("Streak", f"{h.streak} day{'s' if h.streak != 1 else ''} 🔥", "FB8500"),
        shield("Day", str(h.day), "475569"),
    ])


def section_hunter(h) -> str:
    unlocked = sum(ok for _, ok in h.achievements)
    bd = " · ".join(f"{k} {v}" for k, v in h.xp_breakdown.items() if v)
    return "\n".join([
        '<p align="center"><img src="assets/status.svg" alt="Animated hunter status window" width="100%" /></p>',
        "",
        f"> **[SYSTEM]** {h.name} is {'an' if h.rank in 'EAS' else 'a'} **{h.rank}-Rank {h.job}**. "
        f"{h.xp_per_level - h.xp_into_level} XP until level {h.level + 1}.  ",
        f"> XP sources: {bd} · {unlocked}/{len(h.achievements)} achievements",
    ])


def section_progress(h) -> str:
    pct = round(h.skills_done / h.skills_total * 100) if h.skills_total else 0
    core_pct = round(h.core_done / h.core_total * 100) if h.core_total else 0
    lines = [
        "```text",
        f"Overall      {system.bar(h.skills_done, h.skills_total, 30)}  {pct:>3}%  ({h.skills_done}/{h.skills_total} skills)",
        f"Must-knows ⭐ {system.bar(h.core_done, h.core_total, 30)}  {core_pct:>3}%  ({h.core_done}/{h.core_total})",
        f"In progress  🔥 {h.skills_next} skill{'s' if h.skills_next != 1 else ''}",
        "```",
        "",
        "| | Path | Progress | | Status |",
        "|---|---|---|---|---|",
    ]
    label = {"done": "✅ Complete", "active": "🔥 In progress", "locked": "🔒 Locked"}
    for i, p in enumerate(h.data.get("phases", []), 1):
        d = sum(s["status"] == "done" for s in p["skills"])
        n = len(p["skills"])
        lines.append(f"| {p.get('emoji', '')} | **{i}. {p['name']}** | `{system.bar(d, n, 10)}` | {d}/{n} | {label[system.phase_state(p)]} |")
    return "\n".join(lines)


def section_quests(h) -> str:
    quests = h.data.get("quests", []) or []
    lines = ["| | Quest | Rank | Reward | Trial |", "|---|---|---|---|---|"]
    for q in quests:
        icon = system.QUEST_ICON[q["status"]]
        title = f"**{q['title']}**" if q["status"] == "active" else (q["title"] if q["status"] == "done" else f"_{q['title']}_")
        trial = f"`./hunter quiz {q['quiz']}`" if q.get("quiz") else ""
        lines.append(f"| {icon} | {title} | {q.get('rank', 'E')} | +{q.get('reward', 0)} XP | {trial} |")
    active = [q for q in quests if q["status"] == "active"]
    for q in active:
        lines += ["", "<details>", f"<summary>⚔️ <b>{q['title']}</b> objectives</summary>", ""]
        lines += [f"- [ ] {o}" for o in q["objectives"]]
        lines += ["", "</details>"]
    return "\n".join(lines)


def section_roadmap(h) -> str:
    phases = h.data.get("phases", [])
    out = ["```mermaid", "flowchart TD"]
    for p in phases:
        d = sum(s["status"] == "done" for s in p["skills"])
        text = f"{p.get('emoji', '')} {p['name']}<br/>{d}/{len(p['skills'])}".replace('"', "'")
        out.append(f'    {p["id"]}["{text}"]:::{system.phase_state(p)}')
    ids = {p["id"] for p in phases}
    # a branching tree: lab → linux → (bash, track) → recon → web → (exploit, passwords) → free → practice → root
    edges = [("lab", "linux"), ("linux", "bash"), ("linux", "track"), ("bash", "recon"), ("track", "recon"),
             ("recon", "web"), ("web", "exploit"), ("web", "passwords"), ("exploit", "free"),
             ("passwords", "free"), ("free", "practice")]
    used = [(a, b) for a, b in edges if a in ids and b in ids]
    if not used:
        used = list(zip([p["id"] for p in phases], [p["id"] for p in phases][1:]))
    out += [f"    {a} --> {b}" for a, b in used]
    all_done = all(system.phase_state(p) == "done" for p in phases)
    out.append(f'    root(("👑 root")):::{"done" if all_done else "locked"}')
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
        out += [f"**{p.get('emoji', '')} {i}. {p['name']}**", ""]
        out += [f"- {system.SKILL_ICON[s['status']]} {s['name']}{' ⭐' if s['core'] else ''}" for s in p["skills"]]
        out.append("")
    out.append("</details>")
    return "\n".join(out)


def section_achievements(h) -> str:
    unlocked = [a for a, ok in h.achievements if ok]
    locked = [a for a, ok in h.achievements if not ok]
    lines = [f"**{len(unlocked)} of {len(h.achievements)} unlocked** · +{system.load().get('xp', {}).get('achievement', 50)} XP each",
             "", "| | Achievement | |", "|---|---|---|"]
    lines += [f"| {a.get('emoji', '🏅')} | **{a['name']}** | {a.get('desc', '')} |" for a in unlocked]
    lines += [f"| 🔒 | {a['name']} | _{a.get('desc', '')}_ |" for a in locked]
    return "\n".join(lines)


def section_latest_log() -> str:
    dates = system.log_dates()
    if not dates:
        return "_No logs yet. Copy `logs/_template.md` to `logs/YYYY-MM-DD.md` to start the diary._"
    path = system.LOGS / f"{dates[-1].isoformat()}.md"
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^#\s+(.+)$", text, re.M)
    title = m.group(1).strip() if m else dates[-1].isoformat()
    learned = re.search(r"^##[^\n]*learned[^\n]*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    body = (learned.group(1).strip().splitlines() if learned else [])[:10]
    lines = [f"### [{title}](logs/{path.name})", ""]
    if body:
        lines += ["**🧠 What I learned:**", ""] + body
    lines += ["", f"<sub>📚 {len(dates)} log entr{'y' if len(dates) == 1 else 'ies'} so far · [read them all](logs/)</sub>"]
    return "\n".join(lines)


def replace_section(readme: str, name: str, content: str) -> str:
    pattern = re.compile(rf"(<!--{name}:START-->)(.*?)(<!--{name}:END-->)", re.S)
    if not pattern.search(readme):
        print(f"⚠️  marker {name} not found in README.md", file=sys.stderr)
        return readme
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", readme)


def main() -> None:
    h = system.compute()
    status_svg.write(h)
    readme = README.read_text(encoding="utf-8")
    for name, content in [
        ("BADGES", section_badges(h)),
        ("HUNTER", section_hunter(h)),
        ("PROGRESS", section_progress(h)),
        ("QUESTS", section_quests(h)),
        ("ROADMAP", section_roadmap(h)),
        ("ACHIEVEMENTS", section_achievements(h)),
        ("LATEST_LOG", section_latest_log()),
    ]:
        readme = replace_section(readme, name, content)
    README.write_text(readme, encoding="utf-8")
    print(f"✅ README updated: level {h.level} {h.rank}-rank, {h.xp} XP, "
          f"{h.skills_done}/{h.skills_total} skills, {sum(ok for _, ok in h.achievements)} achievements")


if __name__ == "__main__":
    main()
