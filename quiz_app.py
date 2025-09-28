import streamlit as st
import google.generativeai as genai

#  CONFIGURE GEMINI
genai.configure(api_key="AIzaSyDxZiX1wsjX3i2aGDsk9mssDSgYoiA0_5w")

# FETCH QUESTIONS
def fetch_questions():
    prompt = """Generate 10 multiple-choice questions on recent geopolitical issues.
For each question:
Q: [question]
A. [option A]
B. [option B]
C. [option C]
D. [option D]
Answer: [Correct Option Letter]
Explanation: [One sentence explaining the correct answer]"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    raw_data = response.text.strip()

    questions = []
    answers = []
    explanations = []

    raw_questions = raw_data.split("\n\n")
    for item in raw_questions:
        if "Answer:" in item and "Explanation:" in item:
            question_text = item.split("Answer:")[0].strip()
            answer_letter = item.split("Answer:")[1].split("Explanation:")[0].strip().upper()
            explanation_text = item.split("Explanation:")[1].strip()

            questions.append(question_text)
            answers.append(answer_letter)
            explanations.append(explanation_text)

    return questions, answers, explanations

#  STREAMLIT APP 
st.set_page_config(page_title="Geopolitical Quiz", layout="centered")
st.title("🌍 Geopolitical Quiz")

# Initialize session state
if "questions" not in st.session_state:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.explanations = []
    st.session_state.user_answers = []
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.quiz_completed = False

# Start Quiz Button
if not st.session_state.questions:
    if st.button("Start Quiz"):
        with st.spinner("Fetching questions from Gemini..."):
            q, a, e = fetch_questions()
            st.session_state.questions = q
            st.session_state.answers = a
            st.session_state.explanations = e
            st.session_state.user_answers = [None] * len(q)
        st.success("Questions loaded! Scroll down to start answering.")

# Show Questions
if st.session_state.questions and not st.session_state.quiz_completed:
    q_idx = st.session_state.current_question
    question = st.session_state.questions[q_idx]

    st.subheader(f"Question {q_idx + 1} of {len(st.session_state.questions)}")
    st.write(question)

    # Extract options (lines starting with A., B., C., D.)
    options = [line for line in question.split("\n") if line.strip().startswith(("A.", "B.", "C.", "D."))]
    choice = st.radio("Select your answer:", options, index=None, key=f"q_{q_idx}")

    if st.button("Submit Answer"):
        if choice:
            selected_letter = choice.split(".")[0].strip()
            st.session_state.user_answers[q_idx] = selected_letter

            # Score update
            if selected_letter == st.session_state.answers[q_idx]:
                st.session_state.score += 1

            # Move to next question
            if st.session_state.current_question < len(st.session_state.questions) - 1:
                st.session_state.current_question += 1
                st.experimental_rerun()
            else:
                st.session_state.quiz_completed = True
                st.experimental_rerun()
        else:
            st.warning("Please select an answer before submitting.")

# Show Results
if st.session_state.quiz_completed:
    st.header("✅ Quiz Completed!")
    st.write(f"Your Score: **{st.session_state.score}/{len(st.session_state.questions)}**")
    
    with st.expander("See Explanations"):
        for i, q in enumerate(st.session_state.questions):
            st.markdown(f"**Q{i+1}:** {q}")
            st.markdown(f"**Your Answer:** {st.session_state.user_answers[i]}")
            st.markdown(f"**Correct Answer:** {st.session_state.answers[i]}")
            st.markdown(f"**Explanation:** {st.session_state.explanations[i]}")
            st.write("---")

    if st.button("Restart Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

