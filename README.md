# Healthcare Symptom Checker

**Author:** Jai Sri Charan 
**Built With:** Streamlit • Python • OpenAI GPT-4o • dotenv  
**Tags:** LLM • Healthcare AI • Responsible AI • Educational Tool  

---

### Objective
A **Streamlit-based AI web app** that analyzes user-entered symptoms to provide **possible conditions** and **safe next steps** — powered by an **LLM backend** with a **rule-based fallback** for offline or quota-limited usage.

> ⚠️ **Disclaimer:** This tool is for educational use only and does *not* provide a medical diagnosis. Always consult a qualified healthcare professional.

---

### 🧩 Key Features
- 🤖 **LLM Reasoning (GPT-4o)** — Generates structured JSON with top 3 conditions, confidence & urgency.  
- 💾 **Local Fallback Engine** — Works even without an API key via deterministic symptom analysis.  
- 🩹 **Confidence + Urgency Visualization** — Clear color-coded output for better readability.  
- 🕓 **Query History** — Save and review recent symptom checks in session state.  
- 🔒 **API Security** — Uses `.env` file with `python-dotenv` for protected key handling.  
- 🖥️ **Modern UI** — Responsive Streamlit interface with custom CSS and disclaimers.

---

### ⚙️ Tech Stack
| Layer | Technology |
|-------|-------------|
| Frontend | Streamlit (Python) |
| Backend | Python + OpenAI API |
| Environment | dotenv |
| Fallback Engine | Rule-based deterministic analyzer |
| Storage | Session state (SQLite optional) |

---

### 🏗️ Architecture
User
│
▼
[Streamlit UI]
│ ├─ Text input (symptoms)
│ └─ Display results (conditions, steps, disclaimer)
│
▼
[Backend Logic]
│
├─ If API Key present → [OpenAI GPT-4o LLM]
│ │
│ └─ JSON: {conditions[], next_steps[], disclaimer}
│
└─ Else → [Local Rule-Based Analyzer]
└─ Deterministic conditions + steps
│
▼
[Result Renderer]
├─ Save to history
└─ Display disclaimer

##check the diagram also

---

### 🏁 Setup Instructions

```bash
# 1️⃣ Clone the repo
git clone https://github.com/<your-username>/Healthcare-Symptom-Checker.git
cd Healthcare-Symptom-Checker

# 2️⃣ Create & activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Add OpenAI API key (optional)
# Create a file named .env in project root
OPENAI_API_KEY=your_openai_api_key_here

# 5️⃣ Run the app
streamlit run streamlit_app.py

Example Input

“Sore throat and mild fever for 3 days, fatigue, no chest pain.”

Example Output:

Condition 1: Common Cold (Confidence 0.65 | Urgency Low)

Condition 2: Influenza (Confidence 0.55 | Urgency Medium)

Condition 3: Allergic Rhinitis (Confidence 0.45 | Urgency Low)

Next Steps: Rest • Hydration • Monitor Symptoms • Consult if worsens

Future Enhancements

🗣️ Voice Input via streamlit-mic-recorder

📍 Doctor Finder using Google Maps API

🧾 Export reports to PDF

💬 Chat mode for multi-turn queries

🗂️ SQLite-based persistent history

