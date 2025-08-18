import streamlit as st
import pandas as pd
import pickle
import json
import os

def show_recommendation():
    """
    Display personalized learning recommendations using file upload only
    """
    st.header("Your Personalized Learning Path")
    
    # Load course materials
    try:
        with open("course_material.json") as f:
            course_data = json.load(f)
    except Exception as e:
        st.error(f"Failed to load course materials: {e}")
        return
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your learning progress (CSV)", type="csv")
    
    if uploaded_file:
        try:
            # Load and display data
            df = pd.read_csv(uploaded_file)
            st.success("Data loaded successfully!")
            st.dataframe(df.head())
            
            # Generate recommendations
            generate_recommendations(df, course_data)
            
        except Exception as e:
            st.error(f"Error processing file: {e}")

def generate_recommendations(df, course_data):
    """
    Generate recommendations using either ML model or fallback method
    """
    # Check if model file exists
    model_path = "models/rec_model.pkl"
    
    if os.path.exists(model_path):
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            
            # Check for required columns for ML model
            required_cols = ['math_score', 'science_score', 'english_score', 'attendance_rate']
            if all(col in df.columns for col in required_cols):
                prediction = model.predict(df[required_cols])
                
                # Display recommendation
                st.subheader("Recommended Learning Path (AI Model)")
                level = prediction[0]
                display_recommendation(level, course_data)
                return
            else:
                st.error(f"For best results, CSV should contain: {', '.join(required_cols)}")
                st.info("Using fallback recommendation system")
                
        except Exception as e:
            st.error(f"Error in model prediction: {e}")
            st.info("Using fallback recommendation system")
    
    # Fallback to basic analysis if ML model fails or doesn't exist
    fallback_recommendation(df, course_data)

def display_recommendation(level, course_data):
    """Display recommendations based on level"""
    st.success(f"Your level: {course_data[str(level)]['level']}")
    st.write("Recommended topics:")
    for topic in course_data[str(level)]['recommended_topics']:
        st.write(f"- {topic}")

def fallback_recommendation(df, course_data):
    """Fallback recommendation based on average scores"""
    try:
        st.subheader("Recommended Learning Path (Basic Analysis)")
        
        if 'math_score' in df.columns and 'science_score' in df.columns and 'english_score' in df.columns:
            avg_score = df[['math_score', 'science_score', 'english_score']].mean().mean()
            
            if avg_score >= 75:
                level = 0  # Advanced
            elif avg_score >= 50:
                level = 1  # Intermediate
            else:
                level = 2  # Beginner
                
            display_recommendation(level, course_data)
        else:
            st.warning("Using default beginner recommendations")
            display_recommendation(2, course_data)  # Default to beginner
            
    except Exception as e:
        st.error(f"Error in fallback recommendation: {e}")
        st.warning("Using default beginner recommendations")
        display_recommendation(2, course_data)  # Default to beginner