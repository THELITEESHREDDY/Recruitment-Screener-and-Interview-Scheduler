
from langgraph.graph import StateGraph, START, END

from .state import RankerState
from .nodes import (
    get_or_create_secondary_rubric,
    load_existing_rankings,
    evaluate_secondary_metrics,
    calculate_secondary_score,
    rank_candidates,
    persist_rankings,
)


def route_on_error(state: RankerState):
    if state.get("errors"):
        return "stop"

    return "continue"


def build_ranker_graph():
    builder = StateGraph(RankerState)

    builder.add_node("get_or_create_secondary_rubric", get_or_create_secondary_rubric)
    builder.add_node("load_existing_rankings", load_existing_rankings)
    builder.add_node("evaluate_secondary_metrics", evaluate_secondary_metrics)
    builder.add_node("calculate_secondary_score", calculate_secondary_score)
    builder.add_node("rank_candidates", rank_candidates)
    builder.add_node("persist_rankings", persist_rankings)

    builder.add_edge(START, "get_or_create_secondary_rubric")

    builder.add_conditional_edges(
        "get_or_create_secondary_rubric",
        route_on_error,
        {
            "continue": "load_existing_rankings",
            "stop": END,
        },
    )

    builder.add_conditional_edges(
        "load_existing_rankings",
        route_on_error,
        {
            "continue": "evaluate_secondary_metrics",
            "stop": END,
        },
    )

    builder.add_conditional_edges(
        "evaluate_secondary_metrics",
        route_on_error,
        {
            "continue": "calculate_secondary_score",
            "stop": END,
        },
    )

    builder.add_conditional_edges(
        "calculate_secondary_score",
        route_on_error,
        {
            "continue": "rank_candidates",
            "stop": END,
        },
    )

    builder.add_conditional_edges(
        "rank_candidates",
        route_on_error,
        {
            "continue": "persist_rankings",
            "stop": END,
        },
    )

    builder.add_edge("persist_rankings", END)

    return builder.compile()


ranker_graph = build_ranker_graph()
