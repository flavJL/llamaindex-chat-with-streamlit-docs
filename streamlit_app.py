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
st.info("JurisAsk connait tous nos cours de droit administratif et peut t'aider à comprendre des notions, trouver des définitions, expliquer des concepts ou t'aider à faire tes exercices :)", icon="📃")

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner("Je consulte les contenus JurisLogic à ma disposition, je suis à toi dans quelques secondes :)"):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.7, max_tokens=3000, system_prompt="Your detailed system prompt here..."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

# Initialize the chat engine in the session state if not already present
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

# Initialize the messages in the session state if not already present
if "messages" not in st.session_state:
    st.session_state['messages'] = [{"role": "assistant", "content": "Comment est-ce que je peux t'aider aujourd'hui ? Le droit admin c'est mon truc ;)"}]

# Display all messages so far
for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle new user input
if prompt := st.chat_input("Ta question"):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    # Generate and display the response from the assistant incrementally
    if st.session_state['messages'][-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("JurisAsk réfléchit..."):
                
                # Here, replace the placeholder loop with your actual chat engine streaming response
                response_generator = st.session_state.chat_engine.stream_chat(prompt)
                
                full_response = ""
                for token in response_generator.response_gen:  # Assuming response_gen is the correct attribute
                    full_response += token
                    
                # After collecting the full response, display it and add to the message history
                st.write(full_response)
                st.session_state['messages'].append({"role": "assistant", "content": full_response})