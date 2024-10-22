# Databricks notebook source
# MAGIC %md
# MAGIC #Agent Notebook
# MAGIC **TODO**: Before running this notebook, go to `config.yml` in this folder and replace the `warehouse_id` with your SQL warehouse ID. The tools available to your agent are also defined in the config file under `uc_functions`.
# MAGIC
# MAGIC - This is one of a set of auto-generated notebooks exported from the AI playground that define and deploy an agent using Mosaic AI Agent Framework ([AWS](https://docs.databricks.com/en/generative-ai/retrieval-augmented-generation.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/retrieval-augmented-generation)).
# MAGIC - This notebook defines a LangChain agent that has access to the tools from the source playground session
# MAGIC - Then, iterate and modify the agent defined in this notebook (e.g. add more tools or change the system prompt)
# MAGIC - After iterating and testing your agent, go to the generated `driver` notebook in this folder to log, register, and deploy it. Once your agent is deployed, you can chat with it in AI playground to perform additional checks, share it with SMEs in your organization for feedback, or embed it in a production application. See docs ([AWS](https://docs.databricks.com/en/generative-ai/deploy-agent.html) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/deploy-agent)) for details

# COMMAND ----------

# MAGIC %pip install -U -qqqq mlflow-skinny langchain langchain_core langchain_community langgraph pydantic
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import mlflow
from mlflow.models import ModelConfig

mlflow.langchain.autolog()
config = ModelConfig(development_config="/Workspace/Users/mike.lo@databricks.com/agent-playground/config.yml")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Define our chat model and tools
# MAGIC - Create a LangChain chat model that supports tool calling
# MAGIC - Define our agent's tools
# MAGIC     - Modify the tools your agent has access to by modifying the `uc_functions` list in `config.yml`

# COMMAND ----------

from langchain_community.chat_models import ChatDatabricks
from langchain_community.tools.databricks import UCFunctionToolkit

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



# COMMAND ----------

# MAGIC %md
# MAGIC ### Create the agent
# MAGIC - `create_react_agent` is a prebuilt langgraph function that builds a simple graph with a model and tools node - [reference](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/#usage)

# COMMAND ----------

from dataclasses import asdict
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import create_react_agent
from mlflow.models import rag_signatures

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

# mlflow.models.set_model(chain)

# Test the agent
# TODO: replace this placeholder input example with an appropriate domain-specific example for your agent
chain.invoke({'messages': [{"role": "user", "content": "what are the available franchises in the USA?"}]})