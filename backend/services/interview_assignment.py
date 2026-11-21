def assign_candidates_to_slots(
    ranked_candidates: list[dict],
    slots: list[dict],
    top_n: int
) -> list[dict]:

    if top_n <= 0:
        raise ValueError("top_n must be positive")

    if len(slots) < top_n:
        raise ValueError(
            "Insufficient interview slots for selected candidates"
        )

    # Rank 1 gets the earliest slot.
    sorted_candidates = sorted(
        ranked_candidates,
        key=lambda candidate: (
            candidate["rank"],
            -candidate["overall_score"],
            candidate["candidate_id"]
        )
    )

    selected_candidates = sorted_candidates[:top_n]

    if len(selected_candidates) < top_n:
        raise ValueError(
            "Not enough ranked candidates available"
        )

    sorted_slots = sorted(
        slots,
        key=lambda slot: (
            slot["date"],
            slot["start_time"]
        )
    )

    schedule = []

    for candidate, slot in zip(
        selected_candidates,
        sorted_slots
    ):
        schedule.append({
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["candidate_name"],
            "rank": candidate["rank"],
            "overall_score": candidate["overall_score"],
            "interview_slot": slot,
            "status": "scheduled"
        })

    return schedule