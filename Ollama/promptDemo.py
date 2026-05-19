import streamlit as st
import ollama

st.title("Vikash Prompt")
prompt = st.text_area(label ="Write your prompt")
button = st.button("Okay")

if button:
    if prompt: 
        ##response = ollama.generate(model='gemma:latest',prompt=prompt)       
        response = ollama.generate(model='smollm2:latest',prompt=prompt)
        st.markdown(response["response"])        
