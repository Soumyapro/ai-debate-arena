import uuid
import streamlit as st

# All debate logic (prompts, models, graph, state) lives in main.py.
# This file only builds the UI around it.
try:
    import main
except Exception as e:
    st.error(f"Failed to load backend (`main.py`): {e}")
    st.stop()


st.set_page_config(page_title="AI Debate Arena", page_icon="🗣️", layout="centered")

st.title("🗣️ AI Debate Arena")
st.caption("Two LLMs debate a topic of your choosing.")

SPEAKER_AVATAR = {"Debate Model A": "🟦", "Debate Model B": "🟥"}


def render_message(name: str, content: str) -> None:
    avatar = SPEAKER_AVATAR.get(name, "🤖")
    with st.chat_message(name, avatar=avatar):
        st.markdown(f"**{name}**\n\n{content}")


# Session state
if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "running" not in st.session_state:
    st.session_state.running = False
if "winner" not in st.session_state:
    st.session_state.winner = None

# Sidebar controls 
# total_rounds and max_words are fixed in main.py and intentionally not exposed here.
with st.sidebar:
    st.header("Debate settings")
    topic_input = st.text_area(
        "Debate topic",
        value=main.topic,
        help="The resolution the two debaters will argue for/against.",
    )
    st.caption(f"Rounds: {main.total_rounds} · Max words/turn: {main.max_words}")

    col1, col2 = st.columns(2)
    start_clicked = col1.button("Start Debate", type="primary", use_container_width=True)
    reset_clicked = col2.button("Reset", use_container_width=True)

if reset_clicked:
    st.session_state.transcript = []
    st.session_state.running = False
    st.session_state.winner = None

# Kick off a new debate 
if start_clicked:
    # The node functions in main.py read `topic` from the module's global
    # namespace at call time, so overriding it here (before invoking the
    # graph) takes effect without editing main.py.
    main.topic = topic_input.strip() or main.topic

    st.session_state.transcript = []
    st.session_state.thread_id = str(uuid.uuid4())  # fresh checkpointer thread per run
    st.session_state.running = True
    st.session_state.winner = None

# Render whatever transcript we already have 
for name, content in st.session_state.transcript:
    render_message(name, content)

# Stream a fresh debate 
if st.session_state.running:
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    initial_state = {"messages": [], "loop_count": 0}

    with st.spinner(f"Debating: {main.topic}"):
        for update in main.graph.stream(initial_state, config=config):
            for node_name, output in update.items():
                if "messages" in output:
                    last_message = output["messages"][-1]
                    st.session_state.transcript.append((last_message.name, last_message.content))
                    render_message(last_message.name, last_message.content)

    st.session_state.running = False
    st.success("Debate finished.")

# Let the user pick a winner 
if st.session_state.transcript and not st.session_state.running:
    st.divider()
    if st.session_state.winner:
        st.subheader(f"🏆 You picked **{st.session_state.winner}** as the winner")
    else:
        st.subheader("Who won the debate?")
        vcol1, vcol2, vcol3 = st.columns(3)
        if vcol1.button("🟦 Debate Model A", use_container_width=True):
            st.session_state.winner = "Debate Model A"
            st.rerun()
        if vcol2.button("🟥 Debate Model B", use_container_width=True):
            st.session_state.winner = "Debate Model B"
            st.rerun()
        if vcol3.button("🤝 Tie", use_container_width=True):
            st.session_state.winner = "Tie"
            st.rerun()