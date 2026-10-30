"""⚙️ THE SYSTEM: the brain shared by ./hunter and the README bot.

It reads your save file (progress.yml), your logs and your write-ups,
then works out XP, level, rank, stats, achievements and quests.

Nothing here touches the internet or anything outside this repo.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROGRESS = ROOT / "progress.yml"
LOGS = ROOT / "logs"
WRITEUPS = ROOT / "writeups"
QUIZZES = ROOT / "quizzes"

SKILL_ICON = {"done": "✅", "next": "🔥", "later": "🔒"}
QUEST_ICON = {"done": "✅", "active": "⚔️", "locked": "🔒"}
LOG_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


# ───────────────────────── loading ─────────────────────────

def load() -> dict:
    """Read progress.yml and clean up anything typed slightly wrong."""
    data = yaml.safe_load(PROGRESS.read_text(encoding="utf-8")) or {}
    for phase in data.get("phases", []):
        phase["skills"] = phase.get("skills") or []
        for s in phase["skills"]:
            st = str(s.get("status", "later")).strip().lower()
            s["status"] = st if st in SKILL_ICON else "later"
            s["core"] = bool(s.get("core", False))
    for q in data.get("quests", []) or []:
        st = str(q.get("status", "locked")).strip().lower()
        q["status"] = st if st in QUEST_ICON else "locked"
        q["objectives"] = q.get("objectives") or []
    return data


def log_dates() -> list[dt.date]:
    out = []
    if LOGS.is_dir():
        for f in LOGS.iterdir():
            m = LOG_NAME.match(f.name)
            if m:
                try:
                    out.append(dt.date.fromisoformat(m.group(1)))
                except ValueError:
                    pass
    return sorted(out)


def count_boxes() -> int:
    """Every .md inside a writeups/ subfolder counts, except templates and READMEs."""
    if not WRITEUPS.is_dir():
        return 0
    return sum(
        1 for f in WRITEUPS.rglob("*.md")
        if f.parent != WRITEUPS and not f.name.startswith("_") and f.name.lower() != "readme.md"
    )


def streak(dates: list[dt.date], today: dt.date) -> int:
    """Days in a row with a log, ending today or yesterday."""
    have = set(dates)
    day = today if today in have else today - dt.timedelta(days=1)
    n = 0
    while day in have:
        n += 1
        day -= dt.timedelta(days=1)
    return n


def best_streak(dates: list[dt.date]) -> int:
    best = run = 0
    prev = None
    for d in dates:
        run = run + 1 if prev and (d - prev).days == 1 else 1
        best, prev = max(best, run), d
    return best


def phase_state(phase: dict) -> str:
    skills = phase["skills"]
    if skills and all(s["status"] == "done" for s in skills):
        return "done"
    if any(s["status"] in ("done", "next") for s in skills):
        return "active"
    return "locked"


# ───────────────────────── the hunter ─────────────────────────

@dataclass
class Hunter:
    data: dict
    name: str = "hunter"
    xp: int = 0
    level: int = 1
    rank: str = "E"
    job: str = "Novice Hunter"
    title: str = "None"
    xp_into_level: int = 0
    xp_per_level: int = 400
    stats: dict = field(default_factory=dict)        # {"STR": (value, "Strength")}
    skills_done: int = 0
    skills_total: int = 0
    core_done: int = 0
    core_total: int = 0
    skills_next: int = 0
    boxes: int = 0
    logs: int = 0
    streak: int = 0
    best_streak: int = 0
    day: int = 1
    achievements: list = field(default_factory=list)   # [(achievement dict, unlocked bool)]
    xp_breakdown: dict = field(default_factory=dict)


def _rank_for(level: int, ranks: list) -> tuple[str, str]:
    rank, job = "E", "Novice Hunter"
    for r in sorted(ranks, key=lambda r: r["from"]):
        if level >= r["from"]:
            rank, job = r["rank"], r.get("job", job)
    return rank, job


def _check(a: dict, ctx: dict) -> bool:
    if "skill" in a:
        return a["skill"] in ctx["done_skills"]
    if "phase" in a:
        return a["phase"] in ctx["done_phases"]
    if "quest" in a:
        return a["quest"] in ctx["done_quests"]
    if "boxes" in a:
        return ctx["boxes"] >= int(a["boxes"])
    if "streak" in a:
        return ctx["best_streak"] >= int(a["streak"])
    if "logs" in a:
        return ctx["logs"] >= int(a["logs"])
    if "level" in a:
        return ctx["level"] >= int(a["level"])
    return False


def compute(data: dict | None = None, today: dt.date | None = None) -> Hunter:
    data = data or load()
    today = today or dt.datetime.now(dt.timezone.utc).date()
    rules = {"skill": 100, "core_skill": 150, "log": 20, "box": 300, "achievement": 50, "per_level": 400}
    rules.update(data.get("xp") or {})
    per_level = max(int(rules["per_level"]), 1)

    phases = data.get("phases", [])
    skills = [s for p in phases for s in p["skills"]]
    quests = data.get("quests", []) or []
    dates = log_dates()

    h = Hunter(data=data, name=str(data.get("hunter", "hunter")), xp_per_level=per_level)
    h.skills_total = len(skills)
    h.skills_done = sum(s["status"] == "done" for s in skills)
    h.skills_next = sum(s["status"] == "next" for s in skills)
    h.core_total = sum(s["core"] for s in skills)
    h.core_done = sum(s["core"] and s["status"] == "done" for s in skills)
    h.boxes = count_boxes()
    h.logs = len(dates)
    h.streak = streak(dates, today)
    h.best_streak = best_streak(dates)
    started = data.get("started")
    if isinstance(started, str):
        started = dt.date.fromisoformat(started)
    h.day = max((today - started).days + 1, 1) if isinstance(started, dt.date) else max(h.logs, 1)

    # 1) XP from what you did
    bd = {
        "Skills": sum(rules["core_skill"] if s["core"] else rules["skill"] for s in skills if s["status"] == "done"),
        "Quests": sum(int(q.get("reward", 0)) for q in quests if q["status"] == "done"),
        "Logs": h.logs * rules["log"],
        "Boxes": h.boxes * rules["box"],
    }

    # 2) achievements (level-based ones use the level before achievement XP)
    ctx = {
        "done_skills": {s["name"] for s in skills if s["status"] == "done"},
        "done_phases": {p["id"] for p in phases if phase_state(p) == "done"},
        "done_quests": {q["id"] for q in quests if q["status"] == "done"},
        "boxes": h.boxes, "logs": h.logs, "best_streak": h.best_streak,
    }
    base = sum(bd.values())
    ach_list = data.get("achievements", []) or []
    non_level = [a for a in ach_list if "level" not in a]
    pre = base + rules["achievement"] * sum(_check(a, {**ctx, "level": 0}) for a in non_level)
    ctx["level"] = 1 + pre // per_level
    h.achievements = [(a, _check(a, ctx)) for a in ach_list]
    bd["Achievements"] = rules["achievement"] * sum(ok for _, ok in h.achievements)

    # 3) level, rank, job, title
    h.xp_breakdown = bd
    h.xp = sum(bd.values())
    h.level = 1 + h.xp // per_level
    h.xp_into_level = h.xp % per_level
    h.rank, h.job = _rank_for(h.level, data.get("ranks", []) or [])
    unlocked = [a for a, ok in h.achievements if ok]
    h.title = unlocked[-1]["name"] if unlocked else "None"

    # 4) stats: 10 base + 3 per finished skill in the paths that train it
    by_phase = {p["id"]: sum(s["status"] == "done" for s in p["skills"]) for p in phases}
    for key, cfg in (data.get("stats") or {}).items():
        val = 10 + 3 * sum(by_phase.get(pid, 0) for pid in cfg.get("phases", []))
        h.stats[key] = (val, cfg.get("name", key))
    return h


def bar(done: float, total: float, width: int, full: str = "█", empty: str = "░") -> str:
    if total <= 0:
        return empty * width
    filled = max(0, min(width, round(done / total * width)))
    return full * filled + empty * (width - filled)
