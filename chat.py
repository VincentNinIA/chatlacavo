import streamlit as st
import openai

# 1) Clé stockée dans st.secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 2) Créer (ou récupérer) l'assistant/agent
@st.cache_resource  # évite de recréer à chaque rerun
def get_assistant():
    return openai.responses.create(
        model="gpt-4.1-mini",
        instructions="Tu es un assistant francophone spécialisé IA & Python.",
        tools=[{"type": "web_search"},
               {"type": "file_search"},
               {"type": "computer_use"}]
    )
assistant = get_assistant()

# 3) Thread persistant en session
if "thread_id" not in st.session_state:
    st.session_state.thread_id = openai.responses.Thread.create().id

# 4) Interface utilisateur
user_msg = st.chat_input("💬 Pose ta question…")
if user_msg:
    openai.responses.Thread.add_message(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_msg
    )
    with st.spinner("L'assistant réfléchit…"):
        for chunk in openai.responses.Thread.create_run(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant.id,
            stream=True
        ):
            delta = chunk.choices[0].delta
            if delta.content:
                st.write(delta.content, unsafe_allow_html=True)
