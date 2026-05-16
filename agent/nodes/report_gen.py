from agent.state import AgentState
from datetime import datetime

def report_gen_node(state: AgentState) -> AgentState:
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "patient_id": state["patient_id"],
        "eligibility": state["eligibility_result"],
        "eligibility_reason": state["eligibility_reason"],
        "recommended_site": state["site_assignment"],
        "next_action": "Initiate consent process with patient" if state["eligibility_result"] == "match"
                       else "No action required",
        "consent_required": True
    }
    return {**state, "report": report}

def reject_node(state: AgentState) -> AgentState:
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "patient_id": state["patient_id"],
        "eligibility": "no_match",
        "reason": state["eligibility_reason"],
        "next_action": "Patient does not qualify for this trial",
        "consent_required": False
    }
    return {**state, "report": report}
