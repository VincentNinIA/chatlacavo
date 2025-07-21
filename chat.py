import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]

# ---------- helpers mis en cache ----------
@st.cache_resource(show_spinner=False)
def get_thread():
    return client.beta.threads.create().id

thread_id = get_thread()

# ---------- UI ----------
st.title("💬 Assistant OpenAI (stream)")

if "history" not in st.session_state:
    st.session_state.history = []

# rejouer l’historique
for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

# champ d’entrée
if prompt := st.chat_input("Pose ta question…"):
    # afficher/archiver la question
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # envoyer au thread distant
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    # réponse streaming ---------------------------------
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        with client.beta.threads.runs.create_and_stream(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
        ) as stream:
            for event in stream:
                if event.event == "thread.message.delta":
                    delta = event.data.delta
                    for part in delta.content or []:
                        if part.type == "text":
                            full_reply += part.text.value
                            placeholder.markdown(full_reply + "▌")
            stream.until_done()

        placeholder.markdown(full_reply)           # réponse finale
        st.session_state.history.append(("assistant", full_reply))
