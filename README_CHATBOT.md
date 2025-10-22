# Knowledge Base Chatbot

A beautiful, modern chatbot interface built with Streamlit that uses Supermemory for knowledge retrieval and Claude for intelligent responses.

## Features

- **Modern Chat Interface**: Clean, user-friendly chat UI with message history
- **Smart Context Retrieval**: Uses Supermemory to find relevant information from your knowledge base
- **AI-Powered Responses**: Claude generates intelligent, context-aware answers
- **Customizable Settings**: Adjust number of context chunks and toggle context visibility
- **Responsive Design**: Works great on desktop and mobile devices

## System Prompt

The LLM agent uses a carefully crafted system prompt that ensures:

1. **Context-Aware Responses**: Uses retrieved knowledge base information accurately
2. **Source Citation**: References information naturally in responses
3. **Honest Limitations**: Acknowledges when information is insufficient
4. **Coherent Synthesis**: Combines multiple context chunks into clear answers
5. **Professional Tone**: Maintains helpful, approachable communication

## Setup

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Environment Variables**:
   Make sure your `.env` file contains:
   ```
   SUPERMEMORY_API_KEY=your_supermemory_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

3. **Upload Documents to Supermemory** (if not already done):
   ```python
   from supermemory import Supermemory

   client = Supermemory(api_key="your_api_key")

   with open("your_document.docx", 'rb') as file:
       result = client.memories.upload_file(
           file=file,
           container_tags=["tag1", "tag2"]
       )
   ```

## Running the Application

Start the chatbot with:

```bash
uv run streamlit run chatbot_app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

1. **Ask Questions**: Type your question in the chat input at the bottom
2. **View Context**: Toggle "Show retrieved context" in the sidebar to see what information was used
3. **Adjust Settings**: Use the slider to change how many context chunks are retrieved (1-10)
4. **Clear History**: Click "Clear Chat History" in the sidebar to start fresh

## How It Works

1. **User Input**: You ask a question through the chat interface
2. **Context Retrieval**: The app searches Supermemory for relevant information
3. **Response Generation**: Claude uses the retrieved context to generate an accurate answer
4. **Display**: The response is shown in the chat with optional context visibility

## Customization

### Modify the System Prompt

Edit the `SYSTEM_PROMPT` variable in `chatbot_app.py` (lines 27-50) to customize the LLM's behavior.

### Adjust UI Styling

Modify the CSS in the `st.markdown()` call (lines 105-135) to change colors, spacing, and layout.

## Features in Detail

### Context Display
When enabled, you can see exactly what information was retrieved from your knowledge base, helping you understand how the AI arrived at its answer.

### Smart Search
The app searches your Supermemory knowledge base with configurable limits, retrieving the most relevant chunks of information.

### Conversation History
All messages are preserved during the session, allowing you to refer back to previous answers and maintain context throughout the conversation.

## Troubleshooting

- **API Key Errors**: Ensure your `.env` file contains valid API keys
- **No Context Found**: Make sure you've uploaded documents to Supermemory with searchable content
- **Slow Responses**: Reduce the number of context chunks in the sidebar settings
- **Connection Issues**: Check your internet connection and API service status

## Tech Stack

- **Streamlit**: Web framework for the UI
- **Supermemory**: Knowledge base retrieval system
- **Claude (Anthropic)**: AI model for generating responses
- **Python-dotenv**: Environment variable management
