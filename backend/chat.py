from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class State(TypedDict, total=False):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    # Context contains the retrieved information from the vector database
    # Using total=False to make context optional
    context: str


CHROMA_PATH = "chroma"
graph_builder = StateGraph(State)

import os
from langchain.chat_models import init_chat_model


llm = init_chat_model("openai:gpt-4.1")

def chatbot(state: State):
    # The context_text is passed as part of the state in the "context" key
    messages = state["messages"]
    
    # If there's context available, add it as a system message at the beginning
    if "context" in state and state["context"]:
        context_message = {
            "role": "system",
            "content": f"You are an assistant that helps employers decide whether to hire Max Gaspers Scott. Use this information to provide accurate responses:\n\n{state['context']}"
        }
        # Create a new list with the system message first, followed by user messages
        messages_with_context = [context_message] + messages
        return {"messages": [llm.invoke(messages_with_context)]}
    else:
        # If no context is available, proceed with regular messages
        return {"messages": [llm.invoke(messages)]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()

embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)


def stream_graph_updates(user_input: str):
    # Search the DB.
    results = db.similarity_search_with_relevance_scores(user_input, k=3)
    if len(results) == 0: # or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    print(context_text)
    print("")
    # Include the context_text in the state when streaming the graph
    for event in graph.stream({
        "messages": [{"role": "user", "content": user_input}],
        "context": context_text
    }):
        for value in event.values():
            return " ", value["messages"][-1].content


# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#         stream_graph_updates(user_input)
#     except:
#         # fallback if input() is not available
#         user_input = "What do you know about LangGraph?"
#         print("User: " + user_input)
#         stream_graph_updates(user_input)
#         break


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Question(BaseModel):
    text: str

async def generate_complete_response(text: str):
    """Generate a complete response without streaming"""
    # Search the DB
    results = db.similarity_search_with_relevance_scores(text, k=3)
    if len(results) == 0:  # or results[0][1] < 0.7:
        return "Unable to find matching results."
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    
    # Collect the complete response
    complete_response = ""
    for event in graph.stream({
        "messages": [{"role": "user", "content": text}],
        "context": context_text
    }):
        for value in event.values():
            complete_response = value["messages"][-1].content
    
    return complete_response

@app.post("/chat")
async def root(question: Question):
    # Parse the text from the request body
    text = question.text
    
    # Generate the complete response
    response_text = await generate_complete_response(text)
    
    # Return as JSON
    return {"message": response_text}
