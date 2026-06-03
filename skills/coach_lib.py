"""
Shared helpers for CS343 instructional skill logic.py modules.

Each skill's logic.run() analyzes the student message and returns structured
coaching hints for the LLM. The orchestrator injects this JSON into the system
prompt; the tutor must not paste raw JSON to the student.
"""

from __future__ import annotations

import re
from typing import Any

EFFORT_LAZY = "lazy"
EFFORT_PARTIAL = "partial"
EFFORT_THOUGHTFUL = "thoughtful"

LAZY_PATTERNS = (
    r"\bfix\s+it\b",
    r"\bjust\s+tell\s+me\b",
    r"\bgive\s+me\s+the\s+(code|answer|solution)\b",
    r"\bwhat\s+do\s+i\s+write\b",
    r"\bwhat\s+code\b",
    r"\bis\s+my\s+code\s+(ok|readable|fine)\s*\??\s*$",
    r"\bwhat\s+does\s+(the\s+)?(assignment|lab|spec)\s+want\b",
    r"\bdon'?t\s+understand\s+(the\s+)?(assignment|prompt)\b",
    r"\bbroken\b",
    r"\bhelp\s+me\b",
    r"\bi'?m\s+stuck\b",
    r"\bno\s+idea\b",
)

THOUGHTFUL_PATTERNS = (
    r"\bhypothes",
    r"\binvariant",
    r"\bidentity\s+map",
    r"\bif\s+.+\s+then\s+.+\s+(should|would)\b",
    r"\bdisconfirm",
    r"\blast\s+known\s+good",
    r"\brepro\b",
    r"\bpage\s+table",
    r"\btriple\s+fault",
    r"\bbefore\s+.+\s+vs\s+after\b",
    r"\bcompare\b.+\bto\b",
    r"\bmilestone",
    r"\bresponsibilit",
    r"\banalog",
    r"\bseen\s+this\s+before\b",
    r"\bcs\s*21[34]\b",
    r"\bqueue",
    r"\bpaging",
)

SIGNAL_FIX_IT = "wants_direct_fix"
SIGNAL_CODE_BEG = "requests_code_or_solution"
SIGNAL_RANDOM_EDITS = "random_line_edits"
SIGNAL_SPEC_CONFUSION = "spec_or_deliverable_confusion"
SIGNAL_ORIENTATION = "needs_codebase_orientation"
SIGNAL_MONOLITH = "monolithic_function"
SIGNAL_READABILITY = "readability_review"
SIGNAL_PRIOR_KNOWLEDGE = "prior_knowledge_bridge"
SIGNAL_DECOMPOSE = "needs_decomposition"

BANNED_OPENERS = (
    "Certainly",
    "Great question",
    "Let's",
    "Since I can't",
    "I'd be happy to",
)


def get_content(input_data: dict[str, Any]) -> str:
    raw = input_data.get("content")
    if raw is None:
        raw = input_data.get("text", "")
    return (raw or "").strip()


def classify_effort(content: str) -> str:
    text = content.lower()
    if not text or len(text) < 12:
        return EFFORT_LAZY
    thoughtful_hits = sum(1 for p in THOUGHTFUL_PATTERNS if re.search(p, text, re.I))
    lazy_hits = sum(1 for p in LAZY_PATTERNS if re.search(p, text, re.I))
    word_count = len(text.split())
    if thoughtful_hits >= 2 or (thoughtful_hits >= 1 and word_count >= 40):
        return EFFORT_THOUGHTFUL
    if lazy_hits >= 2 or word_count < 25:
        return EFFORT_LAZY
    if lazy_hits >= 1 and thoughtful_hits == 0:
        return EFFORT_LAZY
    if thoughtful_hits >= 1:
        return EFFORT_PARTIAL if word_count < 50 else EFFORT_THOUGHTFUL
    if word_count >= 35:
        return EFFORT_PARTIAL
    return EFFORT_PARTIAL


