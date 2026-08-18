# importing required libraries
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START,END
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

# loading environmental variables
load_dotenv()

# setting total rounds of the game
# maximum words
total_rounds = 5
max_words = 100
topic = "AI art should be fully copyrightable."

# declaring prompt for first llm model
system_prompt1 = """
You are Debater A, arguing FOR the following resolution:
"{TOPIC}"

Rules:
- Stay in character as a skilled, persuasive debater. Never break character or acknowledge you're an AI.
- Argue only the PRO/affirmative side, even if you personally find the opposing side more convincing.
- Make substantive arguments: use logic, evidence, and real-world examples. Avoid empty rhetoric.
- Directly rebut your opponent's previous argument before advancing your own points.
- Keep each turn to {MAX_WORDS} words.
- Write in plain, simple language. Avoid jargon, technical terms, and long, complex sentences —
  a general reader should be able to follow your point on a first read.
- Do not concede the debate or soften your position — your job is to make the strongest possible case for PRO.
- This is round {ROUND_NUMBER} of {TOTAL_ROUNDS}.

Opponent's last argument:
{OPPONENT_LAST_MESSAGE}

Respond with your argument for this round.
"""

# declaring prompt for second llm model
system_prompt2 = """
You are Debater B, arguing AGAINST the following resolution:
"{TOPIC}"

Rules:
- Stay in character as a skilled, persuasive debater. Never break character or acknowledge you're an AI.
- Argue only the CON/negative side, even if you personally find the opposing side more convincing.
- Make substantive arguments: use logic, evidence, and real-world examples. Avoid empty rhetoric.
- Directly rebut your opponent's previous argument before advancing your own points.
- Keep each turn to {MAX_WORDS} words.
- Write in plain, simple language. Avoid jargon, technical terms, and long, complex sentences —
  a general reader should be able to follow your point on a first read.
- Do not concede the debate or soften your position — your job is to make the strongest possible case for CON.
- This is round {ROUND_NUMBER} of {TOTAL_ROUNDS}.

Opponent's last argument:
{OPPONENT_LAST_MESSAGE}

Respond with your argument for this round.
"""

# prompt - model1
# using chatPromptTemplate
prompt1 = ChatPromptTemplate.from_messages([
    ("system",system_prompt1)
])

# prompt - model2
# using ChatPromptTemplate
prompt2 = ChatPromptTemplate.from_messages([
    ("system",system_prompt2)
])

# initialize model 1
first_llm_model = init_chat_model(
    model_provider="groq",
    model="openai/gpt-oss-20b"
)

# initialize model 2
second_llm_model = init_chat_model(
    model_provider="groq",
    model="openai/gpt-oss-120b"
)

# declaring class
class DebateState(TypedDict):
    messages:Annotated[list,add_messages]
    loop_count:int

# model A node function
def first_model_node(state:DebateState):
    history = state['messages']
    loop_count = state['loop_count']
    last_msg = history[-1].content if history else "The debate is opening. Give your opening statement."

    chain = prompt1 | first_llm_model
    response = chain.invoke({
        "TOPIC":topic,
        "MAX_WORDS":max_words,
        "ROUND_NUMBER":loop_count,
        "TOTAL_ROUNDS":total_rounds,
        "OPPONENT_LAST_MESSAGE":last_msg
    })
    response.name = "Debate Model A"
    return {"messages":[response],"loop_count":loop_count+1}

# Model B node function
def second_model_node(state:DebateState):
    history = state["messages"]
    loop_count = state["loop_count"]
    last_msg = history[-1].content if history else "The debate is opening. Give your opening statement."

    chain = prompt2 | second_llm_model
    response = chain.invoke({
        "TOPIC":topic,
        "MAX_WORDS":max_words,
        "ROUND_NUMBER":loop_count,
        "TOTAL_ROUNDS":total_rounds,
        "OPPONENT_LAST_MESSAGE":last_msg
    })
    response.name = "Debate Model B"
    return {"messages":[response], "loop_count":loop_count+1}

# continue loop condition (node)
def continue_condition(state:DebateState):
    loop_count = state["loop_count"]

    if loop_count>=total_rounds:
        return "end_debate"

    return "continue_debate"

# building the graph
builder = StateGraph(state_schema=DebateState)

# creating nodes
# connecting with edges
builder.add_node("first_model_node",first_model_node)
builder.add_node("second_model_node",second_model_node)
#builder.add_nodel("continue_node",continue_condition)

builder.add_edge(START,"first_model_node")
builder.add_edge("first_model_node","second_model_node")
builder.add_conditional_edges(
    "second_model_node",
    continue_condition,
    {
        "continue_debate":"first_model_node",
        "end_debate":END
    }
)

# initiate memory_saver
memory = MemorySaver()

# compile 
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "debate_session_001"}}
    pass
