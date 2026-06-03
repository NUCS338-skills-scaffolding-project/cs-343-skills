"""explain-function-responsibilities — modularity coaching without splitting for them."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SKILLS_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

import coach_lib

SKILL_ID = "explain-function-responsibilities"

_FLOW = {
    coach_lib.EFFORT_LAZY: "step_1_surface_responsibilities",
    coach_lib.EFFORT_PARTIAL: "step_2_name_tension",
    coach_lib.EFFORT_THOUGHTFUL: "step_3_invariant_if_merged",
}


def run(input: dict[str, Any]) -> dict[str, Any]:
    content = coach_lib.get_content(input)
    tier = coach_lib.classify_effort(content)
    signals = coach_lib.detect_student_signals(content)
    return coach_lib.build_coaching_output(
        skill_id=SKILL_ID,
        effort_tier=tier,
        signals=signals,
        coaching_focus=_focus(tier),
        question_stems=_stems(tier),
        must_avoid=[
            "new_function_names",
            "refactor_sketch",
            "splitting_code_for_them",
        ],
        route_away=coach_lib.route_hints(signals, SKILL_ID),
        flow_step=coach_lib.flow_step_for_effort(_FLOW, tier),
    )


def _focus(tier: str) -> str:
    if tier == coach_lib.EFFORT_LAZY:
        return "Ask one sentence on what the function must guarantee to its caller."
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return "Ask which invariant breaks if two responsibilities stay merged."
    return "Ask them to compare two chunks and name which responsibility does not belong."


def _stems(tier: str) -> list[str]:
    if tier == coach_lib.EFFORT_LAZY:
        return [
            "In one sentence, what must this function guarantee to its caller?",
            "What is one thing this function should never do as a side effect?",
        ]
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return [
            "If two responsibilities stay in one function, which invariant becomes hard to test?",
            "What would break for a caller if I/O and core logic stay mixed?",
        ]
    return [
        "Pick two sections of the function: what does each chunk do in plain words?",
        "Which of those jobs does not fit the function name you chose?",
    ]
