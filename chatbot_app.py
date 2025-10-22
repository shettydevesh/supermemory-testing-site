import streamlit as st
from supermemory import Supermemory
from anthropic import Anthropic
from typing import List
from dotenv import dotenv_values
from general_question_analyzer import get_analyzer

# Load environment variables
config = dotenv_values(".env")

# Initialize clients
@st.cache_resource
def initialize_clients():
    supermemory_client = Supermemory(
        api_key=st.secrets["SUPERMEMORY_API_KEY"],
        # api_key=config['SUPERMEMORY_API_KEY']
    )
    anthropic_client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    # anthropic_client = Anthropic(api_key=config["ANTHROPIC_API_KEY"])
    return supermemory_client, anthropic_client

supermemory, anthropic = initialize_clients()

# System prompt for the LLM
SYSTEM_PROMPT = """You are an intelligent assistant with access to a knowledge base through Supermemory. Your role is to provide accurate, helpful, and contextually relevant responses based on the information retrieved from the knowledge base.

## Core Responsibilities:
1. **Context-Aware Responses**: Use the provided context from Supermemory to answer questions accurately
2. **Cite Sources**: When relevant, reference the information from the knowledge base naturally in your responses
3. **Acknowledge Limitations**: If the retrieved context doesn't contain enough information to answer the question, be honest about it
4. **Maintain Coherence**: Synthesize information from multiple chunks of context into coherent, well-structured answers
5. **Stay Relevant**: Focus on the user's question and avoid unnecessary tangents

## Response Guidelines:
- Be concise yet comprehensive
- Use natural, conversational language
- Structure longer responses with bullet points or numbered lists when appropriate
- If the context is insufficient, explain what information is available and what is missing
- Don't make up information not present in the retrieved context
- If asked about topics outside the knowledge base, politely indicate that you don't have that information

## Tone:
- Professional yet approachable
- Helpful and patient
- Clear and direct

## Output Format:
- Prettify the output using Markdown

Your goal is to be a reliable knowledge assistant that helps users find and understand information from their knowledge base."""

def search_supermemory(query: str, limit: int = 5) -> tuple[List[str], bool]:
    """
    Search Supermemory for relevant context
    Returns: (list of context chunks, whether results were found)
    """
    try:
        results = supermemory.search.documents(
            q=query,
            limit=limit,
        )

        context_chunks = []
        for result in results.results:
            for chunk in result.chunks:
                if chunk.content and chunk.content.strip():
                    context_chunks.append(chunk.content.strip())

        return context_chunks, len(context_chunks) > 0
    except Exception as e:
        st.error(f"Error searching Supermemory: {e}")
        return [], False

