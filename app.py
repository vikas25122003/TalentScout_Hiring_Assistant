import streamlit as st
from groq import Groq
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="TalentScout Assistant", page_icon="🤖")
st.title("TalentScout Hiring Assistant")

INFO_SEQUENCE = [
    "Full Name", "Email Address", "Phone Number", "Years of Experience",
    "Desired Position(s)", "Current Location", "Tech Stack"
]

# --- CLIENT SETUP ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Groq API key not found. Please add it to your Streamlit secrets.", icon="🚨")
    st.stop()

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}
if "stage" not in st.session_state:
    st.session_state.stage = "GATHERING_INFO"
    st.session_state.info_index = 0
    initial_greeting = "Welcome to TalentScout! I'm your intelligent hiring assistant. I'll ask a few questions to get started."
    st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
    first_question = f"First, could you please tell me your {INFO_SEQUENCE[0]}?"
    st.session_state.messages.append({"role": "assistant", "content": first_question})

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- MAIN LOGIC FOR HANDLING USER INPUT ---
if prompt := st.chat_input("Your response..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # STAGE 1: GATHERING INFORMATION (with Hybrid Validation)
    if st.session_state.stage == "GATHERING_INFO":
        current_info_key = INFO_SEQUENCE[st.session_state.info_index]
        is_valid = False  # Assume invalid by default

        # 1. For open-ended text, trust the user and always validate.
        if current_info_key in ["Full Name", "Desired Position(s)", "Current Location", "Tech Stack"]:
            is_valid = True
        
        # 2. For Email, use reliable regex.
        elif current_info_key == "Email Address":
            if re.match(r"[^@]+@[^@]+\.[^@]+", prompt):
                is_valid = True
        
        # 3. For Phone Number, check for digits.
        elif current_info_key == "Phone Number":
            if any(char.isdigit() for char in prompt):
                is_valid = True
        
        # 4. For Experience, use the LLM as it's good with natural language numbers.
        elif current_info_key == "Years of Experience":
            with st.spinner("Validating..."):
                validation_prompt = f"The user was asked for 'Years of Experience' and answered '{prompt}'. Does the answer contain a number or a numeric concept? Respond with only VALID or INVALID."
                response = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "system", "content": validation_prompt}], temperature=0, max_tokens=5)
                if response.choices[0].message.content.strip().upper().startswith("VALID"):
                    is_valid = True

        # --- Process based on validation result ---
        if is_valid:
            st.session_state.candidate_info[current_info_key] = prompt
            st.session_state.info_index += 1

            if st.session_state.info_index < len(INFO_SEQUENCE):
                next_info_key = INFO_SEQUENCE[st.session_state.info_index]
                system_prompt = f"You are a polite hiring assistant. Your ONLY task is to ask for the next piece of information: '{next_info_key}'. Ask a single, clear question."
                response = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "system", "content": system_prompt}], temperature=0.7)
                st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
            else:
                st.session_state.stage = "CONFIRMING_TECH_STACK"
                tech_stack = st.session_state.candidate_info.get("Tech Stack", "")
                confirmation_request = f"Great, thank you. You've listed your tech stack as: **{tech_stack}**. Is this correct, or would you like to modify it?"
                st.session_state.messages.append({"role": "assistant", "content": confirmation_request})
        else:
            reprompt_message = f"I'm sorry, that doesn't seem like a valid answer for '{current_info_key}'. Could you please try again?"
            st.session_state.messages.append({"role": "assistant", "content": reprompt_message})
        
        st.rerun()

    # STAGE 2: CONFIRMING TECH STACK
    elif st.session_state.stage == "CONFIRMING_TECH_STACK":
        user_response = prompt.lower()
        if any(word in user_response for word in ["yes", "correct", "proceed", "right", "ok"]):
            st.session_state.stage = "GENERATING_QUESTIONS"
            st.session_state.messages.append({"role": "assistant", "content": "Perfect! I will now generate technical questions. Please wait a moment."})
        else:
            with st.spinner("Updating your tech stack..."):
                current_stack = st.session_state.candidate_info.get("Tech Stack", "")
                modification_prompt = f"""The user's current tech stack is: "{current_stack}". The user wants to modify it with this instruction: "{prompt}". If the instruction is a simple negative like 'no', ask for the correct list. Otherwise, update the stack and return only the new, comma-separated list."""
                response = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "system", "content": modification_prompt}], temperature=0.1)
                new_tech_stack = response.choices[0].message.content.strip()
                if '?' in new_tech_stack:
                    st.session_state.messages.append({"role": "assistant", "content": new_tech_stack})
                else:
                    st.session_state.candidate_info["Tech Stack"] = new_tech_stack
                    confirmation_request = f"OK, I've updated your tech stack to: **{new_tech_stack}**. Is this correct now?"
                    st.session_state.messages.append({"role": "assistant", "content": confirmation_request})
        st.rerun()

    # STAGE 4: AWAITING ANSWERS
    elif st.session_state.stage == "AWAITING_ANSWERS":
        st.session_state.candidate_info["answers"] = prompt
        st.session_state.stage = "EVALUATING_ANSWERS"
        st.session_state.messages.append({"role": "assistant", "content": "Thank you for your answers. I will now prepare a brief performance report."})
        st.rerun()

    # STAGE 6: FOLLOW-UP & CONVERSATION
    elif st.session_state.stage == "FOLLOW_UP":
        if prompt.lower() in ["bye", "exit", "enough", "quit", "thank you", "thanks"]:
            st.session_state.stage = "FINISHED"
            st.session_state.messages.append({"role": "assistant", "content": "You're welcome! This concludes our session. Have a great day!"})
        else:
            with st.spinner("Thinking..."):
                system_prompt = "You are a helpful hiring assistant. The candidate is now asking follow-up questions about their performance report. Answer their questions based on the full conversation context."
                conversation_context = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                response = client.chat.completions.create(model="llama3-8b-8192", messages=conversation_context, temperature=0.7)
                st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# --- STATE-BASED ACTIONS (RUNS WITHOUT USER INPUT) ---

