from typing import TypedDict


class SchedulerState(TypedDict):
    ranked_candidates: list[dict]
    top_n: int
    selected_candidates: list[dict]
    available_slots: list[dict]
    schedule: list[dict]
    errors: list[str]