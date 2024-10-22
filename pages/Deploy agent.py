import streamlit as st
import pandas as pd
from databricks.sdk import WorkspaceClient
import time

st.set_page_config(layout="wide")

st.title("Bake your agent")
st.write("Agent looks good? Let's bake and serve it.")

cols = st.columns(3)

# Log agent
st.markdown("## ⏲️ Bake the agent in MLflow")
# cols[0].caption("")

log_agent = st.button('Log agent')

if log_agent: 
    # Log the model to MLflow
    import os
    # import mlflow
    with st.spinner('Wait for it...'):
        time.sleep(3)

#     input_example = {'messages': [{"role": "user", "content": 'What is RAG?'}]}

#     logged_chain_info = []
#     # with mlflow.start_run():
#     #     logged_chain_info = mlflow.langchain.log_model(
#     #         lc_model=os.path.join(os.getcwd(), 'agent'),
#     #         model_config=os.path.join(os.getcwd(), "config.yml"),
#     #         artifact_path=os.path.join(os.getcwd(), 'agent'),
#     #         input_example=input_example,
#     #     )

# cols[1].markdown("## ➡️")

# Register in UC
st.markdown("## 📦 Box the agent in Unity Catalog")
UC_MODEL_NAME = st.text_input("Destination in Unity Catalog", "main.cookie.my_agent")
st.button('Register model')

# # register the model to UC
# mlflow.set_registry_uri("databricks-uc")
# uc_registered_model_info = mlflow.register_model(model_uri=logged_chain_info.model_uri, name=UC_MODEL_NAME)


# cols[3].markdown("## ➡️")

# Create endpoint
st.markdown('## 🚚 Deliver agent to serving endpoint')
st.button('Serve it!')

# st.subheader("Deploy agent to serving endpoint")
# # Every form must have a submit button.
# deployed = st.button("Deploy agent")

# log_agent = st.button("Log agent to MLflow")


st.write("## Agent assets")
st.write(f"""
         * MLflow experiment [link]()
         * Review app [link]()  
         * Model serving endpoint [link]()
         """)