# streamlit_app.py
import os
import json
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Attempt to import new OpenAI client; if not available, we'll still run in demo mode.
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Healthcare Symptom Checker", layout="wide", page_icon="🩺")
load_dotenv()

# ---------------- UI CSS ----------------
st.markdown("""
    <style>
        .title { color: #2563eb; font-size: 2.1rem; font-weight:700; }
        .subtitle { color: #444; margin-bottom: 1rem; }
        .condition-card { background:#fff; padding:12px; border-radius:8px; box-shadow: 0 3px 8px rgba(15,23,42,0.06); margin-bottom:10px; }
        .disclaimer { background:#fff3cd; padding:10px; border-radius:8px; border:1px solid #ffeeba; color:#856404; }
        .urgent { background:#ffebee; padding:10px; border-radius:8px; border:1px solid #f8c1c0; color:#b71c1c; }
        .footer { color:#777; text-align:center; margin-top:18px; font-size:0.9rem; }
    </style>
""", unsafe_allow_html=True)

# ---------------- Title ----------------
st.markdown("<div class='title'>🩺 Healthcare Symptom Checker</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Educational demo — suggests possible causes & next steps. Not a diagnosis.</div>", unsafe_allow_html=True)

# ---------------- OpenAI client setup ----------------
# Option A: hardcode key (only for local/demonstration; don't commit to git)
# OPENAI_KEY = "sk-REPLACE_WITH_YOUR_KEY"   # <-- you can uncomment and paste your key here temporarily

# Option B: use environment / .env
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")  # if empty -> demo mode

client = None
if OPENAI_KEY and OpenAI is not None:
    try:
        client = OpenAI(api_key=OPENAI_KEY)
    except Exception:
        client = None

# ---------------- Helper: robust wrapper ----------------
def call_openai_chat(messages, model="gpt-4o", temperature=0.2, max_tokens=700):
    """
    Safely call OpenAI v2 client if available. Returns the model text (string).
    If client missing or call fails, raises an exception.
    """
    if client is None:
        raise RuntimeError("OpenAI client not available")
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return resp.choices[0].message.content.strip()

# ---------------- Fallback: deterministic local analyzer (no API key needed) ----------------
def local_symptom_analyzer(symptoms_text: str):
    """
    Deterministic rule-based analysis that produces structured JSON:
    - top 3 conditions with rationale, confidence, urgency
    - next_steps list
    This is educational-only placeholder output for demo purposes.
    """
    text = symptoms_text.lower()
    conditions = []
    # simple heuristics, ordered by priority
    if any(k in text for k in ["shortness of breath", "breathless", "difficulty breathing", "cant breathe"]):
        conditions.append({"name":"Acute respiratory distress / serious respiratory issue", "rationale":"Presence of breathing difficulty is a red flag requiring urgent evaluation.","confidence":0.9,"urgency":"high"})
    if any(k in text for k in ["chest pain", "pressure in chest", "tightness in chest"]):
        conditions.append({"name":"Cardiac or chest emergency (angina / myocardial infarction)", "rationale":"Chest pain can indicate a heart-related emergency; immediate attention advised.","confidence":0.95,"urgency":"high"})
    # common cold / viral upper respiratory
    if any(k in text for k in ["sore throat", "runny nose", "sneezing", "stuffy nose", "nasal congestion"]) and ("fever" not in text or "low fever" in text or "mild fever" in text):
        conditions.append({"name":"Common cold (viral upper respiratory infection)", "rationale":"Upper airway symptoms like runny nose and sore throat without high fever commonly indicate a viral cold.","confidence":0.65,"urgency":"low"})
    # influenza
    if "fever" in text and any(k in text for k in ["body ache", "body aches", "high fever", "chills", "fatigue"]) :
        conditions.append({"name":"Influenza (flu)", "rationale":"Fever combined with body aches and fatigue suggests influenza-like illness.","confidence":0.55,"urgency":"medium"})
    # allergy
    if any(k in text for k in ["itchy eyes", "itchy", "watery eyes", "seasonal", "pollen", "sneezing"]) and "fever" not in text:
        conditions.append({"name":"Allergic rhinitis (allergy)", "rationale":"Itchy/watery eyes and sneezing without fever suggests allergy.","confidence":0.45,"urgency":"low"})
    # gastrointestinal
    if any(k in text for k in ["nausea", "vomit", "vomiting", "diarrhea", "abdominal pain"]):
        conditions.append({"name":"Gastrointestinal infection / gastroenteritis", "rationale":"GI symptoms like vomiting or diarrhea suggest a gastrointestinal infection or upset.","confidence":0.5,"urgency":"medium"})
    # if no conditions found, give a conservative generic set
    if not conditions:
        conditions = [
            {"name":"Viral infection (unspecified)", "rationale":"Symptoms could be due to a viral infection; more specific details would help.", "confidence":0.5, "urgency":"low"},
            {"name":"Allergic or inflammatory cause", "rationale":"Consider allergies or inflammation depending on triggers and timing.", "confidence":0.2, "urgency":"low"},
            {"name":"Further assessment recommended", "rationale":"If symptoms worsen or red flags appear, seek clinical evaluation.", "confidence":0.15, "urgency":"medium"},
        ]
    # trim to top 3 by confidence
    conditions = sorted(conditions, key=lambda x: x["confidence"], reverse=True)[:3]

    # Construct next steps conservatively
    next_steps = [
        "If any red flag is present (difficulty breathing, chest pain, fainting, severe bleeding), seek emergency care immediately.",
        "For mild symptoms: rest, hydration, OTC analgesics if needed, monitor symptoms for 48–72 hours.",
        "If symptoms worsen or persist beyond 7 days (or new severe symptoms appear), consult a healthcare provider."
    ]

    return {"conditions": conditions, "next_steps": next_steps,
            "disclaimer": "This is for educational purposes only and not a medical diagnosis. Consult a qualified healthcare professional for medical advice."}

