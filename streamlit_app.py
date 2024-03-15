# Override the standard library sqlite3 with pysqlite3
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import openai
import chromadb
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
try:
    from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
    from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
from llama_index.core import StorageContext

# App configuration
st.set_page_config(page_title="JurisAsk, ton tuteur spécialisé en droit administratif", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key

# App title and info
st.title("JurisAsk, ton tuteur spécialisé en droit administratif 💬🦙")
st.info("JurisAsk connais tous nos cours de droit administratif et peut t'aider à comprendre des notions, trouver des définitions, expliquer des concepts ou t'aider à faire tes exercices :)", icon="📃")

# Sidebar setup
with st.sidebar:
    st.header('JurisAsk Tuteur', divider='rainbow')
    st.markdown('V0.01 :sunglasses:')
    st.write('Cette première version est capable de chercher dans nos cours de droit administratif pour répondre à tes questions. Tu peux lui demander de t\'expliquer des notions, de trouver des arrêts, de t\'aider sur un exercice... N\'oublie pas qu\'il s\'agit d\'une toute première version et que tes retours seront hyper utile !')
    text_input = st.text_input("Donne nous ton avis 👇", label_visibility='visible', disabled=False, placeholder="Ton avis...")

if text_input:
    st.write("You entered: ", text_input)

# Initialize chat messages history if not already present
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Comment est-ce que je peux t'aider aujourd'hui ? Le droit admin c'est mon truc ;)"}]

# Load data function with ChromaDB integration
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Je consulte les contenus JurisLogic à ma disposition, je suis à toi dans quelques secondes :)"):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        
        # Initialize ChromaDB client and collection
        db = chromadb.PersistentClient(path="./chroma_db")
        chroma_collection = db.get_or_create_collection("jurisask_documents")

        # Set up language model service context with ChromaDB as vector store
        llm_service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo-0125", temperature=0.8, max_tokens=3500, system_prompt='''Tu es un professeur particulier de droit français, tu parles en français et jamais en anglais. Spécialisé en droit administratif, tu es là pour guider les étudiants avec des réponses précises, complètes, bien formatée et surtout pédagogiques. Ta mission est d'assister chaque étudiant avec bienveillance, en offrant des explications claires et en les encourageant à poser des questions pour approfondir leur compréhension. SI l'étudiant te demande de rédiger quelque chose tu dois le faire comme si tu étais l'étudiant (par ex : "rédige un cas pratique" tu dois alors rédiger le cas pratique à la place de l'étudiant. A chaque fin de message, incite l'étudiant à exprimer ses éventuelles incompréhensions ou à demander des éclaircissements. Adopte un ton familier pour rendre tes réponses plus accessibles et n'oublie pas d'incorporer des emojis pour rendre l'échange plus dynamique et engageant.'''))
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store, llm=llm_service_context.llm)

        # Create index from documents with ChromaDB and service context
        index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
        return index

# Load and index documents with ChromaDB
index = load_data()

# Initialize chat engine with indexed data
if "chat_engine" not in st.session_state.keys():
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

# Chat input and message handling
if prompt := st.chat_input("Ta question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Generate and display new response if last message is not from the assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("JurisAsk réfléchis..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            st.session_state.messages.append({"role": "assistant", "content": response.response})
