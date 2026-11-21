import pytest

from backend.services.interview_assignment import (
    assign_candidates_to_slots
)


@pytest.fixture
def ranked_candidates():
    return [
        {
            "candidate_id": "CAND_003",
            "candidate_name": "Charlie",
            "rank": 3,
            "overall_score": 80
        },
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
        }
    ]


@pytest.fixture
def slots():
    return [
        {
            "date": "2026-11-24",
            "start_time": "10:00",
            "end_time": "10:30"
        },
        {
            "date": "2026-11-23",
            "start_time": "10:30",
            "end_time": "11:00"
        },
        {
            "date": "2026-11-23",
            "start_time": "10:00",
            "end_time": "10:30"
        }
    ]


def test_assigns_candidates_by_rank(ranked_candidates, slots):
    result = assign_candidates_to_slots(
        ranked_candidates,
        slots,
        top_n=3
    )

    assert len(result) == 3

    assert [item["candidate_id"] for item in result] == [
        "CAND_001",
        "CAND_002",
        "CAND_003"
    ]

    assert result[0]["interview_slot"]["start_time"] == "10:00"
    assert result[0]["interview_slot"]["date"] == "2026-11-23"


def test_selects_top_n_candidates(ranked_candidates, slots):
    result = assign_candidates_to_slots(
        ranked_candidates,
        slots,
        top_n=2
    )

    assert len(result) == 2

    assert [item["candidate_id"] for item in result] == [
        "CAND_001",
        "CAND_002"
    ]


def test_insufficient_slots(ranked_candidates):
    with pytest.raises(ValueError):
        assign_candidates_to_slots(
            ranked_candidates,
            slots=[
                {
                    "date": "2026-11-23",
                    "start_time": "10:00",
                    "end_time": "10:30"
                }
            ],
            top_n=3
        )


def test_insufficient_candidates(ranked_candidates, slots):
    with pytest.raises(ValueError):
        assign_candidates_to_slots(
            ranked_candidates[:2],
            slots,
            top_n=3
        )


def test_invalid_top_n(ranked_candidates, slots):
    with pytest.raises(ValueError):
        assign_candidates_to_slots(
            ranked_candidates,
            slots,
            top_n=0
        )