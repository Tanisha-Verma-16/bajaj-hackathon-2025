import os
import json
import logging
import time
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path

from rag_system import EnhancedRAGSystem
from models import Document, DocumentChunk, QueryLog, db

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize RAG system
rag_system = EnhancedRAGSystem()

# Authentication token - use environment variable for deployment
BEARER_TOKEN = os.environ.get("API_BEARER_TOKEN", "895ac47fc43e4b5dfbd28179dd2cb7b92a47e2745926e8baad22b6a1d454f54d")

def authenticate_request():
    """Check if request has valid bearer token"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    return token == BEARER_TOKEN

@api_bp.route('/hackrx/run', methods=['POST'])
def run_hackrx():
    """Main API endpoint for processing documents and answering questions"""
    start_time = time.time()
    
    # Check authentication
    if not authenticate_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Valid bearer token required'
        }), 401
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'JSON data required'
            }), 400
        
        documents_url = data.get('documents')
        questions = data.get('questions', [])
        
        if not documents_url:
            return jsonify({
                'error': 'Bad Request',
                'message': 'documents URL is required'
            }), 400
        
        if not questions:
            return jsonify({
                'error': 'Bad Request',
                'message': 'questions array is required'
            }), 400
        
        # Process document
        logging.info(f"Processing document from URL: {documents_url}")
        doc_result = rag_system.process_document_from_url(documents_url)
        
        if not doc_result.get('success', False):
            return jsonify({
                'error': 'Document Processing Failed',
                'message': doc_result.get('error', 'Unknown error processing document')
            }), 400
        
        # Store document in database
        try:
            document = Document(
                filename=doc_result['document_name'],
                file_type=doc_result.get('structure_type', 'unknown'),
                processing_status='completed',
                chunk_count=doc_result.get('chunk_count', 0),
                doc_metadata=doc_result.get('metadata', {})
            )
            db.session.add(document)
            db.session.commit()
            logging.info(f"Document stored in database with ID: {document.id}")
        except Exception as e:
            logging.error(f"Error storing document in database: {str(e)}")
            # Continue processing even if database storage fails
        
        # Process questions and generate answers
        answers = []
        for question in questions:
            logging.info(f"Processing question: {question}")
            
            # Process query through RAG system
            query_result = rag_system.process_query(question, top_k=5)
            answer = query_result.get('answer', 'Unable to find relevant information.')
            
            answers.append(answer)
            
            # Log query in database
            try:
                query_log = QueryLog(
                    query_text=question,
                    document_ids=[document.id] if 'document' in locals() else [],
                    response={
                        'answer': answer,
                        'confidence': query_result.get('confidence', 0),
                        'sources': len(query_result.get('sources', [])),
                        'processing_time': query_result.get('processing_time', 0)
                    },
                    processing_time=query_result.get('processing_time', 0)
                )
                db.session.add(query_log)
                db.session.commit()
            except Exception as e:
                logging.error(f"Error logging query in database: {str(e)}")
        
        processing_time = time.time() - start_time
        
        response_data = {
            'answers': answers,
            'processing_time': processing_time,
            'questions_processed': len(questions),
            'status': 'success'
        }
        
        logging.info(f"Successfully processed {len(questions)} questions in {processing_time:.2f} seconds")
        
        # Create proper response with CORS headers
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    except Exception as e:
        logging.error(f"Error in hackrx/run endpoint: {str(e)}")
        error_response = jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'status': 'error'
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        error_response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return error_response, 500

@api_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document file"""
    # Check authentication
    if not authenticate_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Valid bearer token required'
        }), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': 'Bad Request',
                'message': 'No file selected'
            }), 400
        
        # Check file extension
        filename = secure_filename(file.filename)
        file_extension = Path(filename).suffix.lower()
        
        if file_extension not in ['.pdf', '.docx', '.txt', '.md']:
            return jsonify({
                'error': 'Bad Request',
                'message': f'Unsupported file type: {file_extension}. Supported types: .pdf, .docx, .txt, .md'
            }), 400
        
        # Save file temporarily and process
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Process document
            result = rag_system.process_document(temp_path, filename)
            
            if result['success']:
                # Store in database
                document = Document(
                    filename=filename,
                    file_type=result.get('structure_type', 'unknown'),
                    file_size=len(file.read()) if hasattr(file, 'read') else 0,
                    processing_status='completed',
                    chunk_count=result.get('chunk_count', 0),
                    doc_metadata=result.get('metadata', {})
                )
                db.session.add(document)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Document processed successfully',
                    'document_id': document.id,
                    'chunk_count': result.get('chunk_count', 0),
                    'filename': filename
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }), 400
        
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    except Exception as e:
        logging.error(f"Error in upload endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@api_bp.route('/query', methods=['POST'])
def process_query():
    """Process a single query against processed documents"""
    # Check authentication
    if not authenticate_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Valid bearer token required'
        }), 401
    
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'query field is required'
            }), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        # Process query
        result = rag_system.process_query(query, top_k)
        
        # Log query
        try:
            query_log = QueryLog(
                query_text=query,
                document_ids=[],  # Could be enhanced to track specific documents used
                response=result,
                processing_time=result.get('processing_time', 0)
            )
            db.session.add(query_log)
            db.session.commit()
        except Exception as e:
            logging.error(f"Error logging query: {str(e)}")
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Error in query endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get system status and statistics"""
    try:
        status = rag_system.get_system_status()
        
        # Add database statistics
        try:
            doc_count = Document.query.count()
            chunk_count = DocumentChunk.query.count()
            query_count = QueryLog.query.count()
            
            status['database_stats'] = {
                'documents_processed': doc_count,
                'total_chunks': chunk_count,
                'queries_processed': query_count
            }
        except Exception as e:
            logging.error(f"Error getting database stats: {str(e)}")
            status['database_stats'] = {'error': 'Unable to fetch database statistics'}
        
        return jsonify(status)
    
    except Exception as e:
        logging.error(f"Error in status endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@api_bp.route('/documents', methods=['GET'])
def list_documents():
    """List all processed documents"""
    # Check authentication
    if not authenticate_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Valid bearer token required'
        }), 401
    
    try:
        documents = Document.query.order_by(Document.upload_timestamp.desc()).all()
        
        doc_list = []
        for doc in documents:
            doc_list.append({
                'id': doc.id,
                'filename': doc.filename,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'upload_timestamp': doc.upload_timestamp.isoformat() if doc.upload_timestamp else None,
                'processing_status': doc.processing_status,
                'chunk_count': doc.chunk_count,
                'metadata': doc.doc_metadata
            })
        
        return jsonify({
            'documents': doc_list,
            'total_count': len(doc_list)
        })
    
    except Exception as e:
        logging.error(f"Error in list documents endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'API endpoint not found'
    }), 404

@api_bp.route('/config', methods=['GET'])
def get_client_config():
    """Get client configuration including bearer token"""
    return jsonify({
        'bearer_token': BEARER_TOKEN,
        'api_base': '/api/v1'
    })

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'HTTP method not allowed for this endpoint'
    }), 405
