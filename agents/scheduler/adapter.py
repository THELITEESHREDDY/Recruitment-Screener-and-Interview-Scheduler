def adapt_ranked_candidates(ranked_candidates: list[dict]) -> list[dict]:
    return [
        {
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["candidate_name"],
            "ranking_score": candidate["overall_score"],
            "rank": candidate["rank"]
        }
        for candidate in ranked_candidates
    ]


