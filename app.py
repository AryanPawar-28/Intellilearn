import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.views.chat_page import render_chat_page
from frontend.views.quiz_page import render_quiz_page
from frontend.views.animated_page import render_animated_page
from frontend.views.flashcard_page import render_flashcard_page
from frontend.views.mindmap_page import render_mindmap_page


# ── Load CSS ────────────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="INTELLILEARN",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    load_css()

    # ── Session init ─────────────────────────────────────────────
    defaults = {
        "all_chats":     {},
        "current_chat_id": None,
        "index":         None,
        "text_chunks":   None,
        "pdf_bytes":     None,
        "quiz":          None,
        "flashcards":    None,
        "mindmap_data":  None,
        "fc_index":      0,
        "fc_flipped":    False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if st.session_state.current_chat_id is None:
        chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.current_chat_id = chat_id
        st.session_state.all_chats[chat_id] = []

    # ── Sidebar ──────────────────────────────────────────────────
    with st.sidebar:

        # Brand logo + name  (full visibility, no clipping)
        st.markdown("""
        <div style="
            display:flex;
            align-items:center;
            gap:14px;
            padding:10px 4px 14px 4px;
            margin-bottom:2px;
        ">
            <div style="
                width:44px; height:44px;
                background:linear-gradient(135deg,#00d4ff,#a855f7);
                border-radius:12px;
                display:flex; align-items:center; justify-content:center;
                font-size:1.4rem;
                box-shadow:0 4px 16px rgba(0,212,255,0.35);
                flex-shrink:0;
            ">🧠</div>
            <div>
                <div style="
                    font-size:1.25rem;
                    font-weight:800;
                    letter-spacing:-0.02em;
                    background:linear-gradient(90deg,#00d4ff,#a855f7);
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                    background-clip:text;
                    line-height:1.2;
                ">IntelliLearn</div>
                <div style="font-size:0.65rem;color:#4a6080;font-weight:500;letter-spacing:0.05em;">
                    AI LEARNING PLATFORM
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigate",
            [
                "📄  Chat + PDF",
                "🧩  Quiz",
                "🎬  Animation",
                "🃏  Flashcards",
                "🧠  Mind Map",
            ],
            key="page_nav",
            label_visibility="visible",
        )

        st.markdown("---")

        # Document status pill
        if st.session_state.index is not None:
            st.markdown("""
            <div style="
                background:linear-gradient(135deg,rgba(52,211,153,0.12),rgba(52,211,153,0.06));
                border:1px solid rgba(52,211,153,0.28);
                border-radius:10px;
                padding:10px 14px;
                margin-bottom:14px;
            ">
                <div style="color:#34d399;font-size:0.72rem;font-weight:700;letter-spacing:0.07em;">
                    ✓ &nbsp;DOCUMENT LOADED
                </div>
                <div style="color:#4a6080;font-size:0.7rem;margin-top:2px;">
                    Ready to generate content
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background:linear-gradient(135deg,rgba(251,191,36,0.08),rgba(251,191,36,0.03));
                border:1px solid rgba(251,191,36,0.2);
                border-radius:10px;
                padding:10px 14px;
                margin-bottom:14px;
            ">
                <div style="color:#fbbf24;font-size:0.72rem;font-weight:700;letter-spacing:0.07em;">
                    ⚠ &nbsp;NO DOCUMENT
                </div>
                <div style="color:#4a6080;font-size:0.7rem;margin-top:2px;">
                    Upload a PDF in Chat + PDF
                </div>
            </div>
            """, unsafe_allow_html=True)

        # New Chat button
        if st.button("＋  New Chat", use_container_width=True):
            new_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.current_chat_id = new_id
            st.session_state.all_chats[new_id] = []
            st.session_state.index       = None
            st.session_state.text_chunks = None
            st.session_state.pdf_bytes   = None
            st.session_state.flashcards  = None
            st.session_state.mindmap_data = None
            st.rerun()

        # Footer
        st.markdown("""
        <div style="
            margin-top:28px;
            padding-top:14px;
            border-top:1px solid rgba(255,255,255,0.06);
            text-align:center;
            font-size:0.65rem;
            color:#2a3a55;
            letter-spacing:0.04em;
        ">
            Powered by Groq · LLaMA 3.3
        </div>
        """, unsafe_allow_html=True)

    # ── Routing ──────────────────────────────────────────────────
    page_clean = page.strip()
    if   "Chat"        in page_clean: render_chat_page()
    elif "Quiz"        in page_clean: render_quiz_page()
    elif "Animation"   in page_clean: render_animated_page()
    elif "Flashcards"  in page_clean: render_flashcard_page()
    elif "Mind Map"    in page_clean: render_mindmap_page()


if __name__ == "__main__":
    main()