from datetime import datetime


def get_available_slots() -> list[dict]:
    return [
        {
            "slot_id": "SLOT_001",
            "start_time": datetime(2026, 11, 20, 10, 0),
            "end_time": datetime(2026, 11, 20, 10, 30),
            "interviewer_id": "INT_001",
            "interviewer_name": "John"
        },
        {
            "slot_id": "SLOT_002",
            "start_time": datetime(2026, 11, 20, 10, 30),
            "end_time": datetime(2026, 11, 20, 11, 0),
            "interviewer_id": "INT_002",
            "interviewer_name": "Sarah"
        },
        {
            "slot_id": "SLOT_003",
            "start_time": datetime(2026, 11, 20, 11, 0),
            "end_time": datetime(2026, 11, 20, 11, 30),
            "interviewer_id": "INT_001",
            "interviewer_name": "John"
        },
        {
            "slot_id": "SLOT_004",
            "start_time": datetime(2026, 11, 20, 11, 30),
            "end_time": datetime(2026, 11, 20, 12, 0),
            "interviewer_id": "INT_003",
            "interviewer_name": "David"
        },
        {
            "slot_id": "SLOT_005",
            "start_time": datetime(2026, 11, 20, 12, 0),
            "end_time": datetime(2026, 11, 20, 12, 30),
            "interviewer_id": "INT_002",
            "interviewer_name": "Sarah"
        }
    ]