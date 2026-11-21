import pytest

from backend.services.scheduling import (
    create_interview_schedule
)


@pytest.fixture
def ranked_candidates():
    return [
        {
            "candidate_id": "CAND_001",
            "candidate_name": "Alice",
            "rank": 1,
            "overall_score": 95
        },
        {
            "candidate_id": "CAND_002",
            "candidate_name": "Bob",
            "rank": 2,
            "overall_score": 88
        },
        {
            "candidate_id": "CAND_003",
            "candidate_name": "Charlie",
            "rank": 3,
            "overall_score": 80
        }
    ]


def test_explicit_scheduling(ranked_candidates):
    config = {
        "mode": "explicit",
        "top_n": 2,
        "interview_duration_minutes": 30,
        "schedule": [
            {
                "date": "2026-11-23",
                "start_time": "10:00",
                "end_time": "11:00"
            }
        ]
    }

    result = create_interview_schedule(
        ranked_candidates,
        config
    )

    assert result["mode"] == "explicit"
    assert result["total_scheduled"] == 2

    assert [
        item["candidate_id"]
        for item in result["schedule"]
    ] == ["CAND_001", "CAND_002"]


def test_automatic_scheduling(ranked_candidates):
    config = {
        "mode": "automatic",
        "top_n": 3,
        "interview_duration_minutes": 30,
        "start_date": "2026-11-23",
        "daily_working_hours": {
            "start_time": "10:00",
            "end_time": "11:00"
        }
    }

    result = create_interview_schedule(
        ranked_candidates,
        config
    )

    assert result["mode"] == "automatic"
    assert result["total_scheduled"] == 3

    assert [
        item["interview_slot"]["date"]
        for item in result["schedule"]
    ] == [
        "2026-11-23",
        "2026-11-23",
        "2026-11-24"
    ]


def test_explicit_insufficient_slots(ranked_candidates):
    config = {
        "mode": "explicit",
        "top_n": 3,
        "interview_duration_minutes": 30,
        "schedule": [
            {
                "date": "2026-11-23",
                "start_time": "10:00",
                "end_time": "11:00"
            }
        ]
    }

    with pytest.raises(
        ValueError,
        match="Insufficient interview slots"
    ):
        create_interview_schedule(
            ranked_candidates,
            config
        )


def test_invalid_scheduling_mode(ranked_candidates):
    config = {
        "mode": "unknown",
        "top_n": 2,
        "interview_duration_minutes": 30
    }

    with pytest.raises(
        ValueError,
        match="Unsupported scheduling mode"
    ):
        create_interview_schedule(
            ranked_candidates,
            config
        )