# ---------------- Main app UI ----------------
col1, col2 = st.columns([2, 1])

with col1:
    symptoms = st.text_area("Describe your symptoms (include duration, severity, red flags):", height=180,
                            placeholder="e.g. sore throat, runny nose for 3 days, mild fever 100°F, no shortness of breath")
    st.write("Tip: include duration, severity, and any major medical history (asthma, heart disease).")

    submitted = st.button("Analyze symptoms")
    demo_btn = st.button("Use demo example")

with col2:
    st.markdown("### History")
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if st.button("Save last query"):
        if symptoms.strip():
            st.session_state.history.append({"time": datetime.now().isoformat(), "symptoms": symptoms})
            st.success("Saved to history.")
        else:
            st.info("No symptoms to save.")
    st.write("Recent:")
    for h in reversed(st.session_state.history[-6:]):
        st.write(f"- {h['time'].split('T')[0]} {h['time'].split('T')[1][:8]}: {h['symptoms'][:80]}")

# Demo example convenience
if demo_btn:
    symptoms = "Sore throat, runny nose for 3 days, mild fever 100.4°F, tiredness"
    st.experimental_rerun()

if submitted:
    if not symptoms.strip():
        st.error("Please enter symptoms first.")
    else:
        with st.spinner("Generating analysis..."):
            # If we have a client and a key, try to use real model safely
            result = None
            if client is not None:
                try:
                    # Build a careful system+user prompt that requests JSON
                    prompt = f"""
You are an educational medical assistant. The user gave these symptoms:
\"\"\"{symptoms}\"\"\"

1) Provide top 3 possible conditions (non-diagnostic) with name, rationale, confidence 0-1, urgency (low/medium/high).
2) Provide 3 next steps and urgent red-flag instructions.
3) Return ONLY valid JSON with keys: conditions, next_steps, disclaimer.
"""
                    messages = [
                        {"role": "system", "content": "You are a conservative, safety-first medical assistant for educational purposes."},
                        {"role": "user", "content": prompt}
                    ]
                    text = call_openai_chat(messages, model="gpt-4o")
                    # attempt to parse JSON out of output
                    import re
                    m = re.search(r"(\{.*\})", text, re.DOTALL)
                    if m:
                        result = json.loads(m.group(1))
                    else:
                        # not JSON -> fallback to raw text packaged
                        result = {"raw": text}
                except Exception as e:
                    # if any error calling live API, fallback to local deterministic analysis
                    result = {"note": f"OpenAI call failed: {str(e)}", **local_symptom_analyzer(symptoms)}
            else:
                # no API key/client -> use local deterministic analyzer
                result = local_symptom_analyzer(symptoms)

        # Display results
        if "raw" in result:
            st.warning("Model returned non-JSON text; showing raw output.")
            st.text(result["raw"])
        else:
            st.subheader("Possible conditions (educational only)")
            for c in result["conditions"]:
                color = {"low":"#16a34a","medium":"#f59e0b","high":"#ef4444"}.get(c.get("urgency","low").lower(),"#6b7280")
                st.markdown(f"""
                <div class='condition-card'>
                  <b>{c.get('name')}</b><br>
                  <small><b>Confidence:</b> {c.get('confidence',0):.2f}  —  <b>Urgency:</b> <span style='color:{color}'>{c.get('urgency','low').capitalize()}</span></small>
                  <p><b>Rationale:</b> {c.get('rationale')}</p>
                </div>
                """, unsafe_allow_html=True)

            st.subheader("Recommended next steps")
            for step in result["next_steps"]:
                st.write("• " + step)

            st.markdown(f"<div class='disclaimer'>{result.get('disclaimer')}</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>© 2025 Healthcare Symptom Checker — Educational demo - Developed by Charan</div>", unsafe_allow_html=True)
