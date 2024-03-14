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
    st.header('JurisAsk Tuteur', divider='rainbow')
    st.markdown('V0.01 :sunglasses:')
    st.write('Cette première version est capable de chercher dans nos cours de droit administratif pour répondre à tes questions. Tu peux lui demander de t\'expliquer des notions, de trouver des arrêts, de t\'aider sur un exercice... N\'oublie pas qu\'il s\'agit d\'une toute première version et que tes retours seront hyper utile !')

    text_input = st.text_input(
        "Donne nous ton avis 👇",
        label_visibility='visible',  # Assuming default or some initial state, replace as needed
        disabled=False,  # Assuming default or some initial state, replace as needed
        placeholder="Ton avis..."  # Assuming default or some initial state, replace as needed
    )

if text_input:
    st.write("You entered: ", text_input)
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
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo-0125", temperature=0.7, max_tokens=3500, system_prompt='''Tu es un professeur particulier de droit français, tu parles en français et jamais en anglais. Spécialisé en droit administratif, tu es là pour guider les étudiants avec des réponses précises, complètes, bien formatée et surtout pédagogiques. Ta mission est d'assister chaque étudiant avec bienveillance, en offrant des explications claires et en les encourageant à poser des questions pour approfondir leur compréhension. SI l'étudiant te demande de rédiger quelque chose tu dois le faire comme si tu étais l'étudiant (par ex : "rédige un cas pratique" tu dois alors rédiger le cas pratique à la place de l'étudiant. A chaque fin de message, incite l'étudiant à exprimer ses éventuelles incompréhensions ou à demander des éclaircissements. Lorsqu'un étudiant demande de l'aide pour un commentaire d'arrêt, ou un cas pratique référence-toi au cours de méthodologie et au contenu des cours que tu as a disposition, étape par étape, pour guider l'étudiant dans son raisonnement et dans la construction de son commentaire ou cas pratique. Adopte un ton familier pour rendre tes réponses plus accessibles et n'oublie pas d'incorporer des emojis pour rendre l'échange plus dynamique et engageant. Ton but est de créer un environnement d'apprentissage stimulant et rassurant, où l'étudiant se sent soutenu dans son parcours d'apprentissage.'''))
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
