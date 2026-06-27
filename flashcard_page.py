import streamlit as st
from utils.flashcard_generator import generate_flashcards, parse_flashcards


def render_flashcard_page():
    st.markdown("""
    <div class="page-header">
        <span class="page-icon">🃏</span>
        <div>
            <h1 class="page-title">Flashcards</h1>
            <p class="page-subtitle">AI-generated study cards from your document</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------- CHECK DOCUMENT ---------- #
    if st.session_state.index is None or st.session_state.text_chunks is None:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <h3>No Document Loaded</h3>
            <p>Upload and process a PDF from the <strong>Chat + PDF</strong> page first.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ---------- INIT SESSION ---------- #
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = None
    if "fc_index" not in st.session_state:
        st.session_state.fc_index = 0
    if "fc_flipped" not in st.session_state:
        st.session_state.fc_flipped = False
    if "fc_count" not in st.session_state:
        st.session_state.fc_count = 10

    # ---------- CONTROLS ---------- #
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        count = st.selectbox("Number of Cards", [5, 10, 15, 20], index=1)
        st.session_state.fc_count = count
    with col2:
        topic_filter = st.text_input("Focus Topic (optional)", placeholder="e.g. sorting algorithms")
    with col3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        generate_btn = st.button("✨ Generate Flashcards", use_container_width=True, type="primary")

    if generate_btn:
        with st.spinner("🧠 Generating your flashcards..."):
            raw = generate_flashcards(
                st.session_state.text_chunks,
                count=st.session_state.fc_count,
                topic=topic_filter
            )
            cards = parse_flashcards(raw)
            if not cards:
                st.error("Failed to generate flashcards. Please try again.")
                return
            st.session_state.flashcards = cards
            st.session_state.fc_index = 0
            st.session_state.fc_flipped = False
        st.success(f"✅ Generated {len(cards)} flashcards!")

    # ---------- DISPLAY CARDS ---------- #
    if st.session_state.flashcards:
        cards = st.session_state.flashcards
        idx = st.session_state.fc_index
        total = len(cards)
        card = cards[idx]

        # Progress bar
        progress = (idx + 1) / total
        st.markdown(f"""
        <div class="fc-progress-wrap">
            <div class="fc-progress-bar" style="width:{progress*100:.1f}%"></div>
            <span class="fc-progress-label">{idx+1} / {total}</span>
        </div>
        """, unsafe_allow_html=True)

        # Card display
        is_flipped = st.session_state.fc_flipped
        front_text = card.get("front", "")
        back_text = card.get("back", "")
        hint_text = card.get("hint", "")

        if not is_flipped:
            st.markdown(f"""
            <div class="flashcard front">
                <div class="card-label">QUESTION</div>
                <div class="card-content">{front_text}</div>
                {f'<div class="card-hint">💡 Hint: {hint_text}</div>' if hint_text else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="flashcard back">
                <div class="card-label">ANSWER</div>
                <div class="card-content">{back_text}</div>
            </div>
            """, unsafe_allow_html=True)

        # Navigation buttons
        c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 1, 1])

        with c1:
            if st.button("⬅️ Prev", use_container_width=True, disabled=(idx == 0)):
                st.session_state.fc_index = max(0, idx - 1)
                st.session_state.fc_flipped = False
                st.rerun()

        with c2:
            if st.button("➡️ Next", use_container_width=True, disabled=(idx == total - 1)):
                st.session_state.fc_index = min(total - 1, idx + 1)
                st.session_state.fc_flipped = False
                st.rerun()

        with c3:
            flip_label = "👁️ Show Answer" if not is_flipped else "🔄 Show Question"
            if st.button(flip_label, use_container_width=True, type="primary"):
                st.session_state.fc_flipped = not st.session_state.fc_flipped
                st.rerun()

        with c4:
            if st.button("🔀 Shuffle", use_container_width=True):
                import random
                random.shuffle(st.session_state.flashcards)
                st.session_state.fc_index = 0
                st.session_state.fc_flipped = False
                st.rerun()

        with c5:
            if st.button("🔁 Restart", use_container_width=True):
                st.session_state.fc_index = 0
                st.session_state.fc_flipped = False
                st.rerun()

        # All cards grid view
        st.markdown("---")
        st.markdown("### 📋 All Cards Overview")
        cols = st.columns(3)
        for i, c in enumerate(cards):
            with cols[i % 3]:
                active_class = "card-grid-active" if i == idx else ""
                st.markdown(f"""
                <div class="card-grid-item {active_class}" onclick="">
                    <div class="card-grid-num">#{i+1}</div>
                    <div class="card-grid-q">{c.get('front','')[:80]}{'...' if len(c.get('front','')) > 80 else ''}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Go to #{i+1}", key=f"goto_{i}", use_container_width=True):
                    st.session_state.fc_index = i
                    st.session_state.fc_flipped = False
                    st.rerun()