from datetime import datetime, timedelta,date


def generate_slots(
    schedule: list[dict],
    duration_minutes: int
) -> list[dict]:

    if duration_minutes <= 0:
        raise ValueError("Interview duration must be positive")

    slots = []
    duration = timedelta(minutes=duration_minutes)

    for window in schedule:
        date = window["date"]

        start = datetime.fromisoformat(
            f"{date}T{window['start_time']}"
        )

        end = datetime.fromisoformat(
            f"{date}T{window['end_time']}"
        )

        if start >= end:
            raise ValueError("Invalid working hours")

        current = start

        while current + duration <= end:
            slot_end = current + duration

            slots.append({
                "date": current.date().isoformat(),
                "start_time": current.strftime("%H:%M"),
                "end_time": slot_end.strftime("%H:%M")
            })

            current = slot_end

    slots.sort(
        key=lambda slot: (
            slot["date"],
            slot["start_time"]
        )
    )

    # Reject overlapping slots from overlapping input windows.
    for previous, current in zip(slots, slots[1:]):
        if (
            previous["date"] == current["date"]
            and current["start_time"] < previous["end_time"]
        ):
            raise ValueError("Overlapping interview slots")

    return slots


def generate_automatic_slots(
    start_date: str,
    start_time: str,
    end_time: str,
    duration_minutes: int,
    candidate_count: int
) -> list[dict]:

    if candidate_count <= 0:
        raise ValueError("Candidate count must be positive")

    if duration_minutes <= 0:
        raise ValueError("Interview duration must be positive")

    current_date = date.fromisoformat(start_date)

    # Validate working hours and ensure at least one slot fits.
    daily_slots = generate_slots(
        [{
            "date": current_date.isoformat(),
            "start_time": start_time,
            "end_time": end_time
        }],
        duration_minutes
    )

    if not daily_slots:
        raise ValueError(
            "Working hours cannot fit an interview"
        )

    slots = []

    while len(slots) < candidate_count:
        daily_slots = generate_slots(
            [{
                "date": current_date.isoformat(),
                "start_time": start_time,
                "end_time": end_time
            }],
            duration_minutes
        )

        remaining = candidate_count - len(slots)

        slots.extend(daily_slots[:remaining])

        current_date += timedelta(days=1)

    return slots