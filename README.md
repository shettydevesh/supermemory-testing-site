# Claude Chatbot - Brittannia

A web-based chatbot interface powered by Claude AI with document upload capabilities to Supermemory.

## Features

- Interactive chat interface with Claude AI
- Upload files from the `docs/` folder to Supermemory with "brittannia" container tag
- Upload individual files through the web interface
- Session-based conversation history
- Beautiful, responsive UI

## Project Structure

```
.
├── app.py                  # Flask web application
├── processor.py            # Document processor for Supermemory
├── templates/
│   └── index.html          # Chat interface UI
├── docs/                   # Folder containing documents to upload
├── .env                    # Environment variables (API keys)
└── pyproject.toml          # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file and add your API keys:

```env
SUPERMEMORY_API_KEY="your_supermemory_api_key"
ANTHROPIC_API_KEY="your_anthropic_api_key"
```

To get your Anthropic API key:
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### Chat Interface

1. Open your browser and navigate to `http://localhost:5000`
2. Type your message in the input field
3. Press Enter or click "Send" to chat with Claude
4. Click "Clear Chat" to reset the conversation

### Upload Files

#### Option 1: Upload All Files from docs/ Folder
1. Click the "Upload Files" button in the header
2. Select "Upload All Files from docs/ folder"
3. All files in the `docs/` directory will be uploaded to Supermemory with:
   - Container tag: "brittannia"
   - Additional tag: filename (without extension)

#### Option 2: Upload Single File
1. Click the "Upload Files" button in the header
2. Select "Upload Single File"
3. Choose a file from your computer
4. The file will be uploaded with:
   - Container tag: "brittannia"
   - Additional tag: filename (without extension)

## API Endpoints

### POST /api/chat
Send a message to Claude and receive a response.

**Request:**
```json
{
  "message": "Hello, Claude!",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Hello! How can I help you today?",
  "session_id": "session-uuid"
}
```

### POST /api/upload-docs
Upload all files from the `docs/` folder to Supermemory.

**Response:**
```json
{
  "message": "Processed 6 files",
  "results": [
    {
      "file": "brand_context.docx",
      "status": "success",
      "result": {...}
    }
  ]
}
```

### POST /api/upload-single
Upload a single file via multipart form data.

**Request:**
- Form data with file field

**Response:**
```json
{
  "message": "File uploaded successfully",
  "result": {...}
}
```

### POST /api/clear-session
Clear conversation history for a session.

**Request:**
```json
{
  "session_id": "session-uuid"
}
```

## Files in docs/ Folder

Current documents:
- approved_ideas.docx
- brand_context.docx
- brand_data.pdf
- meta_analysis.xlsx
- rejected_ideas_deck.pptx
- rejected_ideas.docx

## Development

### Modifying the UI

Edit `templates/index.html` to customize the chat interface appearance and behavior.

### Adding Features

The Flask app (`app.py`) can be extended with additional routes and functionality. The document processor (`processor.py`) handles all Supermemory interactions.

## Notes

- Each file uploaded is tagged with "brittannia" as the primary container
- The filename (without extension) is added as an additional tag for easy organization
- Conversation history is stored in memory and will be lost when the server restarts
- The chat uses Claude 3.5 Sonnet model for responses

## Troubleshooting

**Error: Missing API key**
- Make sure you've added both API keys to the `.env` file
- Ensure the `.env` file is in the project root directory

**Error: Module not found**
- Run `uv sync` or `pip install` to install all dependencies

**Error: Cannot find docs folder**
- Make sure the `docs/` folder exists in the project root
- Check file permissions

## License

This project is for internal use.
