import streamlit as st
import requests

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="RGMCET College Assistant",
    page_icon="🎓",
    layout="centered",
)

# ---------------- COLLEGE KNOWLEDGE ----------------
# Starter guidance only. Verify and update official details before production use.
COLLEGE_KNOWLEDGE = """
College: Rajeev Gandhi Memorial College of Engineering and Technology
(RGMCET), Nandyal, Andhra Pradesh, India.

Official website: https://www.rgmcet.edu.in/
Admission procedures: https://www.rgmcet.edu.in/admission-procedures
Fee structure: https://www.rgmcet.edu.in/feestructure
Scholarships: https://www.rgmcet.edu.in/scholarship
Admission application: https://administration.rgmcet.edu.in/Admission_Application.php

ADMISSIONS:
- Admission procedures depend on the programme and current official rules.
- B.Tech convener admissions may use entrance-exam rank and counselling,
  according to current applicable rules.
- Category-B admissions follow applicable official procedures.
- Eligibility, seat availability, cutoffs, dates and required documents can change.
- Never guarantee admission based on rank alone.
- For lateral-entry admissions, students should verify the current ECET and
  applicable counselling rules with the official authority.

FEES AND SCHOLARSHIPS:
- Fee amounts can change by academic year and admission category.
- Tuition, hostel, transport, examination and other charges may differ.
- Confirm current scholarship and fee-reimbursement rules with the college
  and relevant government authority.

OTHER TOPICS:
- Courses and departments
- Required admission documents
- Hostel and transport facilities
- Placement information
- College address and contact details

If exact current information is not supplied here, direct the student to
the relevant official page or college office. Do not invent fees, deadlines,
cutoffs, phone numbers, placement statistics or admission guarantees.
"""

SYSTEM_PROMPT = f"""
You are a helpful college enquiry assistant for RGMCET, Nandyal, Andhra Pradesh.

Use simple English and answer the student's actual question directly.
Use the conversation history to understand follow-up questions.
Explain admission procedures in clear steps when possible.
Distinguish general guidance from confirmed college-specific facts.
Never invent current fees, deadlines, cutoffs, eligibility rules, seat availability,
phone numbers, statistics or admission guarantees.
When information is missing, say what needs confirmation and provide the most
relevant official link listed below.

COLLEGE REFERENCE INFORMATION:
{COLLEGE_KNOWLEDGE}

Useful links:
- College website: https://www.rgmcet.edu.in/
- Admission procedures: https://www.rgmcet.edu.in/admission-procedures
- Fee structure: https://www.rgmcet.edu.in/feestructure
- Scholarships: https://www.rgmcet.edu.in/scholarship
- Admission application: https://administration.rgmcet.edu.in/Admission_Application.php

Do not claim you have visited or checked a website live. The supplied information
is reference context, not a live database.
"""

# ---------------- API KEY ----------------
try:
    API_KEY = st.secrets["OPENROUTER_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "OpenRouter API key not found. Create "
        ".streamlit/secrets.toml and add "
        'OPENROUTER_API_KEY = "your_actual_key".'
    )
    st.stop()

# Replace this with a model ID currently available to your OpenRouter account.
MODEL = "openai/gpt-4o-mini"

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ---------------- HEADER ----------------
st.title("🎓 RGMCET College Assistant")
st.write(
    "Ask about admissions, eligibility, courses, fees, scholarships, "
    "hostel facilities and placements."
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Explore the college")
    st.caption("Choose a topic or type your own question.")

    if st.button("📚 Courses", use_container_width=True):
        st.session_state.pending_question = "What courses are available at RGMCET?"

    if st.button("📝 Admissions", use_container_width=True):
        st.session_state.pending_question = "How can I get admission into B.Tech at RGMCET?"

    if st.button("💰 Fees and scholarships", use_container_width=True):
        st.session_state.pending_question = "How can I find the current fee structure and scholarships?"

    if st.button("🏠 Hostel facilities", use_container_width=True):
        st.session_state.pending_question = "What should I know about hostel facilities?"

    if st.button("💼 Placements", use_container_width=True):
        st.session_state.pending_question = "Where can I find verified placement information?"

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

# ---------------- DISPLAY EXISTING CHAT ONCE ----------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- QUESTION INPUT ----------------
typed_question = st.chat_input("Type your college question...")
question = typed_question

# Sidebar buttons set a pending question; process it on this rerun.
if not question and st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

# ---------------- PROCESS QUESTION ----------------
if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Preparing your answer..."):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *st.session_state.messages[-12:],
                        ],
                        "temperature": 0.2,
                    },
                    timeout=60,
                )

                if response.status_code != 200:
                    st.error(
                        f"OpenRouter API error ({response.status_code}): "
                        f"{response.text[:500]}"
                    )
                else:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip()
                    st.markdown(answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

            except requests.RequestException as error:
                st.error(f"Could not connect to OpenRouter: {error}")
            except (KeyError, IndexError, ValueError):
                st.error(
                    "The AI service returned an unexpected response. "
                    "Check the selected model and API settings."
                )
