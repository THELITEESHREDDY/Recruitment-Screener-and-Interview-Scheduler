
from agents.scheduler.state import SchedulerState
from agents.scheduler.tools.availability import get_available_slots
from agents.scheduler.tools.booking import book_interview


def select_candidates(state: SchedulerState) -> dict:
    candidates = state["ranked_candidates"]
    top_n = state["top_n"]

    return {
        "selected_candidates": candidates[:top_n]
    }


def fetch_availability(state: SchedulerState) -> dict:
    slots = get_available_slots()

    return {
        "available_slots": slots
    }



def assign_interviews(state: SchedulerState) -> dict:
    candidates = state["selected_candidates"]
    slots = state["available_slots"]

    schedule = []
    errors = []
    used_slots = set()

    for candidate in candidates:
        assigned = False

        for slot in slots:
            if slot["slot_id"] in used_slots:
                continue

            booking = book_interview(
                slot_id=slot["slot_id"],
                candidate_id=candidate["candidate_id"]
            )

            if not booking["success"]:
                errors.append(
                    f"Booking failed for {slot['slot_id']}: "
                    f"{booking['message']}"
                )
                used_slots.add(slot["slot_id"])
                continue

            used_slots.add(slot["slot_id"])

            schedule.append({
                "candidate_id": candidate["candidate_id"],
                "candidate_name": candidate["candidate_name"],
                "interview_slot": {
                    "slot_id": slot["slot_id"],
                    "start_time": slot["start_time"],
                    "end_time": slot["end_time"]
                },
                "interviewer": {
                    "interviewer_id": slot["interviewer_id"],
                    "interviewer_name": slot["interviewer_name"]
                },
                "status": "confirmed"
            })

            assigned = True
            break

        if not assigned:
            schedule.append({
                "candidate_id": candidate["candidate_id"],
                "candidate_name": candidate["candidate_name"],
                "interview_slot": None,
                "interviewer": None,
                "status": "pending"
            })

    return {
        "schedule": schedule,
        "errors": errors
    }
