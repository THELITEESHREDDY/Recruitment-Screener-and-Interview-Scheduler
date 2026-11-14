from langgraph.graph import StateGraph, START, END

from .state import OverallState
from .nodes import (
    parse_resume_content,
    get_contact_details,
    get_skills,
    get_domain_skills,
    get_academic_details,
    get_professional_details
)


def build_resume_graph():

    builder = StateGraph(OverallState)

    # Register nodes
    builder.add_node(
        "parse_resume_content",
        parse_resume_content
    )

    builder.add_node(
        "get_contact_details",
        get_contact_details
    )

    builder.add_node(
        "get_skills",
        get_skills
    )

    builder.add_node(
        "get_domain_skills",
        get_domain_skills
    )

    builder.add_node(
        "get_academic_details",
        get_academic_details
    )

    builder.add_node(
        "get_professional_details",
        get_professional_details
    )

    # Define execution flow
    builder.add_edge(START, "parse_resume_content")

    builder.add_edge(
        "parse_resume_content",
        "get_contact_details"
    )

    builder.add_edge(
        "get_contact_details",
        "get_skills"
    )

    builder.add_edge(
        "get_skills",
        "get_domain_skills"
    )

    builder.add_edge(
        "get_domain_skills",
        "get_academic_details"
    )

    builder.add_edge(
        "get_academic_details",
        "get_professional_details"
    )

    builder.add_edge(
        "get_professional_details",
        END
    )

    return builder.compile()


resume_graph = build_resume_graph()