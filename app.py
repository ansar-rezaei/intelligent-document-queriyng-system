import streamlit as st
from bedrock_utils import query_knowledge_base, generate_response, valid_prompt, is_valid_kb_id, format_sources

st.set_page_config(
    page_title="Heavy Machinery Copilot",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit UI
st.title("Heavy Machinery Copilot")

# Sidebar for configurations
st.sidebar.header("Configuration")

model_id = st.sidebar.selectbox(
    "Select LLM Model",
    ["anthropic.claude-3-haiku-20240307-v1:0", "anthropic.claude-3-sonnet-20240229-v1:0", "anthropic.claude-3-5-sonnet-20240620-v1:0","anthropic.claude-3-5-haiku-20241022-v1:0"],
)

kb_id = st.sidebar.text_input(
    "Knowledge Base ID",
    "WFVBDOSYOR"
)

temperature = st.sidebar.select_slider(
    "Temperature",
    [i/10 for i in range(0,11)],
    0.3,
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
    10,
    help="Prompts shorter than this value will be rejected"
)

num_kb_results = st.sidebar.slider(
    "Number of KB Results",
    min_value=1,
    max_value=10,
    value=3,
    help="More results = better context but slower/more expensive"
)

max_tokens = st.sidebar.slider(
    "Max Response Tokens",
    min_value=100,
    max_value=1000,
    value=300,
    step=50,
    help="Maximum length of response - higher = longer answers but more expensive"
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
with st.chat_message("assistant", avatar="🤖"):
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

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user",avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.status("Let's work on your request...", expanded=True) as status:
        st.write("🔍 Validating the prompt...")
        prompt_result = valid_prompt(prompt, model_id, min_prompt_length)
        
        kb_results = []
        if prompt_result["allowed"]:
            st.write("✅Valid Request...")
            st.write("📚 Searching KB...")
            kb_results = query_knowledge_base(prompt, kb_id, num_kb_results)
            st.write("🤖 Generating...")
            context = "\n".join([kb_result['content']['text'] for kb_result in kb_results])
            full_prompt = f"Context: {context}\n\nUser: {prompt}\n\n"
            response = generate_response(full_prompt, model_id, temperature, top_p, max_tokens)
            status.update(label="✅ Complete!", state="complete", expanded=False)
        else:
            status.update(label="❌ Validation failed", state="error")
            st.write(prompt_result["category"])
            st.write(prompt_result["name"])
            st.write(prompt_result["reason"])
            response = "I'm unable to answer this, please try again"


    
    with st.chat_message("assistant",avatar="🤖"):
        st.markdown(response)

        if prompt_result["allowed"] and kb_results:
            with st.expander("📚 Click here to see the Sources", expanded=False):
                for src in format_sources(kb_results):
                    st.markdown(f"""
                            **Source {src['index']}** (Confidence: {src['confidence_score']:.2%}")

                            - **File:** `{src['file_path']}`
                            - **Preview:** {src['text_snippet']}...

                            ---
                            """)

    st.session_state.messages.append({"role": "assistant", "content": response})