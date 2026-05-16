# TrialMatch AI

An agentic pre-screening system that matches patients to clinical trials in minutes — not weeks.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Set your Anthropic API Key in `.env`:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

3. Run the FastAPI backend:
   ```bash
   uvicorn main:app --reload
   ```

4. In a new terminal, run the Streamlit UI:
   ```bash
   streamlit run ui/app.py
   ```

5. (Optional) Run Evaluation:
   ```bash
   python eval.py
   ```

## Demo Flow

1. **Load Patients:** Use the slider to select the number of synthetic patients and click "Generate Patients".
2. **Run Agent:** Click "Run Batch Screening". The LangGraph agent will:
   - De-identify patient data.
   - Evaluate eligibility against trial criteria using Claude 3.5 Sonnet.
   - Match eligible patients to the best clinical site based on geography and capacity.
   - Generate a coordinator-ready report.
3. **Review Results:** See the ranked table of matched patients, reasoning, and site assignments. Note the processing time to verify the "10x faster" claim.
4. **Export Report:** Use the download buttons in the UI to export results as JSON or CSV.
5. **Observability:** Check LangSmith for detailed traces and evaluation metrics.
