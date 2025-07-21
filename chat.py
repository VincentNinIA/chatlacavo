import streamlit as st
import openai

# 1) Clef stockée dans st.secrets ou dans vos variables d'environnement
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("💬 Chatbot OpenAI (basique)")

# 2) Persistance de la conversation dans la session Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Tu es un assistant francophone utile et concis."}
    ]

# 3) Afficher l'historique
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4) Champ d’entrée utilisateur
if prompt := st.chat_input("Pose ta question…"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5) Appel OpenAI — sans tools
    with st.spinner("OpenAI réfléchit…"):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",       # ou "gpt-4.1-mini"
            messages=st.session_state.messages,
            stream=True               # streaming mot‑à‑mot
        )

        # 6) Affichage streaming
        stream_container = st.chat_message("assistant")
        full_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                full_reply += delta.content
                stream_container.markdown(full_reply + "▌")

        # 7) On fige la réponse finale
        stream_container.markdown(full_reply)
        st.session_state.messages.append({"role": "assistant", "content": full_reply})
