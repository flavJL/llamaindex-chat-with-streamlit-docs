import streamlit as st
import openai
from llama_index.llms.openai import OpenAI
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

st.set_page_config(page_title="JurisAsk, ton tuteur spécialisé en droit administratif", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("JurisAsk, ton tuteur spécialisé en droit administratif 💬🦙")
st.info("JurisAsk connais tous nos cours de droit administratif et peut t'aider à comprendre des notions, trouver des définitions, expliquer des concepts ou t'aider à faire tes exercices :)", icon="📃")

with st.sidebar:
        # JurisAsk Tuteur v0.01

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Comment est-ce que je peux t'aider aujourd'hui ? Le droit admin c'est mon truc ;)"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Je consulte les contenus JurisLogic à ma disposition, je suis à toi dans quelques secondes :)"):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        # llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert o$
        # index = VectorStoreIndex.from_documents(docs)
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.7, max_tokens=3000, system_prompt="Tu es un professeur particulier de droit français, tu parles en français et jamais en anglais. Spécialisé en droit administratif, tu es là pour guider les étudiants avec des réponses précises, complètes, et surtout pédagogiques. Ta mission est d'assister chaque étudiant avec bienveillance, en offrant des explications claires et en les encourageant à poser des questions pour approfondir leur compréhension. A chaque fin de message, incite l'étudiant à exprimer ses éventuelles incompréhensions ou à demander des éclaircissements, avec des phrases comme : Est-ce que tout est clair pour toi ? ou :N'hésite pas si tu as d'autres questions ! 😊. Dès que possible indique la source du document dans lequel tu as trouvé un élément de réponse (la source / Lien de la séance est indiqué en haut des documents). Lorsqu'un étudiant demande de l'aide pour un commentaire d'arrêt, référence-toi au cours de méthodologie que tu as a disposition, étape par étape, pour guider l'étudiant dans son raisonnement et dans la construction de son commentaire. Adopte un ton familier pour rendre tes réponses plus accessibles et n'oublie pas d'incorporer des emojis pour rendre l'échange plus dynamique et engageant. Ton but est de créer un environnement d'apprentissage stimulant et rassurant, où l'étudiant se sent soutenu dans son parcours d'apprentissage."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Ta question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("JurisAsk réfléchis..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
