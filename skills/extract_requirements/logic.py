"""extract-requirements — analyze student message for spec-reading coaching."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SKILLS_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

import coach_lib

SKILL_ID = "extract-requirements"

_FLOW = {
    coach_lib.EFFORT_LAZY: "step_1_identify_source",
    coach_lib.EFFORT_PARTIAL: "step_2_active_reading",
    coach_lib.EFFORT_THOUGHTFUL: "step_3_constraints_vs_plan",
}


def run(input: dict[str, Any]) -> dict[str, Any]:
    content = coach_lib.get_content(input)
    tier = coach_lib.classify_effort(content)
    signals = coach_lib.detect_student_signals(content)
    focus = _focus(tier, signals)
    stems = _stems(tier)
    return coach_lib.build_coaching_output(
        skill_id=SKILL_ID,
        effort_tier=tier,
        signals=signals,
        coaching_focus=focus,
        question_stems=stems,
        must_avoid=[
            "quoting_spec_or_listing_requirements",
            "choosing_implementation_for_them",
        ],
        route_away=coach_lib.route_hints(signals, SKILL_ID),
        flow_step=coach_lib.flow_step_for_effort(_FLOW, tier),
    )


def _focus(tier: str, signals: list[str]) -> str:
    if coach_lib.SIGNAL_CODE_BEG in signals:
        return "They want code. Redirect to deliverable and constraints in their own words."
    if tier == coach_lib.EFFORT_LAZY:
        return "Ask which spec section is open and one sentence they think is the deliverable."
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return "Ask which ignored constraint would break their current plan."
    return "Ask them to compare two spec phrases for mandatory vs optional."


def _stems(tier: str) -> list[str]:
    if tier == coach_lib.EFFORT_LAZY:
        return [
            "Which section of the handout or rubric do you have open right now?",
            "In one sentence, what do you think you must submit, even if unsure?",
        ]
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return [
            "Which requirement would break your plan if you ignored it?",
            "What is still unknown after reading the spec once?",
        ]
    return [
        "Which two phrases in the spec sound mandatory vs optional to you?",
        "What output or file name does the rubric treat as the deliverable?",
    ]
