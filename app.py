import streamlit as st
from openai import OpenAI
import PyPDF2
from PIL import Image
import random
from datetime import datetime
import base64
import io

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Heydoctor Study AI | Ultimate", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 3rem; font-weight: 800; color: #4A90E2; margin-bottom: 0px; }
    .sub-title { font-size: 1.2rem; color: #7F8C8D; margin-top: -10px; margin-bottom: 20px; }
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4A90E2; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []
if "api_keys" not in st.session_state:
    st.session_state.api_keys = []

# ==========================================
# 3. OPENROUTER MULTIMODAL ENGINE (Robust Auth)
# ==========================================
def load_api_keys():
    keys = []
    try:
        if hasattr(st, "secrets"):
            for i in range(1, 4):
                key_name = f"GEMINI_API_KEY_{i}"
                if key_name in st.secrets:
                    val = st.secrets[key_name]
                    # Filter: Sirf asli keys ko aage badhne do, spaces remove karo
                    if isinstance(val, str) and val.strip():
                        keys.append(val.strip())
    except Exception:
        pass
    return keys

# OpenRouter ke liye image ko Base64 me convert karna
def encode_image(image):
    buffered = io.BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_with_rotation(prompt_data, available_keys):
    """
    Handles text and image prompts using OpenRouter (OpenAI SDK).
    """
    valid_keys = [k for k in available_keys if k and k.strip()]
    if not valid_keys:
        raise Exception("No valid API keys found! Check sidebar or secrets.")
    
    keys_to_try = valid_keys.copy()
    random.shuffle(keys_to_try)
    
    # Text vs Image Payload Formatting
    messages = []
    if isinstance(prompt_data, list):
        # Multimodal (Photo Analysis)
        img = prompt_data[0]
        txt = prompt_data[1]
        base64_img = encode_image(img)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": txt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                    }
                ]
            }
        ]
    else:
        # Text Only
        messages = [{"role": "user", "content": str(prompt_data)}]

    for attempt, key in enumerate(keys_to_try):
        try:
            # 🚀 OPENROUTER CLIENT + HEADERS
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=key,
                default_headers={
                    "HTTP-Referer": "https://heydoctor.ai",
                    "X-Title": "Heydoctor Study AI"
                }
            )
            
            # Use the FREE Gemini 2.0 Flash Lite model on OpenRouter
                        # Naya aur stable OpenRouter model ID
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash",  
                messages=messages
            )


            
            return response.choices[0].message.content
                
        except Exception as e:
            st.toast(f"⚠️ Key {attempt + 1} failed. Switching...", icon="🔄")
            if attempt == len(keys_to_try) - 1:
                raise Exception(f"Error: {e}")
            continue

if not st.session_state.api_keys:
    st.session_state.api_keys = load_api_keys()

# ==========================================
# 4. SIDEBAR: SETTINGS & PREFERENCES
# ==========================================
with st.sidebar:
    st.title("⚡ Heydoctor AI")
    st.header("⚙️ Settings")
    
    if st.session_state.api_keys:
        st.success(f"✅ {len(st.session_state.api_keys)} API Keys Active!")
    else:
        st.error("⚠️ No API Keys found!")
        fallback_key = st.text_input("Enter OpenRouter API Key", type="password")
        if fallback_key:
            st.session_state.api_keys = [fallback_key]
            st.rerun()
            
    st.markdown("---")
    st.header("🧠 Difficulty Engine")
    difficulty = st.select_slider("Select Level", options=["Beginner (5th Grade)", "Intermediate (8th Grade)", "Advanced (College)"], value="Intermediate (8th Grade)")
    tone = st.selectbox("Tutor Tone", ["Friendly & Encouraging", "Strict & To the Point", "Gaming/Sports Nerd"])
    
    st.markdown("---")
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.success("History Cleared!")

if not st.session_state.api_keys:
    st.markdown('<p class="main-title">⚡ Heydoctor Study AI</p>', unsafe_allow_html=True)
    st.warning("👈 Please configure your OpenRouter API key in the sidebar to start.")
    st.stop()

