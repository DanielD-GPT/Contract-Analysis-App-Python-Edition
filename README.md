# Contract Analysis Application (Python/Flask)

A web application for analyzing contracts using Azure Content Understanding Service.

## ⚠️ Disclaimer

This is a demonstration/proof-of-concept application. It is intended for educational and experimental purposes only. This code is **not production-ready** and should not be used in production environments without significant modifications, security reviews, and proper testing.

**USE AT YOUR OWN RISK.** The authors and contributors are not responsible for any issues, damages, or security vulnerabilities that may arise from using this code.

## Features

- **Three-pane UI Layout**
  - Document Viewer: PDF rendering with page navigation
  - Document Sections: List of extracted headers and paragraphs with search and filter
  - Details & Q&A: Selected content details and LLM-powered Q&A

- **PDF Document Handling**
  - Upload and view PDF contracts
  - Navigate between pages
  - Interactive bounding boxes for extracted content

- **Content Extraction**
  - Automatic heading detection
  - Paragraph extraction
  - Content search and filtering
  - Delete and restore functionality

- **LLM-Powered Q&A**
  - Ask questions about the contract
  - Full document context awareness
  - Chat history display

## Technology Stack

- **Backend**: Python 3.8+ with Flask
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **PDF Rendering**: PDF.js
- **Azure Services**:
  - Azure AI Document Intelligence (Content Understanding)
  - Azure OpenAI

## Prerequisites

- Python 3.8 or higher
- Azure subscription with:
  - Azure AI Document Intelligence resource
  - Azure OpenAI resource with a deployed model

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Contract App Python"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Azure credentials**
   
   Copy `.env.example` to `.env` and fill in your Azure credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your values:
   ```
   AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key-here
   AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-openai-key-here
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   
   Navigate to `http://localhost:3000`

## Usage

1. Click **Upload Contract** to select a PDF document
2. Wait for the document to be processed
3. Browse extracted content in the **Document Sections** pane
4. Click on items to view details and highlight in the document
5. Use the search bar to filter content
6. Ask questions about the contract in the **Q&A** section

## Project Structure

```
Contract App Python/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── static/              # Frontend static files
│   ├── index.html       # Main HTML page
│   ├── styles.css       # CSS styles
│   └── app.js           # Frontend JavaScript
└── uploads/             # Uploaded PDF storage (auto-created)
```

## API Endpoints

- `GET /` - Serve the main application
- `POST /api/analyze` - Upload and analyze a PDF document
- `GET /uploads/<filename>` - Serve uploaded files
- `POST /api/query` - Query the LLM about the document

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Azure Document Intelligence endpoint URL |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | Azure Document Intelligence API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Azure OpenAI deployment/model name |
| `PORT` | Server port (default: 3000) |

## License

This project is provided as-is for demonstration purposes.
