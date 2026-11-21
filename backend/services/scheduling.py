from backend.services.slot_generator import (
    generate_slots,
    generate_automatic_slots
)
from backend.services.interview_assignment import (
    assign_candidates_to_slots
)


def create_interview_schedule(
    ranked_candidates: list[dict],
    config: dict
) -> dict:

    mode = config["mode"]
    top_n = config["top_n"]
    duration = config["interview_duration_minutes"]

    if top_n <= 0:
        raise ValueError("top_n must be positive")

    if len(ranked_candidates) < top_n:
        raise ValueError(
            "Not enough ranked candidates available"
        )

    if mode == "explicit":
        slots = generate_slots(
            schedule=config["schedule"],
            duration_minutes=duration
        )

    elif mode == "automatic":
        working_hours = config["daily_working_hours"]

        slots = generate_automatic_slots(
            start_date=config["start_date"],
            start_time=working_hours["start_time"],
            end_time=working_hours["end_time"],
            duration_minutes=duration,
            candidate_count=top_n
        )

    else:
        raise ValueError(
            f"Unsupported scheduling mode: {mode}"
        )

    schedule = assign_candidates_to_slots(
        ranked_candidates=ranked_candidates,
        slots=slots,
        top_n=top_n
    )

    return {
        "mode": mode,
        "total_scheduled": len(schedule),
        "schedule": schedule
    }