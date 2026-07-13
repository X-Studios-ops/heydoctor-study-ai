import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Heydoctor Study AI | Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 3rem; font-weight: 800; color: #4A90E2; margin-bottom: 0px; }
    .sub-title { font-size: 1.2rem; color: #7F8C8D; margin-top: -10px; margin-bottom: 20px; }
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4A90E2; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
# This keeps the app from resetting every time a button is clicked.
if "history" not in st.session_state:
    st.session_state.history = []
if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""
if "api_configured" not in st.session_state:
    st.session_state.api_configured = False

# ==========================================
# 3. API INITIALIZATION FUNCTION
# ==========================================
@st.cache_resource
def configure_api(api_key):
    try:
        genai.configure(api_key=api_key)
        # Using the advanced Flash model for speed and heavy lifting
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return None

# ==========================================
# 4. SIDEBAR: SETTINGS & PREFERENCES
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # Placeholder logo
    st.header("⚙️ App Settings")
    
    # API Key handling (Secrets first, then manual input fallback)
    api_key = None
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API Key loaded from Secrets!")
    else:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    
    if api_key:
        model = configure_api(api_key)
        if model:
            st.session_state.api_configured = True
        else:
            st.error("Invalid API Key.")
            
    st.markdown("---")
    st.header("🧠 Study Preferences")
    difficulty = st.select_slider("Select Difficulty", options=["Beginner (5th Grade)", "Intermediate (8th Grade)", "Advanced (College)"], value="Intermediate (8th Grade)")
    tone = st.selectbox("Tutor Personality", ["Encouraging & Fun", "Strict & Academic", "Socratic (Asks questions back)"])
    
    st.markdown("---")
    if st.button("🗑️ Clear Study History"):
        st.session_state.history = []
        st.success("History Cleared!")

# Stop execution if API is not set
if not st.session_state.api_configured:
    st.title("⚡ Heydoctor Study AI")
    st.warning("👈 Please provide your Gemini API Key in the sidebar to unlock the application.")
    st.stop()

# ==========================================
# 5. MAIN UI HEADER
# ==========================================
st.markdown('<p class="main-title">⚡ Heydoctor Study AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Engineered by Pratyush Ranjan Roul | Enterprise Edition</p>', unsafe_allow_html=True)

# Create layout tabs
tab1, tab2, tab3 = st.tabs(["📚 Core Study Modes", "📄 Document Analysis", "🕒 Study History"])

# ==========================================
# 6. TAB 1: CORE STUDY MODES (The Mega Engine)
# ==========================================
with tab1:
    st.markdown("### Choose Your Learning Path")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        mode = st.radio(
            "Select Tool:", 
            [
                "📝 Smart Notes", 
                "🧠 Deep Explanation", 
                "🎯 Interactive Quiz", 
                "💡 Flashcard Generator",
                "📅 Study Plan Builder"
            ]
        )
    
    with col2:
        topic = st.text_area("What are we conquering today?", placeholder="Enter a topic, concept, or paste a paragraph here...", height=130)

    if st.button("Generate Learning Module 🚀", use_container_width=True):
        if not topic:
            st.error("You need to provide a topic first!")
        else:
            with st.spinner(f"Heydoctor AI is crafting a module on '{topic}'..."):
                
                # Dynamic System Prompt Engineering
                base_prompt = f"""
                You are 'Heydoctor Study AI', an elite academic tutor created by Pratyush Ranjan Roul.
                Current Target Audience: {difficulty}.
                Tutor Tone: {tone}.
                
                Topic: "{topic}"
                """
                
                # Mode-Specific Logic
                if mode == "📝 Smart Notes":
                    task_prompt = """
                    Create visually appealing notes. Include:
                    1. Executive Summary (2 sentences).
                    2. Core Concepts (Bullet points).
                    3. Key Terminology/Formulas.
                    4. Pratyush's Memory Hack (A mnemonic or trick to remember this).
                    """
                elif mode == "🧠 Deep Explanation":
                    task_prompt = """
                    Explain this concept deeply. Include:
                    1. Step-by-Step Breakdown.
                    2. The 'Game/Sport' Analogy: Explain the hardest part using a relatable video game or sports analogy.
                    3. Real-World Applications (Where is this used?).
                    """
                elif mode == "🎯 Interactive Quiz":
                    task_prompt = """
                    Generate a test. Include:
                    1. 3 MCQs (with 4 options each).
                    2. 2 True/False questions with tricky nuances.
                    3. 1 Conceptual Essay Question.
                    Provide the Answer Key at the very bottom.
                    """
                elif mode == "💡 Flashcard Generator":
                    task_prompt = """
                    Create 5-7 high-yield flashcards. Format them clearly with:
                    **Front (Question/Term):** ...
                    **Back (Answer/Definition):** ...
                    """
                else: # Study Plan Builder
                    task_prompt = """
                    Create a 3-day micro-study plan to master this topic. Break down what to read, practice, and review on Day 1, Day 2, and Day 3.
                    """
                
                final_prompt = base_prompt + "\n\nTASK INSTRUCTIONS:\n" + task_prompt
                
                try:
                    response = model.generate_content(final_prompt)
                    
                    # Display Results
                    st.success("Module Generated Successfully!")
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Save to history
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.history.append({"time": timestamp, "topic": topic, "mode": mode, "content": response.text})
                    
                    # Download Button
                    st.download_button(
                        label="📥 Download this Study Module",
                        data=response.text,
                        file_name=f"{topic.replace(' ', '_')}_notes.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"API Error: {e}")

# ==========================================
# 7. TAB 2: DOCUMENT ANALYSIS (PDF Upload)
# ==========================================
with tab2:
    st.markdown("### 📄 Upload your School Notes or PDF")
    st.info("Upload a document, and Heydoctor AI will summarize it, extract key facts, or create a quiz based *only* on your document.")
    
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_file is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            st.session_state.uploaded_text = text
            st.success(f"Document uploaded successfully! Extracted {len(text)} characters.")
            
            doc_action = st.radio("What should I do with this document?", ["Summarize It", "Extract Key Terms", "Generate Quiz from Text"])
            
            if st.button("Process Document 🧠"):
                with st.spinner("Analyzing document..."):
                    doc_prompt = f"You are Heydoctor AI. Based ONLY on the following text, perform this task: {doc_action}.\n\nTEXT:\n{st.session_state.uploaded_text[:10000]}" # Limiting text length to avoid token limits
                    doc_response = model.generate_content(doc_prompt)
                    
                    st.markdown("### Document Analysis Result:")
                    st.markdown(doc_response.text)
                    
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")

# ==========================================
# 8. TAB 3: STUDY HISTORY LOG
# ==========================================
with tab3:
    st.markdown("### 🕒 Your Previous Sessions")
    if len(st.session_state.history) == 0:
        st.info("No study sessions recorded yet. Go generate some notes!")
    else:
        for i, session in enumerate(reversed(st.session_state.history)):
            with st.expander(f"Session {len(st.session_state.history)-i}: {session['topic']} ({session['mode']}) - {session['time']}"):
                st.markdown(session["content"])

# ==========================================
# 9. FOOTER
# ==========================================
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Designed with ❤️ by Pratyush Ranjan Roul | Heydoctor.ai Ecosystem | Pro Tier Architecture</p>", unsafe_allow_html=True)

