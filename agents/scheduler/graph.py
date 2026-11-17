from langgraph.graph import StateGraph, START, END

from agents.scheduler.state import SchedulerState
from agents.scheduler.nodes import (
    select_candidates,
    fetch_availability,
    assign_interviews
)

def build_scheduler_graph():
    graph = StateGraph(SchedulerState)

    graph.add_node("select_candidates", select_candidates)
    graph.add_node("fetch_availability", fetch_availability)
    graph.add_node("assign_interviews", assign_interviews)

    graph.add_edge(START, "select_candidates")
    graph.add_edge("select_candidates", "fetch_availability")
    graph.add_edge("fetch_availability", "assign_interviews")
    graph.add_edge("assign_interviews", END)

    return graph.compile()

scheduler_graph = build_scheduler_graph()