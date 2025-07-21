import streamlit as st
from openai import OpenAI

# ---------- Configuration ----------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]  # créé dans le dashboard OpenAI

# ---------- Helpers mis en cache ----------
@st.cache_resource(show_spinner=False)
def get_thread_id():
    """Un thread distant par session Streamlit."""
    return client.beta.threads.create().id

# ---------- État de l’interface ----------
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Vue d’introduction ----------
if not st.session_state.show_chat:
    st.title("Incarnez Carole dans un conflit au travail")
    st.markdown(
        """
        **Bienvenue dans cette simulation de gestion de conflit**.

        Vous incarnez **Carole**, employée dans un fast-food rétro années 80.  
        Votre collègue **JP** (30 ans d’ancienneté) est réputé pour son caractère bien trempé : méthodes immuables, critiques fréquentes, tensions récurrentes.

        Aujourd’hui, un nouvel accrochage vient raviver le conflit.  
        **Votre mission** : engager la discussion, désamorcer les tensions et rétablir la coopération.

        - Testez votre posture et vos outils de communication.  
        - Tentez de maintenir une relation professionnelle malgré la situation tendue.  
        - **Poursuivez la conversation jusqu’à ce que l’assistant affiche “FIN DE SIMULATION”.**  
          À ce moment-là, vous recevrez un **feedback structuré** sur votre gestion du conflit.
        """
    )
    if st.button("🚀 Commencer la simulation"):
        st.session_state.show_chat = True
        st.session_state.thread_id = get_thread_id()  # prépare le thread
        st.rerun()
    st.stop()  # empêche le reste du script de s’exécuter tant que le chat n’est pas lancé

# ---------- Vue Chat ----------
st.title("💬 Simulation de conflit — Carole & JP")
thread_id = st.session_state.thread_id

# 1) Rejouer l’historique
for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

# 2) Champ d’entrée utilisateur
if prompt := st.chat_input("Votre message pour JP…"):
    # a) afficher / stocker la question
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # b) envoyer au thread distant
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=prompt)

    # c) réponse streaming
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

        # d) rendu final
        placeholder.markdown(full_reply)
        st.session_state.history.append(("assistant", full_reply))

        # e) si l’assistant signale la fin, afficher un bandeau feedback (placeholder)
        if "FIN DE SIMULATION" in full_reply.upper():
            st.success("Simulation terminée ! Un feedback structuré va s’afficher sous peu…")
            # À implémenter : génération et affichage du feedback.
