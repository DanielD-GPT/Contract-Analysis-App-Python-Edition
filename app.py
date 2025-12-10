import os
import re
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from openai import AzureOpenAI
import time

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Azure Document Intelligence Client
document_client = DocumentAnalysisClient(
    endpoint=os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'),
    credential=AzureKeyCredential(os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY'))
)

# Azure OpenAI Client
openai_client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_KEY'),
    api_version="2024-02-01",
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)

# Store document context for LLM queries
current_document_context = ''

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def flatten_polygon(polygon):
    """Convert polygon from list of Point objects to flat array of numbers."""
    if not polygon:
        return None
    
    # If already a flat list of numbers
    if polygon and isinstance(polygon[0], (int, float)):
        return polygon
    
    # If list of Point objects with x, y attributes
    try:
        return [coord for pt in polygon for coord in [pt.x, pt.y]]
    except AttributeError:
        return None

def extract_structured_content(result):
    """Extract structured content from Azure Document Intelligence result."""
    items = []
    full_text = ''
    
    # Build a map of line polygons by page for lookup
    line_polygon_map = {}
    if result.pages:
        for page in result.pages:
            if page.lines:
                for line in page.lines:
                    key = f"{page.page_number}:{line.content.strip()}"
                    flat_poly = flatten_polygon(line.polygon)
                    if key not in line_polygon_map and flat_poly and len(flat_poly) >= 8:
                        line_polygon_map[key] = {
                            'page': page.page_number,
                            'polygon': flat_poly
                        }
    
    if result.paragraphs:
        for index, paragraph in enumerate(result.paragraphs):
            content = paragraph.content
            role = paragraph.role if hasattr(paragraph, 'role') and paragraph.role else 'paragraph'
            
            full_text += content + '\n\n'
            
            # Determine if it's a heading based on multiple criteria
            is_heading = (
                role in ['title', 'sectionHeading', 'pageHeader'] or
                (len(content) < 150 and (
                    bool(re.match(r'^[A-Z][A-Z\s]+$', content)) or  # ALL CAPS headings
                    bool(re.match(r'^\d+\.', content)) or  # Numbered sections like "1." or "1.1"
                    bool(re.match(r'^Article\s+[IVX\d]+', content, re.IGNORECASE)) or  # Article I, etc.
                    bool(re.match(r'^Section\s+[\d\.]+', content, re.IGNORECASE)) or  # Section 1, etc.
                    bool(re.match(r'^ARTICLE\s+[IVX\d]+', content, re.IGNORECASE)) or
                    bool(re.match(r'^SECTION\s+[\d\.]+', content, re.IGNORECASE)) or
                    bool(re.match(r'^[A-Z][^.!?]*:$', content)) or  # Title Case ending with colon
                    bool(re.match(r'^Clause\s+[\d\.]+', content, re.IGNORECASE))  # Clause numbers
                ))
            )
            
            page_number = 1
            if paragraph.bounding_regions and len(paragraph.bounding_regions) > 0:
                page_number = paragraph.bounding_regions[0].page_number
            
            # Use the paragraph's full bounding polygon
            bounding_polygon = []
            if paragraph.bounding_regions and len(paragraph.bounding_regions) > 0:
                bounding_polygon = flatten_polygon(paragraph.bounding_regions[0].polygon) or []
            
            # Build source string from all bounding regions
            source = None
            if paragraph.bounding_regions and len(paragraph.bounding_regions) > 0:
                sources = []
                for region in paragraph.bounding_regions:
                    flat_poly = flatten_polygon(region.polygon)
                    if flat_poly and len(flat_poly) >= 8:
                        p = flat_poly
                        sources.append(f"D({region.page_number},{p[0]},{p[1]},{p[2]},{p[3]},{p[4]},{p[5]},{p[6]},{p[7]})")
                if sources:
                    source = ';'.join(sources)
            
            items.append({
                'id': f'item-{index}',
                'type': 'heading' if is_heading else 'paragraph',
                'content': content,
                'page': page_number,
                'boundingBox': bounding_polygon,
                'source': source
            })
    
    # If no paragraphs, use pages
    if len(items) == 0 and result.pages:
        for page_index, page in enumerate(result.pages):
            if page.lines:
                for line_index, line in enumerate(page.lines):
                    full_text += line.content + '\n'
                    
                    content = line.content
                    is_heading = (
                        len(content) < 150 and (
                            bool(re.match(r'^[A-Z][A-Z\s]+$', content)) or
                            bool(re.match(r'^\d+\.', content)) or
                            bool(re.match(r'^Article\s+[IVX\d]+', content, re.IGNORECASE)) or
                            bool(re.match(r'^Section\s+[\d\.]+', content, re.IGNORECASE)) or
                            bool(re.match(r'^ARTICLE\s+[IVX\d]+', content, re.IGNORECASE)) or
                            bool(re.match(r'^SECTION\s+[\d\.]+', content, re.IGNORECASE)) or
                            bool(re.match(r'^[A-Z][^.!?]*:$', content)) or
                            bool(re.match(r'^Clause\s+[\d\.]+', content, re.IGNORECASE))
                        )
                    )
                    
                    flat_poly = flatten_polygon(line.polygon)
                    source = None
                    if flat_poly and len(flat_poly) >= 8:
                        p = flat_poly
                        source = f"D({page.page_number},{p[0]},{p[1]},{p[2]},{p[3]},{p[4]},{p[5]},{p[6]},{p[7]})"
                    
                    items.append({
                        'id': f'page-{page_index}-line-{line_index}',
                        'type': 'heading' if is_heading else 'paragraph',
                        'content': content,
                        'page': page.page_number,
                        'boundingBox': flat_poly or [],
                        'source': source
                    })
    
    return {
        'items': items,
        'fullText': full_text,
        'pageCount': len(result.pages) if result.pages else 0
    }

