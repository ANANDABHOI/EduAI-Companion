import streamlit as st
import cv2
import time
import numpy as np
from datetime import datetime

def calculate_accuracy(answers, correct_answers):
    """Calculate accuracy score based on answers"""
    if not answers or not correct_answers:
        return 0
    
    correct_count = 0
    for user_ans, correct_ans in zip(answers, correct_answers):
        if user_ans and correct_ans and user_ans.lower().strip() == correct_ans.lower().strip():
            correct_count += 1
    return (correct_count / len(correct_answers)) * 100

def show_exam():
    st.header("Secure Exam Center")
    
    # Correct answers for the exam questions
    CORRECT_ANSWERS = [
        "paris",
        "5",
        "theory that explains how gravity works in the universe",
        "h2o",
        "harper lee"
    ]
    
    # Exam questions section
    st.subheader("Exam Questions")
    questions = [
        "1. What is the capital of France?",
        "2. Solve for x: 2x + 5 = 15",
        "3. Explain the theory of relativity in simple terms",
        "4. What is the chemical formula for water?",
        "5. Who wrote 'To Kill a Mockingbird'?"
    ]
    
    # Initialize session state
    if 'exam_state' not in st.session_state:
        st.session_state.exam_state = {
            'started': False,
            'submitted': False,
            'terminated': False,
            'answers': [""] * len(questions),
            'start_time': None,
            'warning_count': 0,
            'submit_clicked': False
        }

    # Display questions and collect answers
    for i, question in enumerate(questions):
        st.write(question)
        st.session_state.exam_state['answers'][i] = st.text_area(
            f"Answer for question {i+1}",
            value=st.session_state.exam_state['answers'][i],
            key=f"question_{i}"
        )

    # Exam monitoring agreement
    if not st.session_state.exam_state['started'] and not st.session_state.exam_state['submitted']:
        if st.checkbox("I agree to the monitoring conditions", key="monitoring_agreement"):
            st.session_state.exam_state['started'] = True
            st.session_state.exam_state['start_time'] = time.time()
            st.rerun()

    # Main exam section
    if st.session_state.exam_state['started'] and not st.session_state.exam_state['submitted']:
        st.subheader("Exam Monitoring")
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Create placeholders
        frame_placeholder = st.empty()
        time_placeholder = st.empty()
        warning_placeholder = st.empty()
        submit_placeholder = st.empty()
        
        exam_duration = 600  # 10 minutes
        max_warnings = 3
        
        try:
            # Only create the submit button once
            if submit_placeholder.button("Submit Exam", key="unique_submit_button"):
                st.session_state.exam_state['submit_clicked'] = True
                st.session_state.exam_state['submitted'] = True
                st.rerun()

            while True:
                if st.session_state.exam_state['submit_clicked']:
                    break
                    
                current_time = time.time()
                elapsed = current_time - st.session_state.exam_state['start_time']
                remaining = max(0, exam_duration - elapsed)
                
                # Update timer
                mins, secs = divmod(int(remaining), 60)
                time_placeholder.write(f"Time remaining: {mins}:{secs:02d}")
                
                # Check for time expiration
                if remaining <= 0:
                    st.session_state.exam_state['submitted'] = True
                    st.warning("Time's up! Your exam has been automatically submitted.")
                    break
                
                # Process camera frame
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to access camera")
                    break
                
                # Face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) == 0:
                    warning_text = "WARNING: Face not detected! Look directly at the camera."
                    warning_placeholder.warning(warning_text)
                    st.session_state.exam_state['warning_count'] += 1
                    
                    if st.session_state.exam_state['warning_count'] >= max_warnings:
                        st.error("Exam terminated due to multiple face detection violations!")
                        st.session_state.exam_state['submitted'] = True
                        st.session_state.exam_state['terminated'] = True
                        break
                else:
                    st.session_state.exam_state['warning_count'] = 0
                    warning_placeholder.empty()
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Display frame
                frame_placeholder.image(frame, channels="BGR")
                
                time.sleep(0.2)
                
        finally:
            cap.release()
            cv2.destroyAllWindows()
            frame_placeholder.empty()

    # Show results if exam is submitted
    if st.session_state.exam_state['submitted'] and not st.session_state.exam_state['terminated']:
        accuracy = calculate_accuracy(st.session_state.exam_state['answers'], CORRECT_ANSWERS)
        st.subheader("Exam Results")
        st.metric("Accuracy Score", f"{accuracy:.1f}%")
        
        st.subheader("Correct Answers")
        for i, (question, correct_answer) in enumerate(zip(questions, CORRECT_ANSWERS)):
            st.write(f"{question}")
            st.info(f"Correct answer: {correct_answer}")
            if st.session_state.exam_state['answers'][i]:
                if st.session_state.exam_state['answers'][i].lower().strip() == correct_answer.lower().strip():
                    st.success("Your answer was correct!")
                else:
                    st.error(f"Your answer: {st.session_state.exam_state['answers'][i]}")