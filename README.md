# ✧ LuminaAI ✧

<div align="center">
  <img src="https://img.shields.io/badge/LuminaAI-F43E01?style=for-the-badge&logo=rocket" alt="LuminaAI" />
  <img src="https://img.shields.io/badge/Built%20with-FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Frontend-React%20Vite-61DAFB?style=for-the-badge&logo=react" alt="React Vite" />
  <img src="https://img.shields.io/badge/AI-Google%20Gemini%203-4285F4?style=for-the-badge&logo=google-gemini" alt="Gemini 3" />
</div>

---

### **Experience elite, private document analysis.**
LuminaAI is a premium, localized Retrieval-Augmented Generation (RAG) platform. Chat with your documents using state-of-the-art AI while keeping the heavy lifting (extraction, chunking, and embedding) local and private.

<br/>

## 🌟 **Key Features**

| Feature | Description |
|---------|-------------|
| 🚀 **Next-Gen AI** | Integrated with **Gemini 3 Flash** for ultra-fast, intelligent responses |
| 📄 **Multi-Format Mastery** | Support for PDF, DOCX, TXT, Images (JPG/PNG), CSV, and SQLite databases |
| 👁️ **OCR Integration** | Automatic Tesseract-powered OCR for scanned documents and images |
| 🔍 **Smart Chunking** | Sentence-aware text splitting with configurable overlap for better context |
| 🛡️ **Privacy First** | Embeddings and indexing happen locally via SentenceTransformers |
| 🗄️ **Dual Vector Store** | Choose between FAISS or ChromaDB for vector storage |
| ⚡ **Modern UI** | Stunning, high-performance interface built with React 19 and Vite |
| 📦 **Containerized** | Fully Dockerized for seamless deployment |
| 🌐 **REST API** | Complete API with Swagger documentation |

<br/>

## 🛠️ **Tech Stack**

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI (Python 3.11) |
| **Frontend** | React 19, Vite, TypeScript |
| **AI/LLM** | Google Gemini API (`gemini-3-flash-preview`) |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Vector Search** | FAISS / ChromaDB (configurable) |
| **OCR** | Tesseract OCR + PyTesseract |
| **PDF Processing** | PyMuPDF + pdfplumber |
| **Containerization** | Docker & Docker Compose |

<br/>

## 📂 **Project Architecture**

```
LuminaAI/
├── app/                    # 🧠 Backend API (FastAPI)
│   ├── api/
│   │   └── routes.py       # All API endpoints
│   ├── core/
│   │   └── config.py       # Environment configuration
│   ├── models/
│   │   └── schemas.py      # Pydantic request/response models
│   └── services/
│       ├── extractor.py    # Document text extraction (PDF, DOCX, images, etc.)
│       ├── chunker.py      # Smart text chunking with overlap
│       ├── embedder.py     # SentenceTransformers embeddings
│       ├── vector_store.py # FAISS & ChromaDB implementations
│       ├── gemini.py       # Gemini LLM integration
│       └── rag_pipeline.py # Orchestrates the full RAG flow
├── frontend/               # 🎨 React Frontend
│   ├── components/         # UI components (Navbar, FileUpload, SourceCard)
│   ├── services/           # API service layer
│   └── App.tsx             # Main application
├── data/                   # 💾 Persistent Storage (auto-created)
│   ├── uploads/            # Temporary uploaded files
│   ├── faiss_index/        # FAISS vector database
│   └── chroma_db/          # ChromaDB database (if used)
├── docker-compose.yml      # Production deployment
├── docker-compose.dev.yml  # Development with hot reload
└── .env.example            # Environment template
```

<br/>

## 🚀 **Quick Start**

### **Prerequisites**
- Docker & Docker Compose installed
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- (Optional) Tesseract OCR for local development without Docker

### **1. Clone & Configure**
```bash
# Clone the repository
git clone https://github.com/shaikat-cse/LuminaAI.git
cd LuminaAI

# Setup environment variables
cp .env.example .env

# Edit .env and add your GEMINI_API_KEY
```

### **2. Launch with Docker**
```bash
# Production Mode
docker-compose up --build -d

# Development Mode (with hot reload)
docker-compose -f docker-compose.dev.yml up --build
```

