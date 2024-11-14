from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

### Contextualize question ###
condense_question_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, your task is to formulate it into a standalone question \
which can be understood without the chat history.
Note that, you ARE NOT ALLOWED answer the question, only output the rephrased question"""

#  Do NOT answer the question, just reformulate it if needed and otherwise return it as is.
condense_question_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", condense_question_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ]
)


### Answer question ###
qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ]
)