# Routes

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('static', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    """Upload and analyze a PDF document."""
    global current_document_context
    
    try:
        if 'document' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['document']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save the file
        filename = f"{int(time.time())}-{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read file content
        with open(filepath, 'rb') as f:
            file_content = f.read()
        
        # Analyze document with Azure Document Intelligence
        poller = document_client.begin_analyze_document(
            "prebuilt-layout",
            file_content
        )
        result = poller.result()
        
        # Extract structured content
        structured_content = extract_structured_content(result)
        
        # Store full text for LLM context
        current_document_context = structured_content['fullText']
        
        return jsonify({
            'filename': file.filename,
            'filePath': f'/uploads/{filename}',
            'content': structured_content
        })
    
    except Exception as e:
        print(f'Analysis error: {e}')
        return jsonify({
            'error': 'Failed to analyze document',
            'details': str(e)
        }), 500

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/query', methods=['POST'])
def query_llm():
    """Query the LLM about the analyzed document."""
    global current_document_context
    
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not current_document_context:
            return jsonify({
                'error': 'No document analyzed yet. Please upload a document first.'
            }), 400
        
        print(f'Processing question with document context length: {len(current_document_context)}')
        
        # Query Azure OpenAI with full document context
        response = openai_client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT'),
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant that analyzes contracts and legal documents. You have access to the ENTIRE document content provided below. When answering questions, search through and analyze ALL parts of the document to provide accurate and comprehensive answers. Cite specific sections, clauses, or page references when relevant.'
                },
                {
                    'role': 'user',
                    'content': f'Here is the complete document content:\n\n{current_document_context}\n\n---\n\nBased on the ENTIRE document above, please answer this question: {question}'
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        return jsonify({'answer': answer})
    
    except Exception as e:
        print(f'Query error: {e}')
        return jsonify({
            'error': 'Failed to process query',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    print(f'Server running on http://localhost:{port}')
    print('Make sure to configure your .env file with Azure credentials')
    app.run(host='0.0.0.0', port=port, debug=True)