def generate_response_stream(query: str, context_chunks: List[str]):
    """
    Generate streaming response using Claude with retrieved context
    """
    if context_chunks:
        context_text = "\n\n---\n\n".join([f"Context {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        user_message = f"""Based on the following context from the knowledge base, please answer the user's question.

Retrieved Context:
{context_text}

User Question: {query}

Please provide a helpful answer based on the context above. If the context doesn't fully answer the question, please say so."""
    else:
        user_message = f"""No relevant context was found in the knowledge base for this question.

User Question: {query}

Please acknowledge that you don't have specific information about this in the knowledge base, but you can provide general assistance if appropriate."""

    try:
        with anthropic.messages.stream(
            model="claude-3-5-haiku-20241022",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception as e:
        yield f"Error generating response: {e}"

# Streamlit UI Configuration
st.set_page_config(
    page_title="Knowledge Base Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ultra-modern UI with glassmorphism
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Light mode (default) */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    /* Main container with glassmorphism */
    .block-container {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Streamlit native chat messages */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 0.75rem 0 !important;
    }

    [data-testid="stChatMessage"][data-testid="stChatMessageUser"] {
        justify-content: flex-end;
    }

    /* Chat message avatars */
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon"] {
        width: 42px !important;
        height: 42px !important;
        border-radius: 50% !important;
    }

    /* User message styling */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse !important;
        margin: 1.5rem 0 !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 1.25rem 1.5rem !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3);
        animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        max-width: 75%;
        margin-left: auto;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }

    /* Assistant message styling */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        margin: 1.5rem 0 !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #1a1a1a !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 1.25rem 1.5rem !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(102, 126, 234, 0.2);
        animation: slideInLeft 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        max-width: 85%;
        font-size: 1rem !important;
        line-height: 1.7 !important;
    }

    /* Message avatars styling */
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
        background: rgba(255, 255, 255, 0.25) !important;
        border: 2px solid white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }

    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        border: 2px solid rgba(240, 147, 251, 0.3) !important;
        box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3) !important;
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateX(0) scale(1);
        }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateX(0) scale(1);
        }
    }

    /* Chat input styling */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(20px);
        border-radius: 20px !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        padding: 0.5rem !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 4px 24px rgba(102, 126, 234, 0.3) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #1a1a1a !important;
        font-size: 15px !important;
        padding: 0.5rem !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #666 !important;
    }

    /* Sidebar glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        border-radius: 12px;
        border: none;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
    }

    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }

    /* Metrics styling */
    [data-testid="stMetric"] {
        background: rgba(102, 126, 234, 0.1);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.1) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
        border-right-color: transparent !important;
    }

    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }

    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }

        .block-container {
            background: rgba(30, 30, 46, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {
            background: linear-gradient(135deg, #5b6fd8 0%, #6b46c1 100%) !important;
            box-shadow: 0 6px 20px rgba(91, 111, 216, 0.5) !important;
            border: 2px solid rgba(255, 255, 255, 0.2);
            color: #ffffff !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {
            background: rgba(40, 40, 56, 0.95) !important;
            color: #e4e4e7 !important;
            border: 2px solid rgba(91, 111, 216, 0.3);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
        }

        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
            background: rgba(91, 111, 216, 0.3) !important;
            border: 2px solid rgba(91, 111, 216, 0.5) !important;
        }

        [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            border: 2px solid rgba(240, 147, 251, 0.4) !important;
        }

        [data-testid="stChatInput"] {
            background: rgba(40, 40, 56, 0.9) !important;
            border: 2px solid rgba(91, 111, 216, 0.3) !important;
        }

        [data-testid="stChatInput"] textarea {
            color: #e4e4e7 !important;
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: #a1a1aa !important;
        }

        [data-testid="stSidebar"] {
            background: rgba(30, 30, 46, 0.75) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        [data-testid="stMetric"] {
            background: rgba(91, 111, 216, 0.15);
            border: 1px solid rgba(91, 111, 216, 0.3);
        }

        .streamlit-expanderHeader {
            background: rgba(91, 111, 216, 0.15) !important;
            border: 1px solid rgba(91, 111, 216, 0.3) !important;
        }
    }

    /* Streamlit dark theme override */
    [data-testid="stAppViewContainer"][data-theme="dark"] .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] .block-container {
        background: rgba(30, 30, 46, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {
        background: linear-gradient(135deg, #5b6fd8 0%, #6b46c1 100%) !important;
        box-shadow: 0 6px 20px rgba(91, 111, 216, 0.5) !important;
        border: 2px solid rgba(255, 255, 255, 0.2);
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {
        background: rgba(40, 40, 56, 0.95) !important;
        color: #e4e4e7 !important;
        border: 2px solid rgba(91, 111, 216, 0.3);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
        background: rgba(91, 111, 216, 0.3) !important;
        border: 2px solid rgba(91, 111, 216, 0.5) !important;
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        border: 2px solid rgba(240, 147, 251, 0.4) !important;
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] [data-testid="stChatInput"] {
        background: rgba(40, 40, 56, 0.9) !important;
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] [data-testid="stChatInput"] textarea {
        color: #e4e4e7 !important;
    }

    [data-testid="stAppViewContainer"][data-theme="dark"] [data-testid="stSidebar"] {
        background: rgba(30, 30, 46, 0.75) !important;
    }

    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }

    /* Typing indicator */
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }

    .typing-indicator span {
        animation: typing 1.4s infinite;
        display: inline-block;
    }

    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")

    st.markdown("### 🎨 Display Options")
    show_context = st.checkbox("Show retrieved context", value=False, help="Display the context chunks retrieved from Supermemory")
    context_limit = st.slider(
        "Number of context chunks",
        min_value=1,
        max_value=10,
        value=5,
        help="More chunks provide more context but may slow down responses"
    )

    st.divider()

    st.markdown("### 📊 Session Stats")
    message_count = len(st.session_state.get("messages", []))
    st.metric("Messages", message_count)

    st.divider()

    st.markdown("""
    ### 💡 About
    This intelligent chatbot combines:
    - **Supermemory** - Lightning-fast knowledge retrieval
    - **Claude 3.5 Haiku** - Advanced AI responses

    **Features:**
    - Real-time streaming responses
    - Context-aware answers
    - Dark mode support
    - Beautiful, modern UI
    """)

    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("🤖 Knowledge Base Chatbot")
st.markdown("💬 Ask me anything about your knowledge base - I'll search and provide intelligent answers!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display welcome message if no chat history
if len(st.session_state.messages) == 0:
    st.markdown("""
        <div style='text-align: center; padding: 3rem 2rem; margin: 2rem 0;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>🤖</div>
            <h2 style='color: rgba(102, 126, 234, 0.9); margin-bottom: 0.5rem;'>Welcome to Your Knowledge Assistant!</h2>
            <p style='color: rgba(0, 0, 0, 0.6); font-size: 1.1rem; margin-bottom: 2rem;'>
                I'm here to help you explore your knowledge base. Ask me anything!
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; max-width: 600px; margin: 0 auto;'>
                <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 12px; border: 1px solid rgba(102, 126, 234, 0.2);'>
                    <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🔍</div>
                    <p style='margin: 0; font-size: 0.9rem; color: rgba(0, 0, 0, 0.7);'>Smart Search</p>
                </div>
                <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 12px; border: 1px solid rgba(102, 126, 234, 0.2);'>
                    <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>⚡</div>
                    <p style='margin: 0; font-size: 0.9rem; color: rgba(0, 0, 0, 0.7);'>Fast Responses</p>
                </div>
                <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 12px; border: 1px solid rgba(102, 126, 234, 0.2);'>
                    <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🎯</div>
                    <p style='margin: 0; font-size: 0.9rem; color: rgba(0, 0, 0, 0.7);'>Context-Aware</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Display chat history using Streamlit's native chat components
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

        # Show context if it's an assistant message and context viewing is enabled
        if message["role"] == "assistant" and show_context and "context" in message and message["context"]:
            with st.expander("📚 View Retrieved Context", expanded=False):
                for i, ctx in enumerate(message["context"], 1):
                    st.markdown(f"**Context {i}:**")
                    st.text(ctx)
                    if i < len(message["context"]):
                        st.divider()

# Chat input
if prompt := st.chat_input("Type your question here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # ANALYZER: Check if this is a general question (early exit optimization)
    analyzer = get_analyzer()
    is_general, quick_response = analyzer.analyze(prompt)

    if is_general:
        # Quick response path - skip expensive Supermemory search
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            # Simulate streaming for consistency (but it's instant)
            message_placeholder.markdown(quick_response)

        # Add assistant response to chat history (no context for general questions)
        st.session_state.messages.append({
            "role": "assistant",
            "content": quick_response,
            "context": []
        })
    else:
        # Normal path - search Supermemory for knowledge-based queries
        # Search Supermemory
        with st.spinner("🔍 Searching knowledge base..."):
            context_chunks, found = search_supermemory(prompt, limit=context_limit)

        # Display assistant message with streaming
        with st.chat_message("assistant", avatar="🤖"):
            message_placeholder = st.empty()
            full_response = ""

            # Stream the response
            for chunk in generate_response_stream(prompt, context_chunks):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            # Final message without cursor
            message_placeholder.markdown(full_response)

            # Show context if enabled
            if show_context and context_chunks:
                with st.expander("📚 View Retrieved Context", expanded=False):
                    for i, ctx in enumerate(context_chunks, 1):
                        st.markdown(f"**Context {i}:**")
                        st.text(ctx)
                        if i < len(context_chunks):
                            st.divider()

        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "context": context_chunks
        })

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='color: rgba(102, 126, 234, 0.8); font-size: 0.9rem; font-weight: 500; margin: 0;'>
            ✨ Powered by <strong>Supermemory</strong> & <strong>Claude 3.5 Haiku</strong>
        </p>
        <p style='color: rgba(102, 126, 234, 0.6); font-size: 0.8rem; margin-top: 0.25rem;'>
            Built with ❤️ using Streamlit
        </p>
    </div>
""", unsafe_allow_html=True)
