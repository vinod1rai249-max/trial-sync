import json
import os
from langchain_openai import ChatOpenAI
from agent.state import AgentState
from dotenv import load_dotenv

load_dotenv()

def eligibility_node(state: AgentState) -> AgentState:
    criteria = state["trial_criteria"]
    patient_data = state["deidentified_data"]
    
    # Configure for OpenRouter
    llm = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/TrialSync", # Optional
            "X-Title": "TrialMatch AI", # Optional
        }
    )
    
    prompt = f"""
    You are a clinical trial eligibility auditor.
    Evaluate the following patient against the clinical trial criteria.
    
    Trial Criteria:
    {json.dumps(criteria, indent=2)}
    
    Patient Data:
    {json.dumps(patient_data, indent=2)}
    
    Respond in JSON format with two fields:
    "result": "match" or "no_match"
    "reason": A brief explanation of why the patient matched or failed (mention specific criteria).
    """
    
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        return {
            **state, 
            "eligibility_result": "no_match",
            "eligibility_reason": f"Error calling AI: {str(e)}"
        }
    
    # Try to parse the JSON response
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result_json = json.loads(content)
        return {
            **state, 
            "eligibility_result": result_json.get("result", "no_match"),
            "eligibility_reason": result_json.get("reason", "Unknown error in parsing LLM response")
        }
    except Exception as e:
        return {
            **state, 
            "eligibility_result": "no_match",
            "eligibility_reason": f"Error parsing AI response: {str(e)}"
        }
