import streamlit as st
import pandas as pd

st.title("Bake-An-Agent")
st.write("Build agents in Databricks with no code")


st.page_link("app.py", label="Home", icon="🏠")
st.page_link("pages/Build agent.py", label="Build agent", icon="🏗️")
st.page_link("pages/Try agent.py", label="Try agent", icon="🧪")
st.page_link("pages/Deploy agent.py", label="Deploy agent", icon="🚚")
st.page_link("pages/Test deployed agent.py", label="Test deployed agent", icon="🧪", disabled=True)


# st.subheader("What is it?")
# st.write("...")

