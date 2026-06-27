import streamlit as st
from utils.llm_answer import generate_animation_script
from utils.animated_video import create_animated_video




def render_animated_page():


    st.header("🎬 Animated Video")


    if st.session_state.text_chunks is None:
        st.warning("Upload PDF first")
        return


    if st.button("Generate Animated Video"):


        with st.spinner("Creating video..."):


            # Step 1: generate script
            script = generate_animation_script(
                st.session_state.text_chunks
            )


            # Step 2: create video
            video_path = create_animated_video(script)


            st.success("Video Ready!")


            st.video(video_path)