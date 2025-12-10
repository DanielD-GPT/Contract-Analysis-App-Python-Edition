# Contract Analysis Application (Python/Flask)

A modern web application for analyzing contracts using Azure AI Document Intelligence (Content Understanding) and Azure OpenAI. Features a three-pane UI with document viewing, content extraction, and intelligent Q&A capabilities.

## Features

- 📄 **PDF Document Upload**: Upload contract documents for analysis
- 🔍 **Content Extraction**: Automatically extract headers and paragraphs using Azure AI Document Intelligence
- 📊 **Three-Pane Interface**:
  - **Left Pane**: PDF document viewer with page navigation
  - **Middle Pane**: Extracted headers and paragraphs list with search and filtering
  - **Right Pane**: Content details and LLM-powered Q&A
- 🤖 **AI-Powered Q&A**: Ask questions about your contracts using Azure OpenAI
- 🎯 **Interactive Navigation**: Click on extracted content to view details and bounding box location
- 🔎 **Search & Filter**: Search through extracted content and filter by type

## Architecture

- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python with Flask
- **Azure Services**:
  - Azure AI Document Intelligence (prebuilt-layout model)
  - Azure OpenAI for LLM integration

## Prerequisites

- Python 3.8+ 
- Azure subscription with:
  - Azure AI Document Intelligence resource
  - Azure OpenAI resource with a deployed model

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/DanielD-GPT/Contract-Analysis-App-PYTHON-Veriosn.git
cd Contract-Analysis-App-PYTHON-Veriosn
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Azure Credentials

Create a `.env` file in the root directory by copying `.env.example`:

```bash
copy .env.example .env
```

Edit `.env` and add your Azure credentials:

```env
# Azure Document Intelligence (Content Understanding) Configuration
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key_here

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_key_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_name_here

# Server Configuration
PORT=3000
```

#### How to Get Azure Credentials:

**Azure AI Document Intelligence:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Create or navigate to your Document Intelligence resource
3. Go to "Keys and Endpoint" section
4. Copy the endpoint URL and one of the keys

**Azure OpenAI:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Create or navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the endpoint and key
5. Deploy a model (e.g., gpt-4, gpt-35-turbo) in Azure OpenAI Studio
6. Use the deployment name in your configuration

### 5. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:3000`

### 6. Open in Browser

Navigate to:
```
http://localhost:3000
```

## Usage

1. **Upload a Contract**: Click the "Upload Contract" button and select a PDF file
2. **View Extracted Content**: The middle pane will show all extracted headers and paragraphs
3. **Search Content**: Use the search bar to find specific content
4. **Filter Content**: Use the filter buttons (All, Headings, Paragraphs) to narrow down the list
5. **Select Content**: Click on any item to view its details and highlight its location in the PDF
6. **Ask Questions**: Type questions in the Q&A section to get AI-powered answers about your contract

## Project Structure

```
Contract-Analysis-App-PYTHON-Version/
├── static/
│   ├── index.html          # Main HTML file with three-pane layout
│   ├── styles.css          # Application styling
│   └── app.js              # Frontend JavaScript logic
├── uploads/                # Temporary storage for uploaded PDFs (auto-created)
├── app.py                  # Flask server with Azure integration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## API Endpoints

### `POST /api/analyze`

Upload and analyze a contract document.

- **Request**: `multipart/form-data` with `document` field (PDF file)
- **Response**:
```json
{
  "filename": "contract.pdf",
  "filePath": "/uploads/1234567890-contract.pdf",
  "content": {
    "items": [...],
    "fullText": "...",
    "pageCount": 5
  }
}
```

### `POST /api/query`

Ask a question about the uploaded contract.

- **Request**:
```json
{
  "question": "What is the termination clause?"
}
```

- **Response**:
```json
{
  "answer": "The termination clause states..."
}
```

### `GET /uploads/<filename>`

Retrieve uploaded PDF file.

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), PDF.js
- **Backend**: Python 3.8+, Flask
- **Azure AI Services**:
  - `azure-ai-formrecognizer` - Document Intelligence SDK
  - `openai` - Azure OpenAI integration
- **Other Libraries**:
  - `flask-cors` - Cross-origin resource sharing
  - `python-dotenv` - Environment variable management
  - `werkzeug` - File upload handling

## Security Notes

- Never commit `.env` file to version control
- Keep your Azure keys secure
- Uploaded files are stored temporarily in the `uploads/` directory
- Consider implementing file cleanup and size limits for production use

## Troubleshooting

**Issue: Server won't start**
- Check that port 3000 is not in use
- Verify `.env` file exists and has correct values
- Ensure virtual environment is activated

**Issue: Document analysis fails**
- Verify Azure Document Intelligence credentials
- Check that the PDF file is valid and not corrupted
- Ensure your Azure resource has sufficient quota

**Issue: Q&A not working**
- Verify Azure OpenAI credentials
- Ensure your deployment name is correct
- Check that you've uploaded a document first

## Support

For issues or questions, please check the Azure documentation:
- [Azure AI Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)

---

## ⚠️ DISCLAIMER

**This application is a prototype intended for proof of concept and demonstration purposes only.** It is not designed, tested, or supported for production use. Use at your own risk. Microsoft makes no warranties, express or implied, regarding the functionality, reliability, or suitability of this code for any purpose. For production scenarios, please consult official Microsoft documentation and implement appropriate security, scalability, and compliance measures.
