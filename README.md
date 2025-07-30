# AI Hiring Assistant Chatbot

This project is an advanced, AI-powered chatbot designed to automate the initial screening process for tech job candidates. Built for a fictional recruitment agency, "TalentScout," this chatbot engages users in a dynamic conversation to gather information, assess technical skills, and provide intelligent feedback.

## Key Features

- **Conversational Information Gathering**: Systematically collects essential candidate details like name, contact info, years of experience, desired role, and location.
- **Intelligent Input Validation**: Features a robust, hybrid validation system. It uses simple code (regex) for clear formats like emails and phone numbers, and a targeted LLM check for nuanced inputs like "Years of Experience" to ensure high data quality.
- **Interactive Tech Stack Confirmation**: After a candidate lists their technical skills, the chatbot presents the list back to them and enters a loop where they can add, remove, or modify skills until they confirm the list is correct.
- **Role-Contextual Question Generation**: The chatbot generates technical questions that are highly relevant to both the candidate's declared **tech stack** and their **desired job role**, ensuring a focused and professional screening.
- **AI-Powered Answer Evaluation**: After the candidate answers the technical questions, the bot uses a powerful LLM (Llama3-70B) to analyze the responses and generate a concise performance report, complete with an overall summary and a detailed breakdown.
- **Dynamic Follow-Up Conversation**: Once the evaluation is complete, the chatbot can discuss the results with the candidate, answering questions about their performance before gracefully ending the conversation.

## Demo

https://www.loom.com/share/ec607885fe42494db21659bad39850aa?sid=0a204df6-d819-4c71-a17e-aed47976ddda
Check Out the demo video at loom with 2x speed
<img width="1916" height="974" alt="image" src="https://github.com/user-attachments/assets/fc82e5d1-6b01-4885-96b7-74a2ca62e1b9" />
<img width="1919" height="955" alt="image" src="https://github.com/user-attachments/assets/128f0b9b-1bb2-437c-8564-25daf415d0b8" />
<img width="1915" height="965" alt="image" src="https://github.com/user-attachments/assets/2f67518a-ee21-40ea-9748-1ae48cdd8c46" />
<img width="1912" height="980" alt="image" src="https://github.com/user-attachments/assets/d7a19be6-1fe5-425e-8cb4-f4f5d165712a" />
<img width="1919" height="957" alt="image" src="https://github.com/user-attachments/assets/e7bc9f16-ad40-4762-9d4e-4a3541192735" />


## Technology Stack

- **Programming Language**: Python
- **User Interface**: Streamlit
- **AI/LLM**: Groq API with Llama 3 models (Llama3-8B for conversation and Llama3-70B for evaluation).

## Setup and Installation

To run this project locally, please follow these steps:

1.  **Clone the Repository**

    ```bash
    git clone <your-github-repository-link>
    cd <repository-folder-name>
    ```

2.  **Create and Activate a Virtual Environment**

    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    A `requirements.txt` file is included with all necessary packages.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Add API Key**

    - Create a folder named `.streamlit` in the root of the project directory.
    - Inside this folder, create a file named `secrets.toml`.
    - Add your Groq API key to this file as shown below:
      ```toml
      GROQ_API_KEY="your-gsk_...-key-here"
      ```

## Usage

To start the chatbot, run the following command in your terminal from the project's root directory:

```bash
streamlit run app.py
```

Your web browser will open a new tab with the chatbot interface. Simply follow the on-screen prompts to interact with the assistant.

## Architectural Decisions

The chatbot's conversational flow is managed by a **state machine** implemented using Streamlit's `st.session_state`. The application transitions through various stages (`GATHERING_INFO`, `CONFIRMING_TECH_STACK`, `EVALUATING_ANSWERS`, etc.) based on user input and internal logic. This architecture ensures a structured and predictable conversation flow while allowing for complex, multi-step interactions.

## Prompt Design

Effective prompt engineering was crucial for the chatbot's intelligence and reliability.

- **Validation Prompt**: A key challenge was validating user input. The final solution uses a hybrid approach. For fields like "Years of Experience," a targeted LLM prompt checks for numeric concepts. For other fields like "Email" and "Phone," simple, reliable Python code is used, and for open-ended text like "Full Name," user input is trusted to prevent frustrating loops.

- **Role-Contextual Question Prompt**: To ensure relevance, the question generation prompt is dynamically built to include both the candidate's `desired_role` and `tech_stack`. It explicitly instructs the LLM to generate questions at the intersection of these two contexts.

- **Answer Evaluation Prompt**: This prompt provides the LLM with the original questions and the candidate's answers, instructing it to act as an expert evaluator and produce a report in a strict Markdown format (Overall Summary and Detailed Breakdown).

## Challenges and Solutions

A primary challenge during development was implementing a reliable input validation system.

- **Challenge**: An early AI-based validation approach was too aggressive, incorrectly rejecting valid inputs like single-word names. A later attempt that used a simple allow-list for validation was too lenient, accepting numbers for job roles.

- **Solution**: The final implementation uses a robust **hybrid approach**. It trusts user input for open-ended fields, uses fast and reliable Python code (regex) for strict formats like emails, and leverages the LLM only for nuanced fields like "Years of Experience." This provides the ideal balance of fault tolerance and user-friendliness.
