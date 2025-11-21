import streamlit as st
from bedrock_utils import query_knowledge_base, generate_response, valid_prompt, is_valid_kb_id

# Streamlit UI
st.title("Bedrock Chat Application")

# Sidebar for configurations
st.sidebar.header("Configuration")

model_id = st.sidebar.selectbox(
    "Select LLM Model",
    ["anthropic.claude-3-haiku-20240307-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0", "anthropic.claude-3-5-sonnet-20240620-v1:0","anthropic.claude-3-5-haiku-20241022-v1:0"],
)

kb_id = st.sidebar.text_input("Knowledge Base ID")

temperature = st.sidebar.select_slider(
    "Temperature",
    [i/10 for i in range(0,11)],
    0.1,
    help="Higher = more creative and unpredictable, lower = more consistent and focused"
)

top_p = st.sidebar.select_slider(
    "Top_P",
    [i/1000 for i in range(0,1001)],
    0.1,
    help="Controls word choice variety - keep low for technical topics"
)

min_prompt_length = st.sidebar.select_slider(
    "Min Prompt Length",
    [i for i in range(5,100,5)],
    20,
    help="Prompts shorter than this value will be rejected"
)

# Initialize session state
if "valid_kb" not in st.session_state:
    st.session_state.valid_kb = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "previous_kb_id" not in st.session_state:
    st.session_state.previous_kb_id = None

# Dialog definitions
@st.dialog("Knowledge Base ID Required", dismissible=False)
def kb_id_dialog():
    st.error("Invalid or missing Knowledge Base ID.")
    st.write("Enter a valid Knowledge Base ID in the sidebar, then click OK to continue.")
    if st.button("OK"):
        st.rerun()

@st.dialog("Thanks for entering Valid ID", dismissible=True)
def correct_kb():
    st.success("Let's Chat!")

# Track KB ID changes and validate
kb_id_changed = (st.session_state.previous_kb_id != kb_id)

if kb_id_changed and kb_id and kb_id.strip():
    if is_valid_kb_id(kb_id.strip()):
        if not st.session_state.valid_kb:
            correct_kb()
            st.session_state.valid_kb = True
    else:
        st.session_state.valid_kb = False

st.session_state.previous_kb_id = kb_id

# Chat interface
with st.chat_message("assistant"):
    st.write("Hello human! I am your assistant! I am here to help you with your Heavy Machinery questions. How can I assist you today?")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    if not kb_id or not kb_id.strip():
        kb_id_dialog()
        st.stop()
    
    if not is_valid_kb_id(kb_id.strip()):
        kb_id_dialog()
        st.stop()

    prompt_result = valid_prompt(prompt, model_id, min_prompt_length)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if prompt_result["allowed"]:
        kb_results = query_knowledge_base(prompt, kb_id)
        context = "\n".join([kb_result['content']['text'] for kb_result in kb_results])
        full_prompt = f"Context: {context}\n\nUser: {prompt}\n\n"
        response = generate_response(full_prompt, model_id, temperature, top_p)
    else:
        response = "I'm unable to answer this, please try again"
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})