### **3. Access the Application**
| Service | URL |
|---------|-----|
| 🎨 **Frontend** | [http://localhost:3005](http://localhost:3005) |
| 🔌 **API Backend** | [http://localhost:9005](http://localhost:9005) |
| 📚 **Swagger Docs** | [http://localhost:9005/docs](http://localhost:9005/docs) |
| 📖 **ReDoc** | [http://localhost:9005/redoc](http://localhost:9005/redoc) |

<br/>

## 📡 **API Reference**

### **Endpoints Overview**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check with system status |
| `GET` | `/api/v1/stats` | Get statistics (document count, settings) |
| `POST` | `/api/v1/upload` | Upload a document file |
| `POST` | `/api/v1/upload/url` | Upload document from URL |
| `POST` | `/api/v1/query` | Query documents with a question |
| `DELETE` | `/api/v1/documents/{file_id}` | Delete a specific document |
| `DELETE` | `/api/v1/documents` | Clear all documents |

### **Upload a Document**
```bash
curl -X POST "http://localhost:9005/api/v1/upload" \
  -F "file=@your_document.pdf"
```

**Response:**
```json
{
  "file_id": "abc123-uuid",
  "filename": "your_document.pdf",
  "file_type": "pdf",
  "chunk_count": 42,
  "status": "success",
  "message": "Successfully processed 42 chunks"
}
```

### **Query Documents**
```bash
curl -X POST "http://localhost:9005/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key findings in the document?",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "answer": "Based on the analysis, the key findings include...",
  "sources": [
    {
      "file_id": "abc123-uuid",
      "filename": "report.pdf",
      "chunk_id": 3,
      "score": 0.8542,
      "text_preview": "The study found that..."
    }
  ],
  "ocr_text": null
}
```

### **Query with Image (OCR)**
```bash
curl -X POST "http://localhost:9005/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What does this image say?",
    "image_base64": "data:image/png;base64,iVBORw0KGgo..."
  }'
```

### **Upload from URL**
```bash
curl -X POST "http://localhost:9005/api/v1/upload/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/document.pdf"}'
```

<br/>

## 📁 **Supported File Formats**

| Format | Extensions | Processing Method |
|--------|------------|-------------------|
| **PDF** | `.pdf` | PyMuPDF → pdfplumber fallback → OCR for scanned |
| **Word** | `.docx`, `.doc` | python-docx with table extraction |
| **Text** | `.txt` | Direct read with multi-encoding support |
| **Images** | `.jpg`, `.jpeg`, `.png` | Tesseract OCR |
| **CSV** | `.csv` | Parsed with headers preserved |
| **SQLite** | `.db`, `.sqlite`, `.sqlite3` | All tables extracted (first 100 rows each) |

<br/>

## ⚙️ **Configuration Options**

All settings are configured via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | *required* | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-3-flash-preview` | Gemini model to use |
| `VITE_API_URL` | `http://localhost:9005/api/v1` | Frontend API base URL |
| `VECTOR_STORE_TYPE` | `faiss` | Vector store: `faiss` or `chroma` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformers model |
| `CHUNK_SIZE` | `500` | Target tokens per chunk |
| `CHUNK_OVERLAP` | `75` | Overlap tokens between chunks |
| `TOP_K_RESULTS` | `5` | Number of similar chunks to retrieve |
| `TESSERACT_PATH` | *auto-detect* | Path to Tesseract executable (Windows) |

<br/>

## 🖥️ **Local Development (Without Docker)**

### **Backend Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# Ubuntu: sudo apt install tesseract-ocr
# Mac: brew install tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 9005
```

### **Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

<br/>

## 🔄 **Sample Workflow**

### **1. Upload Documents**
Upload any supported document through the UI or API:
```bash
curl -X POST "http://localhost:9005/api/v1/upload" -F "file=@invoice.pdf"
curl -X POST "http://localhost:9005/api/v1/upload" -F "file=@contract.docx"
curl -X POST "http://localhost:9005/api/v1/upload" -F "file=@data.csv"
```

### **2. Ask Questions**
Query your documents naturally:
- *"What are the payment terms in the invoice?"*
- *"Summarize the key clauses in the contract"*
- *"What is the total revenue from the CSV data?"*

### **3. Get Intelligent Answers**
LuminaAI will:
1. Search for relevant chunks across ALL uploaded documents
2. Build context from the top matches
3. Generate a coherent answer using Gemini
4. Return the answer with source citations

<br/>

## 🐳 **Docker Commands**

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up --build -d

# Stop services
docker-compose down

# Stop and remove volumes (clears all data)
docker-compose down -v

# Clean up old images
docker system prune -f
```

<br/>

## 🔧 **Troubleshooting**

### **Common Issues**

| Issue | Solution |
|-------|----------|
| OCR not working | Install Tesseract and set `TESSERACT_PATH` in `.env` |
| Gemini API errors | Verify your `GEMINI_API_KEY` is valid |
| Frontend can't connect | Check `VITE_API_URL` matches your backend URL |
| Out of memory | Reduce `CHUNK_SIZE` or use a smaller embedding model |
| Slow first query | First query loads the embedding model (~500MB) |

### **Health Check**
```bash
curl http://localhost:9005/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_store": "faiss",
  "embedding_model": "all-MiniLM-L6-v2",
  "document_count": 42
}
```

<br/>

## 📊 **How It Works**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Upload    │────▶│   Extract   │────▶│    Chunk    │
│  Document   │     │    Text     │     │    Text     │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Return    │◀────│   Gemini    │◀────│   Vector    │
│   Answer    │     │   Generate  │     │   Search    │
└─────────────┘     └─────────────┘     └─────────────┘
                          ▲                   │
                          │                   │
                    ┌─────────────┐     ┌─────────────┐
                    │   Build     │◀────│   Embed     │
                    │   Context   │     │   & Store   │
                    └─────────────┘     └─────────────┘
```

<br/>

## 🤝 **Created By**

**Shaikat S.**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/shaikatsk)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/shaikat-cse)

---

<p align="center">
  <strong>MIT License © 2025 Shaikat S.</strong>
  <br/>
  <sub>Built with ❤️ using FastAPI, React, and Google Gemini</sub>
</p>
