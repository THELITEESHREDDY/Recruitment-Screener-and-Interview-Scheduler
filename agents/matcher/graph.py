from langgraph.graph import StateGraph, START, END

from agents.matcher.state.matcher_state import MatcherState

from agents.matcher.nodes import (
    get_ideal_candidate,
    generate_ideal_candidate,
    save_ideal_candidate,
    match_candidate,
    calculate_match_score,
    validate_match_result,
    prepare_retry,
    ideal_candidate_router,
    validation_router
)


builder = StateGraph(MatcherState)


# Register nodes

builder.add_node("get_ideal_candidate", get_ideal_candidate)
builder.add_node("generate_ideal_candidate", generate_ideal_candidate)
builder.add_node("save_ideal_candidate", save_ideal_candidate)
builder.add_node("match_candidate", match_candidate)
builder.add_node("calculate_match_score", calculate_match_score)
builder.add_node("validate_match_result", validate_match_result)
builder.add_node("prepare_retry", prepare_retry)


# Entry point

builder.add_edge(START, "get_ideal_candidate")


# Ideal candidate retrieval / generation

builder.add_conditional_edges(
    "get_ideal_candidate",
    ideal_candidate_router,
    {
        "match": "match_candidate",
        "generate": "generate_ideal_candidate"
    }
)

builder.add_edge("generate_ideal_candidate", "save_ideal_candidate")
builder.add_edge("save_ideal_candidate", "match_candidate")


# Matching and scoring

builder.add_edge("match_candidate", "calculate_match_score")
builder.add_edge("calculate_match_score", "validate_match_result")


# Validation and retry

builder.add_conditional_edges(
    "validate_match_result",
    validation_router,
    {
        "retry": "prepare_retry",
        "success": END,
        "failed": END
    }
)

builder.add_edge("prepare_retry", "match_candidate")


# Compile

matcher_graph = builder.compile()