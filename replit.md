# Overview

This is an Intelligent Document Query & Retrieval System powered by advanced RAG (Retrieval-Augmented Generation) technology. The system processes documents (PDF, DOCX, TXT, MD, HTML) and enables users to ask natural language questions about the content, with specialized support for insurance, legal, HR, and compliance domains. It combines semantic search with AI-powered reasoning to provide accurate, contextual answers with supporting evidence from the source documents.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Flask with Jinja2 templating engine
- **UI Design**: Bootstrap-based responsive interface with dark theme support
- **Client-Side**: Vanilla JavaScript with Bootstrap components for modals and alerts
- **File Upload**: Drag-and-drop interface with progress tracking and real-time feedback

## Backend Architecture
- **Web Framework**: Flask with Blueprint-based route organization
- **Database**: SQLAlchemy ORM with support for SQLite (default) and PostgreSQL
- **Document Processing**: Multi-layer processing pipeline with structure preservation
- **Vector Search**: FAISS-based semantic search with hybrid retrieval capabilities
- **AI Integration**: OpenAI GPT-4o for natural language understanding and response generation

## Data Storage Solutions
- **Relational Database**: Three main models:
  - `Document`: Stores file metadata, processing status, and error tracking
  - `DocumentChunk`: Stores processed document segments with semantic annotations
  - `QueryLog`: Tracks user queries and system responses for analytics
- **Vector Storage**: FAISS index for embeddings with persistent storage
- **File Storage**: Temporary file handling for uploaded documents

## Authentication and Authorization
- **Bearer Token Authentication**: Simple token-based API security
- **Hardcoded Token**: Static bearer token for API access (development setup)
- **Request Validation**: All API endpoints protected with authentication middleware

## Document Processing Pipeline
- **Multi-Format Support**: Handles PDF (PyPDF2), DOCX, and plain text files
- **Smart Chunking**: Adaptive chunking with overlap preservation and semantic type detection
- **Content Analysis**: Automatic detection of numbers, currency, dates, percentages, and domain-specific terms
- **Structure Preservation**: Maintains document hierarchy and page information

## Query Processing Architecture
- **Pattern Recognition**: Built-in query classification for coverage, exclusions, costs, procedures, and conditions
- **Hybrid Retrieval**: Combines semantic search with keyword matching for comprehensive results
- **Context Enhancement**: Multi-layer context extraction with relevance scoring
- **Response Generation**: Structured JSON responses with confidence scores and source citations

# External Dependencies

## AI/ML Services
- **OpenAI API**: GPT-4o model for natural language processing and response generation
- **SentenceTransformers**: all-MiniLM-L6-v2 model for document embeddings
- **FAISS**: Facebook AI Similarity Search for vector indexing and retrieval

## Document Processing Libraries
- **PyPDF2**: PDF text extraction and metadata parsing
- **python-docx**: Microsoft Word document processing
- **Pathlib**: File system operations and path handling

## Web Framework Dependencies
- **Flask**: Core web framework with SQLAlchemy integration
- **Werkzeug**: WSGI utilities and security features
- **Bootstrap**: Frontend UI framework with dark theme support
- **Font Awesome**: Icon library for user interface elements

## Database and Storage
- **SQLAlchemy**: ORM for database operations with migration support
- **SQLite**: Default database for development (PostgreSQL ready)
- **JSON**: Metadata and configuration storage format

## HTTP and Networking
- **Requests**: HTTP client for external document fetching
- **Werkzeug ProxyFix**: Proxy header handling for deployment environments

## Development and Deployment
- **Python 3.x**: Core runtime environment
- **Environment Variables**: Configuration management for API keys and database URLs
- **Logging**: Comprehensive logging system for debugging and monitoring