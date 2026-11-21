import pytest
from backend.services.slot_generator import generate_automatic_slots
from backend.services.slot_generator import generate_slots


def test_generates_slots():
    schedule = [
        {
            "date": "2026-11-23",
            "start_time": "10:00",
            "end_time": "11:30"
        }
    ]

    result = generate_slots(schedule, 30)

    assert len(result) == 3
    assert result[0]["start_time"] == "10:00"
    assert result[-1]["end_time"] == "11:30"


def test_does_not_exceed_working_hours():
    schedule = [
        {
            "date": "2026-11-23",
            "start_time": "10:00",
            "end_time": "11:10"
        }
    ]

    result = generate_slots(schedule, 30)

    assert len(result) == 2
    assert result[-1]["end_time"] == "11:00"


def test_multiple_dates_sorted():
    schedule = [
        {
            "date": "2026-11-24",
            "start_time": "14:00",
            "end_time": "15:00"
        },
        {
            "date": "2026-11-23",
            "start_time": "10:00",
            "end_time": "11:00"
        }
    ]

    result = generate_slots(schedule, 30)

    assert len(result) == 4
    assert result[0]["date"] == "2026-11-23"
    assert result[-1]["date"] == "2026-11-24"


def test_invalid_working_hours():
    schedule = [
        {
            "date": "2026-11-23",
            "start_time": "17:00",
            "end_time": "10:00"
        }
    ]

    with pytest.raises(ValueError):
        generate_slots(schedule, 30)


def test_overlapping_windows_rejected():
    schedule = [
        {
            "date": "2026-11-23",
            "start_time": "10:00",
            "end_time": "11:00"
        },
        {
            "date": "2026-11-23",
            "start_time": "10:30",
            "end_time": "11:30"
        }
    ]

    with pytest.raises(ValueError):
        generate_slots(schedule, 30)


def test_invalid_duration():
    with pytest.raises(ValueError):
        generate_slots([], 0)






def test_automatic_slots_single_day():
    result = generate_automatic_slots(
        start_date="2026-11-23",
        start_time="10:00",
        end_time="12:00",
        duration_minutes=30,
        candidate_count=3
    )

    assert len(result) == 3
    assert all(
        slot["date"] == "2026-11-23"
        for slot in result
    )


def test_automatic_slots_multiple_days():
    result = generate_automatic_slots(
        start_date="2026-11-23",
        start_time="10:00",
        end_time="11:00",
        duration_minutes=30,
        candidate_count=5
    )

    assert len(result) == 5

    assert [slot["date"] for slot in result] == [
        "2026-11-23",
        "2026-11-23",
        "2026-11-24",
        "2026-11-24",
        "2026-11-25"
    ]


def test_automatic_slots_insufficient_daily_hours():
    with pytest.raises(ValueError):
        generate_automatic_slots(
            start_date="2026-11-23",
            start_time="10:00",
            end_time="10:20",
            duration_minutes=30,
            candidate_count=3
        )


def test_automatic_slots_invalid_candidate_count():
    with pytest.raises(ValueError):
        generate_automatic_slots(
            start_date="2026-11-23",
            start_time="10:00",
            end_time="12:00",
            duration_minutes=30,
            candidate_count=0
        )