"""narrow-the-bug-location — analyze student message for debugging coaching."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SKILLS_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

import coach_lib

SKILL_ID = "narrow-the-bug-location"

_FLOW = {
    coach_lib.EFFORT_LAZY: "step_1_symptoms",
    coach_lib.EFFORT_PARTIAL: "step_2_trusted_vs_untrusted",
    coach_lib.EFFORT_THOUGHTFUL: "step_4_iterate_or_disconfirm",
}


def run(input: dict[str, Any]) -> dict[str, Any]:
    content = coach_lib.get_content(input)
    tier = coach_lib.classify_effort(content)
    signals = coach_lib.detect_student_signals(content)
    focus = _focus(tier, signals)
    stems = _stems(tier, signals)
    return coach_lib.build_coaching_output(
        skill_id=SKILL_ID,
        effort_tier=tier,
        signals=signals,
        coaching_focus=focus,
        question_stems=stems,
        must_avoid=[
            "naming_bug_line_or_function",
            "stack_trace_interpretation_for_them",
            "spec_extraction",
        ],
        route_away=coach_lib.route_hints(signals, SKILL_ID),
        flow_step=coach_lib.flow_step_for_effort(_FLOW, tier),
    )


def _focus(tier: str, signals: list[str]) -> str:
    if coach_lib.SIGNAL_RANDOM_EDITS in signals:
        return "Stop random edits. Get one harness symptom and one falsifiable hypothesis."
    if coach_lib.SIGNAL_FIX_IT in signals:
        return "Refuse fix-it mode. Ask for exact failure text and last trusted run."
    if tier == coach_lib.EFFORT_LAZY:
        return "Demand one concrete artifact: harness line, test name, or before/after observation."
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return "Push disconfirmation: what observation would rule their hypothesis out?"
    return "Compare two suspects or predict next run under hypothesis A vs B."


def _stems(tier: str, signals: list[str]) -> list[str]:
    if coach_lib.SIGNAL_RANDOM_EDITS in signals:
        return [
            "What exact failure text does the harness print on the last run?",
            "What single change would test one hypothesis instead of many edits?",
        ]
    if tier == coach_lib.EFFORT_LAZY:
        return [
            "What is the exact error or wrong output you see right now?",
            "When did you last trust the result, even if that was early?",
        ]
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return [
            "What one observation on the next run would disprove your current guess?",
            "What invariant must still hold at the midpoint you picked?",
        ]
    return [
        "Between your last trusted point and the failure, what midpoint could you probe?",
        "If the bug were before that probe, what would you expect to see?",
    ]
