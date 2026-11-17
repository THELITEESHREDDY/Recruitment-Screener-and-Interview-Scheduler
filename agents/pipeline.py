
from agents.parser.main import process_resume
from agents.matcher.adapter import adapt_parser_output
from agents.matcher.graph import matcher_graph
from agents.ranker.graph import ranker_graph
from agents.scheduler.adapter import adapt_ranked_candidates
from agents.scheduler.graph import scheduler_graph

from sqlalchemy import select

from backend.db.connection import LocalSession
from backend.models.candidate import Candidate



def save_candidate(candidate: dict) -> str:
    with LocalSession() as session:
        existing = session.scalar(
            select(Candidate).where(
                Candidate.id == candidate["id"]
            )
        )

        if existing:
            return existing.id

        db_candidate = Candidate(
            id=candidate["id"],
            name=candidate["name"],
            email=candidate["email"],
            mobile_number=candidate["mobile_number"],
            linkedin_url=candidate["linkedin_url"],
            google_form_response_id=candidate["id"]
        )

        session.add(db_candidate)
        session.commit()

        return db_candidate.id


async def run_recruitment_pipeline(
    jd_id: str,
    job_description: str,
    candidates: list[dict],
    top_n: int
):
    ranked_candidates = []
    candidate_errors = []

    # Parser → Matcher → Ranker
    for candidate_input in candidates:
        candidate_id = candidate_input["candidate_id"]

        try:
            # 1. Parse resume
            parsed_candidate = await process_resume(
                candidate_input["pdf"],
                candidate_id,
                candidate_input["pep_score"],
                candidate_input["pep_priority"]
            )

            # 2. Adapt Parser output
            candidate = adapt_parser_output(parsed_candidate)

            # 3. Persist candidate before ranking
            save_candidate(parsed_candidate)

            # 4. Match candidate
            matcher_result = await matcher_graph.ainvoke({
                "jd_id": jd_id,
                "job_description": job_description,
                "candidate": candidate,
                "retry_count": 0,
                "validation_errors": []
            })

            if matcher_result.get("validation_errors"):
                candidate_errors.append({
                    "candidate_id": candidate_id,
                    "stage": "matcher",
                    "errors": matcher_result["validation_errors"]
                })
                continue

            if "match_result" not in matcher_result:
                candidate_errors.append({
                    "candidate_id": candidate_id,
                    "stage": "matcher",
                    "errors": ["Match result was not generated"]
                })
                continue

            # 5. Rank candidate
            ranker_result = await ranker_graph.ainvoke({
                "jd_id": jd_id,
                "job_description": job_description,
                "incoming_candidate": candidate,
                "match_result": matcher_result["match_result"],
                "errors": []
            })

            if ranker_result.get("errors"):
                candidate_errors.append({
                    "candidate_id": candidate_id,
                    "stage": "ranker",
                    "errors": ranker_result["errors"]
                })
                continue

            ranked_candidates = ranker_result["ranked_candidates"]

        except Exception as exc:
            candidate_errors.append({
                "candidate_id": candidate_id,
                "stage": "pipeline",
                "errors": [str(exc)]
            })

    # Ranker → Scheduler
    if ranked_candidates:
        scheduler_candidates = adapt_ranked_candidates(
            ranked_candidates
        )

        scheduler_result = await scheduler_graph.ainvoke({
            "ranked_candidates": scheduler_candidates,
            "top_n": top_n,
            "selected_candidates": [],
            "available_slots": [],
            "schedule": [],
            "errors": []
        })

        schedule = scheduler_result["schedule"]
        scheduler_errors = scheduler_result["errors"]

    else:
        schedule = []
        scheduler_errors = ["No candidates were successfully ranked"]

    return {
        "ranked_candidates": ranked_candidates,
        "schedule": schedule,
        "candidate_errors": candidate_errors,
        "scheduler_errors": scheduler_errors
    }
