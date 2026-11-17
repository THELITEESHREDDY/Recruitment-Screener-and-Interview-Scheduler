from agents.scheduler.graph import scheduler_graph
from agents.scheduler.tools.availability import get_available_slots
from agents.scheduler.tools.booking import booked_slots, book_interview
import pytest

@pytest.fixture(autouse=True)
def reset_booked_slots():
    booked_slots.clear()
    yield
    booked_slots.clear()


@pytest.fixture
def scheduler_input():
    return {
        "ranked_candidates": [
            {
                "candidate_id": f"CAND_00{i}",
                "candidate_name": name,
                "ranking_score": score,
                "rank": i
            }
            for i, (name, score) in enumerate(
                [("Alice", 94), ("Bob", 89), ("Charlie", 85)],
                start=1
            )
        ],
        "top_n": 3,
        "selected_candidates": [],
        "available_slots": [],
        "schedule": [],
        "errors": []
    }



def test_scheduler_with_insufficient_slots(monkeypatch, scheduler_input):
    booked_slots.clear()

    monkeypatch.setattr(
        "agents.scheduler.nodes.get_available_slots",
        lambda: get_available_slots()[:2]
    )

    result = scheduler_graph.invoke(scheduler_input)

    statuses = [item["status"] for item in result["schedule"]]

    assert statuses == ["confirmed", "confirmed", "pending"]


def test_scheduler_with_booking_failure(scheduler_input):
    booked_slots.clear()

    book_interview("SLOT_001", "OTHER_CANDIDATE")

    result = scheduler_graph.invoke(scheduler_input)

    statuses = [item["status"] for item in result["schedule"]]

    assert statuses == ["confirmed", "confirmed", "confirmed"]
    assert result["schedule"][0]["interview_slot"]["slot_id"] == "SLOT_002"
    assert len(result["errors"]) == 1


def test_scheduler_graph():
    initial_state = {
        "ranked_candidates": [
            {
                "candidate_id": "CAND_001",
                "candidate_name": "Alice",
                "ranking_score": 94,
                "rank": 1
            },
            {
                "candidate_id": "CAND_002",
                "candidate_name": "Bob",
                "ranking_score": 89,
                "rank": 2
            },
            {
                "candidate_id": "CAND_003",
                "candidate_name": "Charlie",
                "ranking_score": 85,
                "rank": 3
            }
        ],
        "top_n": 2,
        "selected_candidates": [],
        "available_slots": [],
        "schedule": [],
        "errors": []
    }

    result = scheduler_graph.invoke(initial_state)

    assert len(result["selected_candidates"]) == 2
    assert len(result["schedule"]) == 2

    assert result["schedule"][0]["status"] == "confirmed"
    assert result["schedule"][1]["status"] == "confirmed"

    assert result["schedule"][0]["candidate_id"] == "CAND_001"
    assert result["schedule"][1]["candidate_id"] == "CAND_002"

    assert len(result["errors"]) == 0




def test_scheduler_retries_next_slot(scheduler_input):
    booked_slots.clear()

    book_interview("SLOT_001", "OTHER_CANDIDATE")

    result = scheduler_graph.invoke(scheduler_input)

    first_candidate = result["schedule"][0]

    assert first_candidate["status"] == "confirmed"
    assert first_candidate["interview_slot"]["slot_id"] == "SLOT_002"