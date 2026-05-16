from typing import TypedDict, Optional, Dict, Any

class AgentState(TypedDict):
    patient_id: str
    raw_data: Dict[str, Any]
    deidentified_data: Dict[str, Any]
    eligibility_result: Optional[str]
    eligibility_reason: Optional[str]
    site_assignment: Optional[Dict[str, Any]]
    report: Optional[Dict[str, Any]]
    processing_time: Optional[float]