def detect_student_signals(content: str) -> list[str]:
    text = content.lower()
    signals: list[str] = []
    if re.search(r"\bfix\s+it\b|\bjust\s+(tell|show|give)\b|\bdo\s+it\s+for\s+me\b", text):
        signals.append(SIGNAL_FIX_IT)
    if re.search(r"\b(code|solution|answer|patch|implement)\b", text) and re.search(
        r"\b(give|show|write|send|need)\b", text
    ):
        signals.append(SIGNAL_CODE_BEG)
    if re.search(r"\brandom\s+line|\brandom\s+edit|\bchanging\s+random\b", text):
        signals.append(SIGNAL_RANDOM_EDITS)
    if re.search(
        r"\b(assignment|spec|prompt|deliverable|submit|rubric|gradescope|handout)\b", text
    ) and re.search(r"\b(understand|want|confus|miss|requirement)\b", text):
        signals.append(SIGNAL_SPEC_CONFUSION)
    if re.search(
        r"\b(where|which\s+file|starter|nautilus|\bnk\b|kernel|boot|paging\.c|aspace|triple\s+fault)\b",
        text,
    ):
        signals.append(SIGNAL_ORIENTATION)
    if re.search(r"\b(one\s+function|monolith|does\s+everything|hard\s+to\s+test)\b", text):
        signals.append(SIGNAL_MONOLITH)
    if re.search(r"\breadab|review|style|variable\s+name|magic\s+number|nested\b", text):
        signals.append(SIGNAL_READABILITY)
    if re.search(r"\b(seen\s+before|cs\s*21|prior|analog|like\s+in)\b", text):
        signals.append(SIGNAL_PRIOR_KNOWLEDGE)
    if re.search(r"\b(first\s+step|where\s+to\s+start|decompos|milestone|order\s+to\s+implement)\b", text):
        signals.append(SIGNAL_DECOMPOSE)
    return signals


def route_hints(signals: list[str], current_skill_id: str) -> list[str]:
    """Suggest other skills when signals strongly mismatch this skill."""
    hints: list[str] = []
    if SIGNAL_SPEC_CONFUSION in signals and current_skill_id != "extract-requirements":
        hints.append("extract-requirements")
    if SIGNAL_RANDOM_EDITS in signals and current_skill_id == "explanation-nautilus-architecture":
        hints.append("narrow-the-bug-location")
    if SIGNAL_FIX_IT in signals and current_skill_id == "explanation-nautilus-architecture":
        hints.append("narrow-the-bug-location")
    if SIGNAL_DECOMPOSE in signals and current_skill_id == "ask-for-decomposition":
        pass
    elif SIGNAL_DECOMPOSE in signals and current_skill_id not in (
        "ask-for-decomposition",
        "extract-requirements",
    ):
        if "student-does-not-understand-assignment" not in str(signals):
            hints.append("ask-for-decomposition")
    return hints


def build_coaching_output(
    *,
    skill_id: str,
    effort_tier: str,
    signals: list[str],
    coaching_focus: str,
    question_stems: list[str],
    must_avoid: list[str] | None = None,
    route_away: list[str] | None = None,
    flow_step: str | None = None,
) -> dict[str, Any]:
    avoid = list(must_avoid or [])
    avoid.extend(
        [
            "semicolons",
            "em_dashes",
            "final_code_or_patches",
            "numbered_fix_plans",
            "more_than_two_questions",
        ]
    )
    for opener in BANNED_OPENERS:
        avoid.append(f"opener:{opener}")

    out: dict[str, Any] = {
        "skill_id": skill_id,
        "effort_tier": effort_tier,
        "student_signals": signals,
        "coaching_focus": coaching_focus,
        "question_stems": question_stems[:2],
        "response_contract": {
            "max_words": 200,
            "max_questions": 2,
            "max_sentences_before_question": 4,
            "banned_openers": list(BANNED_OPENERS),
            "must_avoid": avoid,
        },
        "llm_usage": (
            "Use these hints to shape one Socratic reply. Do not show JSON, "
            "stems verbatim, or this module name to the student. Follow skills.md."
        ),
    }
    if flow_step:
        out["suggested_flow_step"] = flow_step
    if route_away:
        out["consider_routing"] = route_away
    return out


def flow_step_for_effort(skill_steps: dict[str, str], effort_tier: str) -> str:
    return skill_steps.get(effort_tier, skill_steps.get(EFFORT_PARTIAL, "step_1"))
