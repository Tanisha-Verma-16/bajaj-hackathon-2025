from app import db
from datetime import datetime
from sqlalchemy import Text, DateTime, Integer, String, Boolean, JSON
import uuid

class Document(db.Model):
    """Model for storing document metadata and processing status"""
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(String(255), nullable=False)
    file_type = db.Column(String(10), nullable=False)
    file_size = db.Column(Integer, nullable=True)
    upload_timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=True)
    processing_status = db.Column(String(20), default='pending', nullable=True)  # pending, processing, completed, failed
    chunk_count = db.Column(Integer, default=0, nullable=True)
    doc_metadata = db.Column(JSON, nullable=True)
    error_message = db.Column(Text, nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f'<Document {self.filename}>'

class DocumentChunk(db.Model):
    """Model for storing document chunks with metadata"""
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(String(36), db.ForeignKey('document.id'), nullable=False)
    chunk_index = db.Column(Integer, nullable=False)
    content = db.Column(Text, nullable=False)
    semantic_type = db.Column(String(50), nullable=True)
    content_categories = db.Column(JSON, nullable=True)  # List of categories
    has_numbers = db.Column(Boolean, default=False, nullable=True)
    has_currency = db.Column(Boolean, default=False, nullable=True)
    has_dates = db.Column(Boolean, default=False, nullable=True)
    has_percentages = db.Column(Boolean, default=False, nullable=True)
    has_medical_terms = db.Column(Boolean, default=False, nullable=True)
    has_legal_terms = db.Column(Boolean, default=False, nullable=True)
    word_count = db.Column(Integer, nullable=True)
    chunk_position = db.Column(db.Float, nullable=True)  # Relative position in document (0.0 to 1.0)
    urgency_indicators = db.Column(JSON, nullable=True)
    exclusion_indicators = db.Column(JSON, nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    # Relationships
    document = db.relationship('Document', backref=db.backref('chunks', lazy=True))
    
    def __repr__(self):
        return f'<DocumentChunk {self.document_id}:{self.chunk_index}>'

class QueryLog(db.Model):
    """Model for logging queries and responses for analytics"""
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text = db.Column(Text, nullable=False)
    document_ids = db.Column(JSON, nullable=True)  # List of document IDs used
    response = db.Column(JSON, nullable=True)
    processing_time = db.Column(db.Float, nullable=True)
    timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def __repr__(self):
        return f'<QueryLog {self.id}>'
