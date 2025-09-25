from app.llm.highlight_selector import HighlightSelector, HighlightSelectorParams
from app.llm.schemas import HighlightPlan


def test_heuristic_plan_clamp():
    selector = HighlightSelector()
    params = HighlightSelectorParams(
        max_clips=2,
        min_clip_sec=1,
        max_clip_sec=10,
        llm_style='viral',
        language='pt'
    )
    plan = selector.select(['Primeiro trecho', 'Segundo trecho'], 20, params)
    assert len(plan.clips) <= 2
    for clip in plan.clips:
        assert clip.end_sec > clip.start_sec
        assert clip.end_sec - clip.start_sec <= 10


def test_plan_validation():
    plan = HighlightPlan(clips=[])
    clamped = plan.clamp(duration=30, min_length=5, max_length=10, max_clips=3)
    assert clamped.clips == []
