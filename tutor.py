import streamlit as st

# Sample MCQ data

import os
import streamlit as st
import openai
import requests
import json
import streamlit as st
from PIL import Image
import pytesseract
import cv2
import numpy as np
# Set your OpenAI API key
openai.api_key = os.getenv("openaikey")
chatgpt_url = "https://api.openai.com/v1/chat/completions"

chatgpt_headers = {
    "content-type": "application/json",
    "Authorization":"Bearer {}".format(os.getenv("openaikey"))}

def generate_mcq(paragraph,url,headers,prompt):
    
    # Define the payload for the chat model
    messages = [
        {"role": "system", "content": """You are an expert In generating multiple choice questions from given paragraph and provide answer. strictly Follow the given json Format as output
        
        [{
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "answer": "Paris"
	    },
	    {
		"question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Mars"
    		},]
        ,"""},
        {"role": "user", "content": paragraph}
    ]

    chatgpt_payload = {
        "model": "gpt-3.5-turbo-16k",
        "messages": messages,
        "temperature": 1.3,
        "max_tokens": 2000,
        "top_p": 1,
        "stop": ["###"]
    }

    # Make the request to OpenAI's API
    response = requests.post(url, json=chatgpt_payload, headers=headers)
    response_json = response.json()
    #st.write(response_json)
    # Extract data from the API's response
    #st.write(response_json)
    output = response_json['choices'][0]['message']['content']
    return output


# Function to display MCQs and get answers
tab1, tab2, tab3 = st.tabs(["Content", "MCQ", "Feedback"])
answers=[]
submitted=""
# Initialize session state for responses

        
        
def display_mcqs(mcqs_json):
    # Create a form
    with st.form(key='questions_form'):
        # Temporary list to hold current form responses
        current_responses = [st.radio(q["question"], q["options"], key=f"question_{i}") for i, q in enumerate(mcqs_json)]

        # Submit button for the form
        submitted = st.form_submit_button('Submit')

    return submitted, current_responses
    
    
def feedback(questions,original_answers,student_answers,url,headers):
    outputs=[]
	# Define the payload for the chat model
    for id,data in enumerate(questions):
            messages = [
		{"role": "system", "content": """You are an expert in evaluating student responses for questions and gives them the feeedback on mistakes.I Will provide questions and original answers along with student responses.compare original_answers and student_answers and mention if they are correct or wrong and give explanation on the topic
		""",
		"role": "user", "content": f"{questions[id]},{original_answers[id]},{student_answers[id]}"}
	    ]

            chatgpt_payload = {
		"model": "gpt-3.5-turbo-16k",
		"messages": messages,
		"temperature": 1.3,
		"max_tokens": 2000,
		"top_p": 1,
		"stop": ["###"]
	    }

	    # Make the request to OpenAI's API
            print(questions,original_answers,student_answers)
            response = requests.post(url, json=chatgpt_payload, headers=headers)
            response_json = response.json()
            #st.write(response_json)
	    # Extract data from the API's response
	    #st.write(response_json)
            output = response_json['choices'][0]['message']['content']
            outputs.append(output)
    return outputs
with tab1:
    paragraph, prompt = None, None
    uploaded_image = st.file_uploader("Upload an image...", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        text = extract_text(image)
        paragraph = st.text_area("Enter a paragraph:", text, height=200)

    if not uploaded_image:
        paragraph = st.text_area("Enter a paragraph:", height=200)

    if st.button("Generate MCQs"):
        if paragraph:
            mcqs = generate_mcq(paragraph, chatgpt_url, chatgpt_headers, prompt)
            st.session_state.mcqs = mcqs
            st.write("Question Generated Go to MCQ Tab for Questions")
        else:
            st.write("Please enter a paragraph to generate questions.")

with tab2:
    if 'mcqs' in st.session_state and st.session_state.mcqs:
        print(st.session_state.mcqs)
        mcqs_json = json.loads(st.session_state.mcqs)
        submitted, responses = display_mcqs(mcqs_json)
        
        if submitted:
            st.session_state.responses = responses

        if 'responses' in st.session_state and st.session_state.responses:
            st.write("### Responses:")
            student_answers=[]
            for i, response in enumerate(st.session_state.responses):
               if response:
                  st.write(f"{mcqs_json[i]['question']}: {response}")
                  student_answers.append(response)
                  
with tab3:
	if submitted:
		student_answers = []
		questions = []
		answers = []
		for (i, response) in enumerate(st.session_state.responses):
			
			if response:
			    questions.append(mcqs_json[i]['question'])
			    answers.append(mcqs_json[i]['answer'])
			    student_answers.append(response)

		feedback_ans=feedback(questions, answers, student_answers,chatgpt_url, chatgpt_headers)
		for ids,data in enumerate(questions):
			st.write("Questions:",questions[ids])
			st.write("Correct Answer:",answers[ids])
			st.write("Student Response:",student_answers[ids])
			st.write("Feedback:",feedback_ans[ids])
			st.write("------------------------------------------------------------------------------------")

