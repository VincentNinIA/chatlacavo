import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("💬 Chatbot OpenAI (streaming propre)")

# Historique en session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un assistant francophone, utile et concis."}
    ]

# 1) Rejouer l’historique (on saute le système)
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 2) Entrée utilisateur
if prompt := st.chat_input("Pose ta question…"):
    # a) On sauvegarde et affiche immédiatement la question
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # b) Préparer le bloc assistant + placeholder
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        # c) Appel OpenAI en streaming
        for chunk in openai.chat.completions.create(
            model="gpt-4o-mini",           # ou "gpt-4.1-mini"
            messages=st.session_state.messages,
            stream=True
        ):
            delta = chunk.choices[0].delta
            if delta.content:
                full_reply += delta.content
                placeholder.markdown(full_reply + "▌")  # remplace le contenu

        # d) Contenu final (sans curseur)
        placeholder.markdown(full_reply)

    # e) On ajoute la réponse complète à l’historique
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
