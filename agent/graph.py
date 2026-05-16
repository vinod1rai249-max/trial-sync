from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.deidentify import deidentify_node
from agent.nodes.eligibility import eligibility_node
from agent.nodes.site_match import site_match_node
from agent.nodes.report_gen import report_gen_node, reject_node

def route_eligibility(state: AgentState) -> str:
    return "site_match" if state["eligibility_result"] == "match" else "reject"

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)
    
    g.add_node("deidentify",  deidentify_node)
    g.add_node("eligibility", eligibility_node)
    g.add_node("site_match",  site_match_node)
    g.add_node("report_gen",  report_gen_node)
    g.add_node("reject",      reject_node)
    
    g.set_entry_point("deidentify")
    
    g.add_edge("deidentify", "eligibility")
    
    g.add_conditional_edges("eligibility", route_eligibility, {
        "site_match": "site_match",
        "reject":     "reject"
    })
    
    g.add_edge("site_match", "report_gen")
    g.add_edge("report_gen", END)
    g.add_edge("reject",     END)
    
    return g.compile()
