booked_slots = set()


def book_interview(slot_id: str, candidate_id: str) -> dict:
    if slot_id in booked_slots:
        return {
            "success": False,
            "message": "Slot already booked"
        }

    booked_slots.add(slot_id)

    return {
        "success": True,
        "slot_id": slot_id,
        "candidate_id": candidate_id,
        "message": "Interview booked successfully"
    }