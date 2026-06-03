"""ask-for-decomposition — analyze student message for planning coaching."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SKILLS_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

import coach_lib

SKILL_ID = "ask-for-decomposition"

_FLOW = {
    coach_lib.EFFORT_LAZY: "step_1_identify_block",
    coach_lib.EFFORT_PARTIAL: "step_2_prompt_decomposition",
    coach_lib.EFFORT_THOUGHTFUL: "step_3_smallest_testable_step",
}


def run(input: dict[str, Any]) -> dict[str, Any]:
    content = coach_lib.get_content(input)
    tier = coach_lib.classify_effort(content)
    signals = coach_lib.detect_student_signals(content)
    if coach_lib.SIGNAL_SPEC_CONFUSION in signals:
        route = ["extract-requirements"]
    else:
        route = coach_lib.route_hints(signals, SKILL_ID)
    return coach_lib.build_coaching_output(
        skill_id=SKILL_ID,
        effort_tier=tier,
        signals=signals,
        coaching_focus=_focus(tier, signals),
        question_stems=_stems(tier, signals),
        must_avoid=[
            "numbered_milestone_list",
            "full_implementation_order",
            "assignment_spec_extraction",
        ],
        route_away=route,
        flow_step=coach_lib.flow_step_for_effort(_FLOW, tier),
    )


def _focus(tier: str, signals: list[str]) -> str:
    if coach_lib.SIGNAL_SPEC_CONFUSION in signals:
        return "Spec confusion detected. Defer deliverable questions to extract-requirements."
    if coach_lib.SIGNAL_CODE_BEG in signals or coach_lib.SIGNAL_FIX_IT in signals:
        return "Refuse end-to-end solution. Get one milestone they name plus smallest next action."
    if tier == coach_lib.EFFORT_LAZY:
        return "Ask for one milestone they already see and one step doable in under an hour."
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return "Ask which milestone is blocked by a missing interface or invariant."
    return "Ask them to compare two first steps and what each would prove."


def _stems(tier: str, signals: list[str]) -> list[str]:
    if coach_lib.SIGNAL_SPEC_CONFUSION in signals:
        return [
            "Before planning code, which part of the spec are you unsure is required?",
            "What one deliverable phrase would you quote from the handout?",
        ]
    if tier == coach_lib.EFFORT_LAZY:
        return [
            "What is one piece of this lab you already know how to finish?",
            "What is the smallest next action you could try in under an hour?",
        ]
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return [
            "Which milestone is blocked until you define an interface or invariant?",
            "What would you test first to know that milestone is done?",
        ]
    return [
        "If you split the work into two steps, what must step one prove?",
        "What information do you need before writing more code?",
    ]
