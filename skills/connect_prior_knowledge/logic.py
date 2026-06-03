"""connect-prior-knowledge — bridge from prior courses without lecturing."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SKILLS_ROOT = Path(__file__).resolve().parent.parent
if str(_SKILLS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILLS_ROOT))

import coach_lib

SKILL_ID = "connect-prior-knowledge"

_FLOW = {
    coach_lib.EFFORT_LAZY: "step_1_surface_prior",
    coach_lib.EFFORT_PARTIAL: "step_2_prompt_connection",
    coach_lib.EFFORT_THOUGHTFUL: "step_3_check_analogy_limits",
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
            "delivering_analogy",
            "os_concept_lecture",
            "mapping_terms_for_them",
        ],
        route_away=coach_lib.route_hints(signals, SKILL_ID),
        flow_step=coach_lib.flow_step_for_effort(_FLOW, tier),
    )


def _focus(tier: str) -> str:
    if tier == coach_lib.EFFORT_LAZY:
        return "Ask which earlier course topic feels closest and one rule they remember."
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return "Ask where their analogy would fail in NK or the lab harness."
    return "Ask them to predict one way the OS version must differ from the prior idea."


def _stems(tier: str) -> list[str]:
    if tier == coach_lib.EFFORT_LAZY:
        return [
            "Which topic from an earlier course feels closest to what you are seeing now?",
            "What is one rule or definition you still remember from that topic?",
        ]
    if tier == coach_lib.EFFORT_THOUGHTFUL:
        return [
            "Where would your analogy break in this kernel or harness?",
            "What difference would you expect if the prior-course rule applied literally here?",
        ]
    return [
        "How do you think that prior idea maps onto this lab, in your own words?",
        "What must be different here because this is kernel or OS code, not user space?",
    ]
