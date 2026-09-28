import os
import streamlit as st
from google import genai
from google.genai import types

# Configure Page
st.set_page_config(
    page_title="EduGenie - AI Learning Assistant",
    page_icon="🎓",
    layout="wide"
)

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please set your GEMINI_API_KEY environment variable.")
    st.stop()

client = genai.Client(api_key=api_key)

# App Header
st.title("🎓 EduGenie")
st.caption("Your Gemini-Powered Personal Learning & Study Assistant")

# Sidebar for feature selection
mode = st.sidebar.selectbox(
    "Select Mode",
    [
        "Concept Explainer",
        "Generate Practice Quiz",
        "Summarize Study Notes",
        "Doubt Solver (Chat)"
    ]
)

# ----------------------------------------------------
# Mode 1: Concept Explainer
# ----------------------------------------------------
if mode == "Concept Explainer":
    st.subheader("💡 Learn Any Concept")
    
    topic = st.text_input("Enter a topic or concept:", placeholder="e.g., Backpropagation in Neural Networks")
    audience_level = st.select_slider(
        "Target understanding level:",
        options=["5-Year-Old (ELI5)", "High School Student", "Undergraduate", "Expert / Researcher"]
    )
    
    if st.button("Explain Concept", type="primary") and topic:
        with st.spinner("Generating explanation..."):
            prompt = (
                f"Explain the following concept: '{topic}'.\n"
                f"Target audience level: {audience_level}.\n"
                f"Structure your response with: "
                f"1. A simple intuitive analogy, "
                f"2. Core principles, "
                f"3. A real-world example, "
                f"4. A quick 1-question check for understanding."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.markdown(response.text)

# ----------------------------------------------------
# Mode 2: Generate Practice Quiz
# ----------------------------------------------------
elif mode == "Generate Practice Quiz":
    st.subheader("📝 Practice Quiz Generator")
    
    quiz_topic = st.text_input("Topic for the quiz:", placeholder="e.g., Photosynthesis")
    num_questions = st.slider("Number of questions:", min_value=1, max_value=10, value=3)
    
    if st.button("Create Quiz", type="primary") and quiz_topic:
        with st.spinner("Creating your quiz..."):
            prompt = (
                f"Create a {num_questions}-question multiple-choice quiz on '{quiz_topic}'.\n"
                f"For each question, list 4 options (A, B, C, D) and hide the correct answers "
                f"and brief explanations inside a collapsable markdown spoiler block labeled 'Answer & Explanation'."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.markdown(response.text)

# ----------------------------------------------------
# Mode 3: Summarize Study Notes
# ----------------------------------------------------
elif mode == "Summarize Study Notes":
    st.subheader("📑 Smart Notes Summarizer")
    
    notes_text = st.text_area("Paste your study text or lecture notes here:", height=200)
    
    if st.button("Generate Summary", type="primary") and notes_text:
        with st.spinner("Summarizing..."):
            prompt = (
                f"Analyze and summarize the following study notes:\n\n{notes_text}\n\n"
                f"Provide:\n"
                f"- **Key Takeaways** (3-5 bullet points)\n"
                f"- **Core Terminology & Definitions**\n"
                f"- **Potential Exam Questions**"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            st.markdown(response.text)

# ----------------------------------------------------
# Mode 4: Doubt Solver (Chat)
# ----------------------------------------------------
elif mode == "Doubt Solver (Chat)":
    st.subheader("💬 Interactive Tutor Chat")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if user_query := st.chat_input("Ask any academic question..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                system_instruction = (
                    "You are EduGenie, an encouraging, patient, and precise educational tutor. "
                    "Help students learn by breaking down complex problems step-by-step."
                )
                
                # Format conversation history
                formatted_contents = [
                    types.Content(
                        role="user" if m["role"] == "user" else "model",
                        parts=[types.Part.from_text(text=m["content"])]
                    )
                    for m in st.session_state.messages
                ]

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})