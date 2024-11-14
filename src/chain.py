from langchain.document_loaders import SitemapLoader, RecursiveUrlLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS, Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from prompts import qa_prompt, condense_question_prompt
from db import load_session_history, save_message

def get_llm():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=1000)
    return llm

def get_embeddings():
    embeddings = OpenAIEmbeddings()
    return embeddings

def load_documents(urls):

    loader = WebBaseLoader(urls)

    # docs = sitemap_loader.load()
    docs = loader.load()

    return docs

def create_vector_db(collection_name, docs):
    # # Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                chunk_overlap=200)
    
    # Split the documents into smaller text chunks
    texts = text_splitter.split_documents(docs)
    persist_directory = "../persist"

    # Create a new Chroma collection from the text chunks
    # try:
    vector_db = Chroma.from_documents(
        documents=texts,
        embedding=get_embeddings(),
        persist_directory=persist_directory,
        collection_name=collection_name,
    )
    # except Exception as e:
    #     print(f"Error creating collection: {e}")
    #     return None

    return vector_db

def load_vector_db(collection_name):
    persist_directory = "../persist"
    # Load the Chroma collection from the specified directory
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=get_embeddings(),
        collection_name=collection_name,
    )

    return vector_db

def get_retriver(vector_db):
    # # Load docs
    # docs = load_documents(urls)

    # # Split
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
    #                                             chunk_overlap=200)
    # splits = text_splitter.split_documents(docs)


    # # Embed
    # vectorstore = FAISS.from_documents(documents=splits, 
    #                                 embedding=OpenAIEmbeddings())
    retriever = vector_db.as_retriever()

    return retriever

# def get_rephrase_question_chain():
#     llm = get_llm()
#     rephrase_question_chain = contextualize_q_prompt | llm | StrOutputParser()
#     return rephrase_question_chain

def get_rag_chain():
    llm = get_llm()
    urls = [
        'https://cmcglobal.com.vn/vi/ve-chung-toi/',
        'https://cmcglobal.com.vn/vi/cmc-corporation-vi/',
        'https://cmcglobal.com.vn/vi/contact-us-vi/'
        ]
    docs = load_documents(urls)
    
    vector_db = create_vector_db(collection_name="cmcglobal_aboutus", docs=docs)
    retriever = get_retriver(vector_db)
    
    condense_question_chain = condense_question_prompt | llm | StrOutputParser()
    context_chain = condense_question_chain | retriever
    rag_chain = qa_prompt | llm | StrOutputParser()

    parallel_chain = RunnableParallel({
        "context": lambda x: x["context"],
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["chat_history"]
    })

    rag_with_sources_chain = RunnablePassthrough.assign(
        context=context_chain,
        question=condense_question_chain
    ) | parallel_chain.assign(answer=rag_chain)

    return rag_with_sources_chain

# Example usage
# rag_with_source_chain.invoke(
#     {"input": "văn hóa của CMC Global",
#     "chat_history": chat_history})
    



def get_response(session_id, question):

    # # LLM
    # llm = get_llm()

    chat_history = load_session_history(session_id).messages
    
    chain = get_rag_chain()
    input = {"question": question, "chat_history": chat_history}
    response = chain.invoke(input)

    return response

if __name__ == "__main__":
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process a question with a session ID.")
    parser.add_argument("question", type=str, help="The question to be answered.")
    parser.add_argument("--session_id", type=str, default="abc", help="Session ID for the request.")


    # Parse arguments
    args = parser.parse_args()

    # Extract question and session_id
    question = args.question
    session_id = args.session_id

    # Get response
    response = get_response(session_id, question)
    print(response)

    # question = "CMC Global thành lập khi nào?"
    # session_id = "abc"
    response = get_response(session_id, question)

    

    print(response)