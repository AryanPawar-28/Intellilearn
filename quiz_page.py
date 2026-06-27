import streamlit as st
from utils.quiz_generator import generate_quiz, parse_quiz




def render_quiz_page():


    st.header("🧠 Quiz Generator")


    # ---------- CHECK DOCUMENT ---------- #
    if st.session_state.index is None or st.session_state.text_chunks is None:
        st.warning("Upload and process a document first.")
        return


    # ---------- INIT SESSION ---------- #
    if "quiz" not in st.session_state:
        st.session_state.quiz = None


    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}


    if "submitted" not in st.session_state:
        st.session_state.submitted = False


    # ---------- DIFFICULTY ---------- #
    difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard"]
    )


    # ---------- GENERATE QUIZ ---------- #
    if st.button("Generate Quiz", use_container_width=True):


        with st.spinner("Creating quiz..."):


            quiz_text = generate_quiz(
                st.session_state.text_chunks,
                difficulty=difficulty
            )


            questions = parse_quiz(quiz_text)


            if not questions:
                st.error("Failed to generate quiz. Try again.")
                return


            st.session_state.quiz = questions
            st.session_state.user_answers = {}
            st.session_state.submitted = False


    # ---------- DISPLAY QUIZ ---------- #
    if st.session_state.quiz:


        for i, q in enumerate(st.session_state.quiz):


            st.markdown(f"### 📝 Q{i+1}: {q['question']}")


            options = q["options"]


            selected = st.radio(
                "Choose:",
                options,
                index=None,
                key=f"q_{i}",
                disabled=st.session_state.submitted
            )


            st.session_state.user_answers[i] = selected


        # ---------- SUBMIT ---------- #
        if st.button("Submit Quiz", use_container_width=True):


            # check all answered
            if None in st.session_state.user_answers.values():
                st.warning("Please answer all questions before submitting.")
                return


            st.session_state.submitted = True


        # ---------- RESULTS ---------- #
        if st.session_state.submitted:


            score = 0


            st.markdown("## 🎯 Results")


            for i, q in enumerate(st.session_state.quiz):


                user_ans = st.session_state.user_answers.get(i)
                correct_ans = q["answer"]


                st.markdown(f"### Q{i+1}: {q['question']}")


                if user_ans == correct_ans:
                    st.success(f"✅ Correct: {correct_ans}")
                    score += 1
                else:
                    st.error("❌ Wrong")
                    st.write(f"**Your Answer:** {user_ans}")
                    st.write(f"**Correct Answer:** {correct_ans}")


                st.info(f"💡 Explanation: {q['explanation']}")
                st.markdown("---")


            st.success(f"🏆 Final Score: {score} / {len(st.session_state.quiz)}")


            if score == len(st.session_state.quiz):
                st.balloons()
