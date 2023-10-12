from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
import langchain
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

app = FastAPI()

langchain.verbose = False

@app.post("/process_pdf")
async def process_pdf(files: list[UploadFile], query: str):
    try:
        text_pdf = get_pdf_text(files)
        text_chunks = get_text_chunks(text_pdf)
        vectorstore = get_vectorstore(text_chunks)
        conversation_chain = get_conversation_chain(vectorstore)
        response = handle_userinput(query, conversation_chain)
        return JSONResponse(content={"response": response}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

def get_pdf_text(pdf_files):
    text = ""
    for pdf_file in pdf_files:
        pdf_content = pdf_file.file.read()
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text_pdf):
    text_splitter = CharacterTextSplitter(separator='\n', chunk_size=1000, chunk_overlap=200, length_function=len)
    chunks = text_splitter.split_text(text_pdf)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)
    return conversation_chain

def handle_userinput(user_question, conversation_chain):
    response = conversation_chain({'question': user_question})
    chat_history = response['chat_history']
    bot_responses = [message.content for i, message in enumerate(chat_history) if i % 2 != 0]
    return bot_responses

if __name__ == "__main__":
    load_dotenv()
