import streamlit as st
import pandas as pd

import os
import requests
import numpy as np
import json

from openai import OpenAI

import streamlit as st
# import auth

from databricks.sdk import WorkspaceClient
w = WorkspaceClient(profile='dogfood')

st.set_page_config(layout="wide")

endpoint_name = "agents_main-demo_mlo-cookie_agent_mlo"

st.title("🍰 Try out agent")
st.write(f"Test the freshly baked agent (`{endpoint_name}`)")

try: 
    from pyspark.dbutils import DBUtils
    user_info = auth.get_user_info()
except ImportError:
    user_info = {}
    user_info['access_token'] = w.dbutils.secrets.get("mikelo", "pat")

if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

client = OpenAI(
    api_key=user_info.get("access_token"),
    base_url=os.getenv("FMAPI_URL"),
)

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
        stream = client.chat.completions.create(
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            model=endpoint_name,
            stream=True,
        )
        response = st.write_stream(stream)
        
        # stream_content = stream.choices[0].message.content
        # response = st.write(stream_content)
        
        # for chunk in stream:
        #     st.write_stream(chunk.choices[0].delta.content)
        # response = st.write_stream(stream.choices[0].message.content)
        # st.balloons()

    # Add assistant response to chat history
    # st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": stream_content})