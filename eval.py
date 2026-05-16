import os
import uuid
import json
from langsmith import Client, evaluate
from agent.graph import build_graph
from utils.synthea_sim import generate_synthetic_patients
from dotenv import load_dotenv

load_dotenv()

# Initialize LangSmith Client
client = Client()

# Compile our LangGraph
graph = build_graph()

def run_agent(input_dict: dict):
    """
    Wrapper function for LangSmith evaluation.
    Takes a single patient's raw data and returns the agent's eligibility result.
    """
    initial_state = {
        "patient_id": str(uuid.uuid4()),
        "raw_data": input_dict,
        "deidentified_data": {},
        "eligibility_result": None,
        "eligibility_reason": None,
        "site_assignment": None,
        "report": None,
        "processing_time": 0.0
    }
    
    # LangSmith will trace this automatically if LANGSMITH_TRACING=true
    config = {"run_name": f"Eval-Run-{initial_state['patient_id'][:8]}", "tags": ["evaluation"]}
    result = graph.invoke(initial_state, config=config)
    
    return {
        "eligibility": result["eligibility_result"],
        "reason": result["eligibility_reason"]
    }

def run_evaluation():
    print("🚀 Starting LangSmith Evaluation for TrialMatch AI...")
    
    # 1. Create a mini dataset of 5 synthetic patients for evaluation
    eval_patients = generate_synthetic_patients(5)
    
    # Format for LangSmith evaluate
    inputs = [{"name": p["name"], "age": p["age"], "hba1c": p["hba1c"], 
               "diagnosis": p["diagnosis"], "region": p["region"], 
               "prior_chemo": p["prior_chemo"]} for p in eval_patients]
    
    # Note: In a real scenario, you'd upload this to LangSmith as a 'Dataset'
    # For the hackathon demo, we can just run against this list.
    
    print(f"📋 Running agent against {len(inputs)} evaluation cases...")
    
    # 2. Define a simple evaluator (e.g., just checking if it returned a result)
    def check_result(run, example):
        output = run.outputs
        if output and "eligibility" in output:
            return {"key": "has_result", "score": 1}
        return {"key": "has_result", "score": 0}

    # 3. Execute evaluation
    # Note: evaluate() usually expects a dataset name. 
    # For local testing, we'll just invoke manually in a loop for the demo.
    for i, p_data in enumerate(inputs):
        print(f"  [{i+1}/5] Evaluating {p_data['name']} (Age: {p_data['age']}, Diagnosis: {p_data['diagnosis']})...")
        result = run_agent(p_data)
        print(f"      Result: {result['eligibility']} | Reason: {result['reason'][:50]}...")

    print("\n✅ Evaluation complete! Check your LangSmith dashboard for detailed traces and metrics.")

if __name__ == "__main__":
    if not os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGSMITH_API_KEY") == "ls__your_key_here":
        print("⚠️  Warning: LANGSMITH_API_KEY is not set. Traces will not be uploaded.")
    
    if not os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY") == "your_openrouter_key_here":
        print("❌ Error: OPENROUTER_API_KEY is not set. Agent will fail.")
    else:
        run_evaluation()
