from agent.state import AgentState

SITES = [
    {"site_id": "S01", "name": "Chennai Central Lab", "capacity": 8,  "region": "south"},
    {"site_id": "S02", "name": "Mumbai Trial Hub",    "capacity": 3,  "region": "west"},
    {"site_id": "S03", "name": "Delhi Oncology Ctr",  "capacity": 12, "region": "north"},
]

def site_match_node(state: AgentState) -> AgentState:
    patient_region = state["deidentified_data"].get("region", "south")
    scored = []
    for site in SITES:
        score = site["capacity"] * 0.6
        if site["region"] == patient_region:
            score += 20                  # proximity bonus
        scored.append({**site, "score": round(score, 1)})
    
    # Sort by score descending and pick best
    best = max(scored, key=lambda s: s["score"])
    return {**state, "site_assignment": best}
