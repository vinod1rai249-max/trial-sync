from agent.state import AgentState

def deidentify_node(state: AgentState) -> AgentState:
    raw = state["raw_data"]
    # Simple de-identification: remove name, ssn, etc.
    deidentified = {
        "age": raw.get("age"),
        "hba1c": raw.get("hba1c"),
        "diagnosis": raw.get("diagnosis"),
        "region": raw.get("region", "south"),
        "prior_chemo": raw.get("prior_chemo", False),
        "ecog_status": raw.get("ecog_status", 0)
    }
    return {**state, "deidentified_data": deidentified}
