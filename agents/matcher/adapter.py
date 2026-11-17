from agents.matcher.state.candidate import CandidateState


def adapt_parser_output(parsed_candidate: dict) -> CandidateState:
    return {
        "id": parsed_candidate["id"],
        "name": parsed_candidate["name"],
        "mobile_number": parsed_candidate["mobile_number"],
        "email": parsed_candidate["email"],
        "linkedin_url": parsed_candidate["linkedin_url"],

        "technical_skills": parsed_candidate["technical_skills"],
        "soft_skills": parsed_candidate["soft_skills"],
        "tech_stacks": parsed_candidate["tech_stacks"],
        "tools_and_platforms": parsed_candidate["tools_and_platforms"],
        "certifications": parsed_candidate["certifications"],
        "work_experience": parsed_candidate["work_experience"],
        "coursework": parsed_candidate["coursework"],
        "achievements": parsed_candidate["achievements"],
        "education": parsed_candidate["education"],

        "PEP_score": parsed_candidate["PEP_score"],
        "PEP_priority": parsed_candidate["PEP_priority"]
    }