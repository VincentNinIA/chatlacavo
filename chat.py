import streamlit as st
import openai, os

# --- Config -------------------------------------------------
openai.api_key  = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID    = st.secrets["ASSISTANT_ID"]

# --- Helpers mis en cache -----------------------------------
@st.cache_resource(show_spinner=False)
def get_client():
    """Client unique, réutilisé entre les reruns."""
    return openai.Client(api_key=openai.api_key)

client = get_client()

@st.cache_resource(show_spinner=False)
def get_thread():
    """Un thread par session utilisateur Streamlit."""
    return client.beta.threads.create().id

thread_id = get_thread()

# --- UI -----------------------------------------------------
st.title("💬 Chatbot via Assistant API")

# Historique : on relit toutes les paires user/assistant déjà stockées
if "history" not in st.session_state:
    st.session_state.history = []

for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

# Champ d’entrée utilisateur
if prompt := st.chat_input("Pose ta question…"):
    # 1) Affichage immédiat de la question
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.history.append(("user", prompt))

    # 2) Enregistrement dans le thread distant
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    # 3) Lancement du run en streaming
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        # La méthode 'stream' ouvre un flux SSE d’événements
        # et itère jusqu’à la fin du run.
        for event in client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
        ):
            # On s’intéresse aux deltas de texte générés par l’assistant
            if event.event == "thread.message.delta":
                delta = event.data.delta
                # Chaque delta.content est une liste d’éléments ;
                # on ne garde que ceux de type "text"
                for part in delta.content:
                    if part.type == "text":
                        full_reply += part.text.value
                        placeholder.markdown(full_reply + "▌")

        # 4) Texte final (sans curseur) + sauvegarde
        placeholder.markdown(full_reply)
        st.session_state.history.append(("assistant", full_reply))
