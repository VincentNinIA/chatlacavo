import streamlit as st
from openai import OpenAI

# ---------- Configuration ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]

# ---------- État global ----------
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "history" not in st.session_state:
    st.session_state.history = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None  # sera créé au lancement

# ---------- Vue d’introduction ----------
if not st.session_state.show_chat:
    st.title("Incarnez Carole dans un conflit au travail")
    st.markdown(
        """
        **Bienvenue dans cette simulation de gestion de conflit**.

        Vous incarnez **Carole**, employée dans un fast-food rétro années 80.  
        Votre collègue **JP** a 30 ans d’ancienneté et un caractère bien trempé.

        **Mission** : discuter avec JP, désamorcer le conflit, rétablir la coopération.

        Poursuivez jusqu’à ce que l’assistant affiche **“FIN DE SIMULATION”** ;  
        vous recevrez alors un **feedback structuré**.
        """
    )
    if st.button("🚀 Commencer la simulation"):
        # nouveau thread + affichage du chat
        st.session_state.thread_id = client.beta.threads.create().id
        st.session_state.show_chat = True
        st.rerun()
    st.stop()

# ---------- Vue Chat ----------
st.title("💬 Simulation de conflit — Carole & JP")

# --- Bouton RESET ---
if st.button("🗑️ Effacer la conversation", type="secondary"):
    st.session_state.history = []
    st.session_state.thread_id = client.beta.threads.create().id  # nouveau thread
    st.rerun()

thread_id = st.session_state.thread_id

# 1) Rejouer l’historique
for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

# 2) Champ d’entrée
if prompt := st.chat_input("Votre message pour JP…"):
    # a) afficher & stocker la question
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # b) envoyer au thread distant
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    # c) réponse streaming
    with st.chat_message("assistant"):
        placeholder, full_reply = st.empty(), ""
        with client.beta.threads.runs.create_and_stream(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
        ) as stream:
            for event in stream:
                if event.event == "thread.message.delta":
                    for part in (event.data.delta.content or []):
                        if part.type == "text":
                            full_reply += part.text.value
                            placeholder.markdown(full_reply + "▌")
            stream.until_done()

        placeholder.markdown(full_reply)
        st.session_state.history.append(("assistant", full_reply))

        if "FIN DE SIMULATION" in full_reply.upper():
            st.success("Simulation terminée ! Un feedback structuré vous sera proposé.")
