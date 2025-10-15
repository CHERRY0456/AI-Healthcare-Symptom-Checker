import os
import json
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ------------------------- CONFIG -------------------------
st.set_page_config(
    page_title="AI Healthcare Symptom Checker",
    layout="wide",
    page_icon="🩺"
)

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_KEY:
    st.warning("⚠️ OPENAI_API_KEY not found — the app will run in demo mode with fake responses.")
    client = None
else:
    client = OpenAI(api_key=OPENAI_KEY)

# ------------------------- CUSTOM CSS -------------------------
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fb;
            font-family: 'Segoe UI', sans-serif;
        }
        .title {
            color: #3A86FF;
            font-size: 2.2rem;
            font-weight: 700;
        }
        .subtitle {
            color: #555;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        .condition-card {
            background-color: white;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 10px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
        }
        .disclaimer {
            background-color: #FFF3CD;
            padding: 0.8rem;
            border-radius: 10px;
            border: 1px solid #FFEEBA;
            color: #856404;
            margin-top: 20px;
        }
        .footer {
            text-align: center;
            color: #888;
            margin-top: 2rem;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------- TITLE -------------------------
st.markdown("<h1 class='title'>🩺 Healthcare Symptom Checker</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Enter your symptoms to get possible conditions and next steps.<br>"
            "⚠️ For educational purposes only — not a medical diagnosis.</p>", unsafe_allow_html=True)


# ------------------------- LLM FUNCTION -------------------------
def get_condition_analysis(symptoms_text: str):
    """
    Queries GPT model to return structured JSON of conditions + next steps.
    """
    if not client:
        # demo mode fallback
        return {
            "conditions": [
                {"name": "Common Cold", "rationale": "Mild fever, runny nose, and sore throat match viral cold.", "confidence": 0.6, "urgency": "low"},
                {"name": "Allergic Rhinitis", "rationale": "Seasonal runny nose without severe fever suggests allergy.", "confidence": 0.25, "urgency": "low"},
                {"name": "Influenza", "rationale": "Fatigue and body aches suggest flu-like infection.", "confidence": 0.15, "urgency": "medium"}
            ],
            "next_steps": [
                "Stay hydrated and rest adequately.",
                "Monitor temperature and symptoms daily.",
                "If high fever or breathing issues appear, see a doctor immediately."
            ],
            "disclaimer": "This is for educational purposes only and not a medical diagnosis. Please consult a qualified doctor."
        }

    prompt = f"""
You are a cautious AI medical assistant for educational use only.
Analyze the user's symptoms:
\"\"\"{symptoms_text}\"\"\"

1. Suggest top 3 *possible* conditions (non-diagnostic):
   - name
   - rationale
   - confidence (0-1)
   - urgency ("low", "medium", "high")
2. Suggest 3–5 next steps or precautions.
3. Always include the disclaimer:
"This is for educational purposes only and not a medical diagnosis. Please consult a qualified doctor."

Return strictly valid JSON:
{{
  "conditions": [{{"name": "...", "rationale": "...", "confidence": 0.0, "urgency": "..."}}],
  "next_steps": ["...", "..."],
  "disclaimer": "..."
}}
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a careful, medically-aware assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=700,
        )
        output = completion.choices[0].message.content.strip()
        import re
        match = re.search(r"\{.*\}", output, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            return {"raw": output}
    except Exception as e:
        return {"error": str(e)}


# ------------------------- SIDEBAR -------------------------
with st.sidebar:
    st.header("⚙️ Options")
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if st.button("🧹 Clear History"):
        st.session_state["history"] = []
        st.success("History cleared.")
    st.markdown("### Previous Queries")
    if len(st.session_state["history"]) == 0:
        st.write("No previous queries.")
    else:
        for i, h in enumerate(reversed(st.session_state["history"][-5:])):
            st.write(f"{i+1}. {h['symptoms'][:40]}...")

# ------------------------- MAIN BODY -------------------------
symptoms = st.text_area(
    "🩹 Describe your symptoms:",
    placeholder="Example: fever, sore throat, fatigue for 3 days, mild cough",
    height=140
)

col1, col2 = st.columns(2)
with col1:
    analyze = st.button("🔍 Analyze Symptoms", use_container_width=True)
with col2:
    demo = st.button("💡 Demo Example", use_container_width=True)

if demo:
    symptoms = "Fever, body aches, sore throat for 3 days, fatigue"

if analyze or demo:
    if not symptoms.strip():
        st.error("Please enter symptoms.")
    else:
        st.session_state.history.append({"symptoms": symptoms, "time": datetime.now().isoformat()})
        with st.spinner("Analyzing symptoms..."):
            result = get_condition_analysis(symptoms)

        if "error" in result:
            st.error("Model Error: " + result["error"])
        elif "conditions" in result:
            st.success("✅ Analysis Complete")

            st.subheader("Possible Conditions")
            for c in result["conditions"]:
                urgency_color = {"low": "#66BB6A", "medium": "#FFA726", "high": "#E53935"}.get(
                    c["urgency"].lower(), "#90A4AE"
                )
                st.markdown(
                    f"""
                    <div class='condition-card'>
                        <b>{c['name']}</b>  
                        <p><b>Rationale:</b> {c['rationale']}</p>
                        <p><b>Confidence:</b> {c['confidence']:.2f}</p>
                        <p><b>Urgency:</b> <span style='color:{urgency_color}'>{c['urgency'].capitalize()}</span></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.subheader("Recommended Next Steps")
            for step in result["next_steps"]:
                st.write("• " + step)

            st.markdown(f"<div class='disclaimer'>{result['disclaimer']}</div>", unsafe_allow_html=True)

        else:
            st.write(result.get("raw", "Unexpected model output."))

st.markdown("<div class='footer'>© 2025 Healthcare Symptom Checker — AI Educational Project</div>", unsafe_allow_html=True)
