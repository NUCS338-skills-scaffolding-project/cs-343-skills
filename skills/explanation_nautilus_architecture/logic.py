"""explanation-nautilus-architecture — orient in starter codebase without dumping maps."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SKILLS_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

import coach_lib

SKILL_ID = "explanation-nautilus-architecture"

_FLOW = {
    coach_lib.EFFORT_LAZY: "step_1_name_subsystem",
    coach_lib.EFFORT_PARTIAL: "step_2_execution_stage",
    coach_lib.EFFORT_THOUGHTFUL: "step_3_invariant_at_stage",
}


def run(input: dict[str, Any]) -> dict[str, Any]:
    content = coach_lib.get_content(input)
    tier = coach_lib.classify_effort(content)
    signals = coach_lib.detect_student_signals(content)
    route = coach_lib.route_hints(signals, SKILL_ID)
    if coach_lib.SIGNAL_SPEC_CONFUSION in signals:
        route = list(dict.fromkeys(route + ["extract-requirements"]))
    return coach_lib.build_coaching_output(
        skill_id=SKILL_ID,
        effort_tier=tier,
        signals=signals,
        coaching_focus=_focus(tier, signals),
        question_stems=_stems(tier, signals),
        must_avoid=[
            "directory_trees",
            "call_graph_dumps",
            "boot_or_paging_lecture",
            "naming_files_to_edit_for_them",
        ],
        route_away=route,
        flow_step=coach_lib.flow_step_for_effort(_FLOW, tier),
    )


def _focus(tier: str, signals: list[str]) -> str:
    if coach_lib.SIGNAL_FIX_IT in signals or coach_lib.SIGNAL_RANDOM_EDITS in signals:
        return "Not orientation. Route mindset to repro and hypothesis, not file picks."
    if coach_lib.SIGNAL_CODE_BEG in signals:
        return "Redirect from what to write to which boot or test stage they are in."
    if tier == coach_lib.EFFORT_LAZY:
        return "Ask which subsystem or file they chose and what changed last."
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return "Ask what invariant must hold at their named stage and who runs next."
    return "Ask them to predict the next execution stage after their current stop."


def _stems(tier: str, signals: list[str]) -> list[str]:
    if coach_lib.SIGNAL_FIX_IT in signals or coach_lib.SIGNAL_RANDOM_EDITS in signals:
        return [
            "Which test or boot stage fails, and what changed right before that?",
            "What one log line or symptom tells you the stage you are in?",
        ]
    if tier == coach_lib.EFFORT_LAZY:
        return [
            "Which file or symbol did you pick to read first, and why?",
            "What part of the lab do you think runs before your code is called?",
        ]
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return [
            "What invariant must hold at that stage in the starter tree?",
            "Who should run immediately after that point if your mental model is right?",
        ]
    return [
        "At the point you are stuck, what stage of boot or test is running?",
        "What would you expect the next component to do if control leaves there?",
    ]
