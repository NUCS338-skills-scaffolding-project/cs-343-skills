"""evaluate-readability-on-code — one-spot readability coaching."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SKILLS_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

import coach_lib

SKILL_ID = "evaluate-readability-on-code"

_FLOW = {
    coach_lib.EFFORT_LAZY: "step_1_direct_attention",
    coach_lib.EFFORT_PARTIAL: "step_2_self_evaluate",
    coach_lib.EFFORT_THOUGHTFUL: "step_3_prioritize_fix",
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
            "rewritten_code",
            "whole_file_score",
            "style_makeover_list",
        ],
        route_away=coach_lib.route_hints(signals, SKILL_ID),
        flow_step=coach_lib.flow_step_for_effort(_FLOW, tier),
    )


def _focus(tier: str) -> str:
    if tier == coach_lib.EFFORT_LAZY:
        return "Make them pick one line they would hate to read at 2am and say why."
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return "Ask which muddy boundary hurts the next reader most."
    return "Ask if a named variable or branch matches what it actually does."


def _stems(tier: str) -> list[str]:
    if tier == coach_lib.EFFORT_LAZY:
        return [
            "Which single line in your snippet would confuse you at 2am?",
            "What would a new reader think that line does, in one phrase?",
        ]
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return [
            "Which responsibility blur would confuse someone reading this for the first time?",
            "If you fixed only one spot today, which confusion would you remove?",
        ]
    return [
        "Does the name on that variable match what the value represents?",
        "In plain words, what does that branch do, and does the code say the same?",
    ]