# ==========================================
# 5. MAIN UI HEADER & TABS
# ==========================================
st.markdown('<p class="main-title">⚡ Heydoctor Study AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">The Ultimate Learning Super-App | Powered by OpenRouter</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📚 Learn Topic", "📸 Photo Analysis", "📄 PDF Analysis", "🕒 History"])

# ==========================================
# TAB 1: CORE STUDY MODES (TEXT)
# ==========================================
with tab1:
    st.markdown("### 🔍 Search & Generate")
    col1, col2 = st.columns([1, 2])
    with col1:
        mode = st.radio("Select Tool:", ["📝 Make Notes", "🧠 Detail Explanation", "🎯 Take a Test", "💡 Flashcards"])
    with col2:
        topic = st.text_area("What topic do you want to master?", placeholder="e.g., Photosynthesis, Newton's Laws...", height=110)

    if st.button("Generate! 🚀", key="btn_text_gen"):
        if topic:
            with st.spinner("Processing with OpenRouter..."):
                base_prompt = f"Act as 'Heydoctor AI', an elite tutor built by Pratyush Ranjan Roul. Target Level: {difficulty}. Tone: {tone}. Topic: '{topic}'\n\n"
                
                if mode == "📝 Make Notes":
                    base_prompt += "Provide high-yield notes: 1. Summary, 2. Core Points, 3. Memory Hack."
                elif mode == "🧠 Detail Explanation":
                    base_prompt += "Explain step-by-step. Include a relatable real-world or video game analogy for the hardest part."
                elif mode == "🎯 Take a Test":
                    base_prompt += "Generate a quiz: 3 MCQs, 1 True/False, 1 Short Essay. Put answers at the bottom."
                else:
                    base_prompt += "Generate 5 flashcards formatted as Front: [Term] and Back: [Definition]."
                
                try:
                    response_text = generate_with_rotation(base_prompt, st.session_state.api_keys)
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(response_text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.session_state.history.append({"time": datetime.now().strftime("%H:%M:%S"), "title": f"{mode}: {topic[:20]}", "content": response_text})
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Enter a topic first!")

# ==========================================
# TAB 2: PHOTO ANALYSIS ENGINE (VISION)
# ==========================================
with tab2:
    st.markdown("### 📸 Upload a Photo")
    st.info("Upload a diagram, a textbook page, or a math problem. Heydoctor AI will use its Vision capabilities to read it!")
    
    uploaded_img = st.file_uploader("Upload Image (JPG/PNG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_img:
        image = Image.open(uploaded_img)
        st.image(image, caption="Uploaded Image", width=400)
        
        img_action = st.radio("What should I do with this photo?", ["🧠 Explain this Diagram", "🧮 Solve this Problem", "📝 Make Notes from this Text/Page"])
        
        if st.button("Scan & Process Photo 🔍"):
            with st.spinner("Heydoctor AI's Vision Engine is scanning your image..."):
                img_prompt = f"Act as Heydoctor AI (Target: {difficulty}). Look at this uploaded image. {img_action}. Be clear, structured, and use Markdown formatting."
                
                try:
                    # Payload must be [image, text] for our new OpenRouter function
                    img_response = generate_with_rotation([image, img_prompt], st.session_state.api_keys)
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(img_response)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.session_state.history.append({"time": datetime.now().strftime("%H:%M:%S"), "title": f"Photo Analysis: {img_action}", "content": img_response})
                except Exception as e:
                    st.error(f"Vision Analysis Failed: {e}")

# ==========================================
# TAB 3: PDF DOCUMENT ANALYSIS
# ==========================================
with tab3:
    st.markdown("### 📄 Upload PDF Notes")
    uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_pdf:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            pdf_text = "".join(page.extract_text() for page in pdf_reader.pages)
            st.success(f"PDF read successfully! ({len(pdf_text)} characters)")
            
            pdf_action = st.radio("What to do with PDF?", ["📝 Summarize into Notes", "🎯 Generate a Test from this PDF"])
            
            if st.button("Process PDF 📑"):
                with st.spinner("Analyzing PDF content..."):
                    pdf_prompt = f"Act as Heydoctor AI. Based strictly on the following text, {pdf_action}:\n\n{pdf_text[:12000]}" 
                    try:
                        pdf_response = generate_with_rotation(pdf_prompt, st.session_state.api_keys)
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(pdf_response)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.session_state.history.append({"time": datetime.now().strftime("%H:%M:%S"), "title": f"PDF: {pdf_action}", "content": pdf_response})
                    except Exception as e:
                        st.error(f"Analysis Failed: {e}")
        except Exception as e:
            st.error(f"PDF Error: {e}")

# ==========================================
# TAB 4: STUDY HISTORY LOG
# ==========================================
with tab4:
    st.markdown("### 🕒 Your Saved Sessions")
    if not st.session_state.history:
        st.info("No study sessions recorded yet. Start generating!")
    else:
        for i, session in enumerate(reversed(st.session_state.history)):
            with st.expander(f"[{session['time']}] {session['title']}"):
                st.markdown(session["content"])

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Built with ❤️ by Pratyush Ranjan Roul | Heydoctor.ai Multi-Modal Ecosystem</p>", unsafe_allow_html=True)

