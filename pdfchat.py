# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 13:58:54 2023

Application : Chat with PDF

@author: Rakesh M K
"""
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import langchain
langchain.verbose = False
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from html_Template1 import css, bot_template ,user_template

def get_pdf_text(pdf_files):
    text = ""
    for pdf in pdf_files:
        pdf_reader = PdfReader(pdf)
        for pages in pdf_reader.pages:
            text += pages.extract_text()
    return text

def get_text_chunks(text_pdf):
    text_splitter = CharacterTextSplitter(separator ='\n',
                                          chunk_size=1000,
                                          chunk_overlap=200,
                                          length_function = len)
    chunks = text_splitter.split_text(text_pdf)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    #embeddings = HuggingFaceInstructEmbeddings()
    vectorstore = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vectorstore
    
def get_conversation_chain(vectorstore):

    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key = 'chat_history', return_messages = True)
    conversation_chain  =ConversationalRetrievalChain.from_llm(llm=llm,
                                                               retriever=vectorstore.as_retriever(),
                                                               memory=memory)
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question':user_question})
#    st.write(response)
    st.session_state.chat_history = response['chat_history']
    
    for i ,message in enumerate(st.session_state.chat_history):
        
        if i%2 ==0:
            st.write(user_template.replace('{{MSG}}',message.content), unsafe_allow_html =True)
        else:
            st.write(bot_template.replace('{{MSG}}',message.content), unsafe_allow_html =True)


def main():
    load_dotenv()
    st.set_page_config(page_title = 'Multiple PDF Chat' ,page_icon ='📖')
    st.write(css, unsafe_allow_html = True)
    
    
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None
        
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        
    st.header('Multiple PDF Chat :📖')
    user_question = st.text_input('Query about your documents')
    
    if user_question:
        handle_userinput(user_question)
    
 #   st.write(user_template.replace('{{MSG}}','Hello Bot'), unsafe_allow_html =True)
  #  st.write(bot_template.replace('{{MSG}}','Hello Friend'), unsafe_allow_html =True)

    
    with st.sidebar:
        st.subheader('Your Documents')
        pdf_files = st.file_uploader('Upload your PDF and Process',accept_multiple_files = True )
        
        if st.button('Process'):
             with st.spinner("Processing"):
               # get the pdf 
                 text_pdf = get_pdf_text(pdf_files)
               # st.write(text_pdf)
               # get the chunks
                 text_chunks = get_text_chunks(text_pdf)
               #  st.write(text_chunks)
                 vectorstore = get_vectorstore(text_chunks)
               # create conversation chain
                 st.session_state.conversation = get_conversation_chain(vectorstore)
                 
            
            #create vector
    
if __name__ == '__main__':
   
    main()