# STAGE 3: GENERATING QUESTIONS
if st.session_state.get("stage") == "GENERATING_QUESTIONS":
    with st.spinner("Generating role-specific technical questions..."):
        tech_stack = st.session_state.candidate_info.get("Tech Stack", "")
        desired_role = st.session_state.candidate_info.get("Desired Position(s)", "a technical role")
        question_generation_prompt = f"""
        You are a senior technical interviewer. Your task is to generate relevant technical questions for a candidate applying for the role of '{desired_role}'.
        The candidate's declared tech stack is: '{tech_stack}'.

        Follow these rules strictly:
        1. Generate 3-5 questions that are highly relevant to the intersection of the role and the tech stack.
        2. For a 'Web Developer' with 'Python', focus on web frameworks (Django, Flask), APIs, and databases. Avoid data science topics.
        3. For a 'Data Scientist' with 'Python', focus on NumPy, Pandas, Scikit-learn, and statistics.
        4. Format the output using Markdown with a heading for each technology.
        5. Do NOT provide answers.
        """
        response = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "system", "content": question_generation_prompt}], temperature=0.5)
        generated_questions = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": generated_questions})
        st.session_state.candidate_info["questions"] = generated_questions
        st.session_state.messages.append({"role": "assistant", "content": "Please provide your answers to the questions above."})
        st.session_state.stage = "AWAITING_ANSWERS"
    st.rerun()

# STAGE 5: EVALUATING ANSWERS
if st.session_state.get("stage") == "EVALUATING_ANSWERS":
    with st.spinner("Evaluating your answers and generating a report..."):
        questions = st.session_state.candidate_info.get("questions", "")
        answers = st.session_state.candidate_info.get("answers", "")
        evaluation_prompt = f"""
        You are an expert technical evaluator. Analyze a candidate's answers and provide a brief performance report.

        Here are the questions that were asked:
        ---QUESTIONS---
        {questions}
        ---END QUESTIONS---

        Here are the candidate's answers:
        ---ANSWERS---
        {answers}
        ---END ANSWERS---

        Generate a concise Markdown report with:
        1. **Overall Summary:** A one-sentence summary of the performance.
        2. **Detailed Breakdown:** A list evaluating each answer's correctness.
        """
        response = client.chat.completions.create(model="llama3-70b-8192", messages=[{"role": "system", "content": evaluation_prompt}], temperature=0.3)
        report = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": report})
        st.session_state.messages.append({"role": "assistant", "content": "This is your performance summary. Do you have any questions? You can say 'bye' to end our session."})
        st.session_state.stage = "FOLLOW_UP"
    st.rerun()