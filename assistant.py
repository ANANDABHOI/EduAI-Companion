import streamlit as st
import cohere

def show_chatbot():
    # Initialize the Cohere client with API key from secrets
    try:
        co = cohere.Client(st.secrets["COHERE_API_KEY"])
    except Exception as e:
        st.error("Failed to initialize AI assistant. Please check configuration.")
        st.stop()
    
    st.header("AI Learning Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "Chatbot", "content": "How can I help you with your studies today?"}]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"].lower()):  # Streamlit uses lowercase roles
            st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("Ask me anything about your studies"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "User", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Format the conversation history for Cohere
                chat_history = [
                    {"role": msg["role"], "message": msg["content"]} 
                    for msg in st.session_state.messages[:-1]
                ]
                
                # Generate response using Cohere - UPDATED METHOD
                response = co.chat_stream(
                    message=prompt,
                    chat_history=chat_history
                )
                
                # Stream the response
                for chunk in response:
                    if chunk.event_type == "text-generation":
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "Chatbot", "content": full_response})
                
            except Exception as e:
                st.error(f"Error communicating with AI assistant: {e}")