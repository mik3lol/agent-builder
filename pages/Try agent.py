import mlflow
from mlflow.models import ModelConfig
import os
import streamlit as st

from langchain_community.chat_models import ChatDatabricks
from langchain_community.tools.databricks import UCFunctionToolkit

from dataclasses import asdict
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import create_react_agent
from mlflow.models import rag_signatures

@st.cache_resource
def create_agent():
    # Define our chat model and tools
    # Create a LangChain chat model that supports tool calling

    mlflow.langchain.autolog()
    config = ModelConfig(development_config="./config.yml")

    # Create the llm
    llm = ChatDatabricks(
        endpoint=config.get("llm_endpoint")
    )

    # Create the uc function tools
    uc_function_tools = (
        UCFunctionToolkit(
            warehouse_id=config.get("warehouse_id")
        )
        .include(*config.get("uc_functions"))
        .get_tools()
    )

    # Create the agent
    # create_react_agent is a prebuilt langgraph function that builds a simple graph with a model and tools node - reference

    # Create the agent
    system_message = config.get("agent_prompt")
    agent = create_react_agent(llm, uc_function_tools, state_modifier=system_message)

    # Wrap the input/output schemas to be ChatCompletions compatible
    # This allows us to take advantage of agent framework features like streaming and payload logging
    def wrap_lg(input):
        if not isinstance(input, dict):
            if isinstance(input, list) and len(input) > 0:
                # Extract the content from the HumanMessage
                content = input[-1].content.strip("\"")
                input = {"messages": [{"role": "user", "content": content}]}
        return agent.invoke(input)


    chain = RunnableLambda(wrap_lg) | RunnableLambda(
        lambda response: asdict(
            rag_signatures.ChatCompletionResponse(
                choices=[
                    rag_signatures.ChainCompletionChoice(
                        message=rag_signatures.Message(
                            content=response["messages"][-1].content
                        )
                    )
                ]
            )
        )
    )

    mlflow.models.set_model(chain)
    return chain

chain = create_agent()

st.title("🍰 Try out the agent")

if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # TODO: replace this placeholder input example with an appropriate domain-specific example for your agent
        response = chain.invoke({'messages': [{"role": "user", "content": prompt}]})
        response = response['choices'][0]['message']['content']
        st.write(response)
        # response = st.write(response)

        # stream = client.chat.completions.create(
        #     messages=[
        #         {"role": m["role"], "content": m["content"]}
        #         for m in st.session_state.messages
        #     ],
        #     model=endpoint_name,
        #     stream=True,
        # )
        
        # stream_content = stream.choices[0].message.content
        # response = st.write(stream_content)
        
        # for chunk in stream:
        #     st.write_stream(chunk.choices[0].delta.content)
        # response = st.write_stream(stream.choices[0].message.content)
        # st.balloons()

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
