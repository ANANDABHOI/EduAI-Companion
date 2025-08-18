import streamlit as st
from assistant import show_chatbot
from cheat_detector import show_exam
from recomend import show_recommendation

# Basic page configuration
st.set_page_config(
    page_title="EduAI Companion",
    page_icon="📚"
)

def show_home():
    st.title("EduAI Companion")
    st.write("Your personal learning assistant")
    st.markdown("---")
    
    # Simple features list without icons
    st.subheader("Features")
    st.write("- Personalized Study Plans")
    st.write("- 24/7 AI Tutor")
    st.write("- Progress Tracking")
    st.write("- Secure Exam Proctoring")

def show_main_app():
    """Minimal main application"""
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox(
        "Navigate to",
        ["Home", "Learning Recommendations", "AI Tutor", "Exam Center"]
    )
    
    if page == "Home":
        show_home()
    elif page == "Learning Recommendations":
        show_recommendation()
    elif page == "AI Tutor":
        show_chatbot()
    elif page == "Exam Center":
        show_exam()

if __name__ == "__main__":
    show_main_app()