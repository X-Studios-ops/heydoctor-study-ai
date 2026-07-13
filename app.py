import streamlit as st

st.title("🛠️ Heydoctor Diagnostic Test")

# Check 1: Package Test
try:
    from google import genai
    st.success("✅ SDK PASS: Naya 'google-genai' package properly installed hai!")
except ImportError:
    st.error("❌ SDK FAIL: Streamlit abhi bhi purane package pe atka hai. Naya SDK install nahi hua.")

# Check 2: API & Model Test
test_key = st.text_input("Apni 'AQ.' wali nayi API key yahan daal:", type="password")

if st.button("Test Model 🚀"):
    if test_key:
        try:
            client = genai.Client(api_key=test_key)
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents="Say 'Hello, systems are online!'"
            )
            st.success(f"✅ API PASS! AI Response: {response.text}")
        except Exception as e:
            st.error(f"❌ API ERROR: {e}")
    else:
        st.warning("Pehle key daal bhai!")

