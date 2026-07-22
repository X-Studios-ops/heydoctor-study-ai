import streamlit as st
from openai import OpenAI
import fitz
import requests
import json
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
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4A90E2; margin-bottom: 15px; color: #000000; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []
if "api_keys" not in st.session_state:
    st.session_state.api_keys = []
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = [] # NAYA: Memory Storage

# ==========================================
# 3. OPENROUTER MULTIMODAL ENGINE
# ==========================================
def load_api_keys():
    keys = []
    try:
        if hasattr(st, "secrets"):
            for i in range(1, 4):
                key_name = f"GEMINI_API_KEY_{i}"
                if key_name in st.secrets:
                    val = st.secrets[key_name]
                    if isinstance(val, str) and val.strip():
                        keys.append(val.strip())
    except Exception:
        pass
    return keys

def encode_image(image):
    buffered = io.BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_with_rotation(prompt_data, available_keys):
    valid_keys = [k for k in available_keys if k and k.strip()]
    if not valid_keys:
        raise Exception("No valid API keys found! Check sidebar or secrets.")
    
    keys_to_try = valid_keys.copy()
    random.shuffle(keys_to_try)
    
    # SYSTEM PROMPT: AI ko strict rakhne aur memory ka context dene ke liye
    messages = [
        {"role": "system", "content": "You are 'Heydoctor AI', an elite study tutor created exclusively by Pratyush Ranjan Roul. Always maintain context of the conversation. If the user asks a follow-up question, answer it based on previous discussions. Make learning fun with epic analogies."}
    ]

    # MEMORY INJECTION: Aakhri 4 baatein yaad rakhna
    for msg in st.session_state.chat_memory[-4:]:
        messages.append(msg)

    # Naya Prompt set karna
    user_text = ""
    if isinstance(prompt_data, list):
        img = prompt_data[0]
        txt = prompt_data[1]
        user_text = txt
        base64_img = encode_image(img)
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": txt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
            ]
        })
    else:
        user_text = str(prompt_data)
        messages.append({"role": "user", "content": user_text})

    for attempt, key in enumerate(keys_to_try):
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=key,
                default_headers={
                    "HTTP-Referer": "https://heydoctor.ai",
                    "X-Title": "Heydoctor Study AI"
                }
            )
            
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash",  
                messages=messages,
                max_tokens=2000 
            )

            ai_answer = response.choices[0].message.content
            
            # MEMORY SAVE KARNA: Taaki agli baar yaad rahe
            st.session_state.chat_memory.append({"role": "user", "content": user_text})
            st.session_state.chat_memory.append({"role": "assistant", "content": ai_answer})
            
            return ai_answer
                
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
    if st.button("🗑️ Clear History & Memory"):
        st.session_state.history = []
        st.session_state.chat_memory = []
        st.success("History & Memory Cleared!")

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
                base_prompt = f"Target Level: {difficulty}. Tone: {tone}. Topic: '{topic}'\n\n"
                
                if mode == "📝 Make Notes":
                    base_prompt += "Provide high-yield notes: 1. Summary, 2. Core Points, 3. Memory Hack."
                elif mode == "🧠 Detail Explanation":
                    base_prompt += "Explain step-by-step. Include a relatable real-world analogy."
                elif mode == "🎯 Take a Test":
                    base_prompt += "Generate a quiz: 3 MCQs, 1 True/False, 1 Short Essay. Put answers at the bottom."
                else:
                    base_prompt += "Generate 5 flashcards formatted as Front: [Term] and Back: [Definition]."
                
                try:
                    response_text = generate_with_rotation(base_prompt, st.session_state.api_keys)
                    # NAYA UI FIX: Single f-string for perfect rendering
                    st.markdown(f'<div class="card">\n\n{response_text}\n\n</div>', unsafe_allow_html=True)
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
                img_prompt = f"Look at this uploaded image. {img_action}. Be clear, structured, and use Markdown formatting."
                
                try:
                    img_response = generate_with_rotation([image, img_prompt], st.session_state.api_keys)
                    # NAYA UI FIX
                    st.markdown(f'<div class="card">\n\n{img_response}\n\n</div>', unsafe_allow_html=True)
                    st.session_state.history.append({"time": datetime.now().strftime("%H:%M:%S"), "title": f"Photo Analysis: {img_action}", "content": img_response})
                except Exception as e:
                    st.error(f"Vision Analysis Failed: {e}")

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
