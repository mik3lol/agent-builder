import streamlit as st
import pandas as pd
from databricks.sdk import WorkspaceClient
import yaml

w = WorkspaceClient(profile='dogfood')

st.set_page_config(layout="wide")

st.title("Pick your tools")
st.write("Choose tools to use.")

n_cols = 3
cols = st.columns(2)

catalogs = [x.name for x in w.catalogs.list()]
catalog = cols[0].selectbox("Catalog", catalogs, index=None)
if catalog:
    schemas = [x.name for x in w.schemas.list(catalog)]
    schema = cols[1].selectbox("Schema", schemas, index=None)
else: 
    # Placeholder
    schema = cols[1].selectbox("Schema", [], index=None)
    # if schema:
    #     volumes = [x.name for x in w.volumes.list(catalog, schema)]
    #     volume = st.selectbox("Volume", volumes, index=None)

# catalog = cols[0].text_input("Catalog", "main")
# schema = cols[1].text_input("Schema", "cookie")

res = []
try: 
    res = list(w.functions.list(catalog, schema))
except Exception as e:
    st.warning("Please choose a catalog")
    # st.error(f"{e}")
    st.stop()

n_rows = len(res) // n_cols + 1

# st.subheader("Available hosted functions")
selected = {x.name for x in res}
checked = [0] * len(res)

# show available hosted functions
# TODO
st.subheader(f"Available functions in `{catalog}.{schema}`")
k = 0
for i in range(0, n_rows):
    cols = st.columns(n_cols)
    for j in range(0, n_cols):
        if k < len(res):
            item = res[k]
            cols[j].subheader(f"🔧 `{item.name}`")
            cols[j].write(f"{item.comment}")
            checked[k] = cols[j].toggle(f"Use `{item.name}` [{k}]")
            k += 1

func_names = []
for idx, val in enumerate(checked):
    if val is True:
        func_names.append(res[idx].full_name)


# st.write(checked)
# st.write(func_names)

# Update config.yaml
if any(checked):
    # Load the YAML file
    with open("config.yml", "r") as f:
        configs = yaml.safe_load(f)

    # Provide a default value if the file is empty or malformed
    configs = configs or {}

    # Update the field
    # configs.setdefault("field_to_update", "default_value")
    configs["uc_functions"] = func_names

    # Save the updated YAML file
    with open("config.yml", "w") as f:
        yaml.safe_dump(configs, f, default_flow_style=False)
            