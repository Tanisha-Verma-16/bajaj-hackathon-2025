// Main JavaScript for Intelligent Document Query System

// Global variables
let processingModal;
let statusModal;
let API_BASE = '/api/v1';
let BEARER_TOKEN = '895ac47fc43e4b5dfbd28179dd2cb7b92a47e2745926e8baad22b6a1d454f54d'; // fallback token

// Initialize page
document.addEventListener('DOMContentLoaded', async function() {
    processingModal = new bootstrap.Modal(document.getElementById('processingModal'));
    statusModal = new bootstrap.Modal(document.getElementById('statusModal'));
    
    // Load configuration from server
    await loadClientConfig();
    
    // Check system status on load
    checkSystemStatus();
});

// Utility functions
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alert-container');
    const alertId = 'alert-' + Date.now();
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show alert-floating" id="${alertId}" role="alert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-remove after duration
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }
    }, duration);
}

function showProcessingModal(title = 'Processing...', subtitle = 'Please wait while we process your request.') {
    document.getElementById('processingText').textContent = title;
    document.getElementById('processingSubtext').textContent = subtitle;
    processingModal.show();
}

function hideProcessingModal() {
    processingModal.hide();
}

// API helper function
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${BEARER_TOKEN}`,
            'Content-Type': 'application/json',
        }
    };
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(API_BASE + endpoint, finalOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Document processing functions
async function processFromUrl() {
    const urlInput = document.getElementById('documentUrl');
    const url = urlInput.value.trim();
    
    if (!url) {
        showAlert('Please enter a document URL', 'warning');
        return;
    }
    
    if (!isValidUrl(url)) {
        showAlert('Please enter a valid URL', 'warning');
        return;
    }
    
    showProcessingModal('Downloading Document...', 'Retrieving document from URL and processing content.');
    
    try {
        // Test with a single question first
        const testData = {
            documents: url,
            questions: ['What is this document about?']
        };
        
        const result = await apiCall('/hackrx/run', {
            method: 'POST',
            body: JSON.stringify(testData)
        });
        
        hideProcessingModal();
        showAlert('Document processed successfully! You can now ask questions.', 'success');
        
        // Clear the URL input
        urlInput.value = '';
        
        // Show processing result
        displayDocumentProcessed(url, result);
        
    } catch (error) {
        hideProcessingModal();
        showAlert(`Error processing document: ${error.message}`, 'danger');
    }
}

async function uploadFile(fileInput) {
    const file = fileInput.files[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
    const allowedExtensions = ['.pdf', '.docx', '.txt', '.md'];
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
        showAlert('Unsupported file type. Please upload PDF, DOCX, TXT, or MD files.', 'warning');
        fileInput.value = '';
        return;
    }
    
    // Check file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
        showAlert('File is too large. Please upload files smaller than 50MB.', 'warning');
        fileInput.value = '';
        return;
    }
    
    showProcessingModal('Uploading File...', 'Uploading and processing your document.');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const result = await fetch(API_BASE + '/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${BEARER_TOKEN}`
            },
            body: formData
        });
        
        if (!result.ok) {
            const errorData = await result.json().catch(() => ({}));
            throw new Error(errorData.message || 'Upload failed');
        }
        
        const data = await result.json();
        
        hideProcessingModal();
        showAlert(`File uploaded successfully! ${data.chunk_count} chunks created.`, 'success');
        
        // Clear file input
        fileInput.value = '';
        
        // Display upload status
        displayUploadStatus(data);
        
    } catch (error) {
        hideProcessingModal();
        showAlert(`Error uploading file: ${error.message}`, 'danger');
        fileInput.value = '';
    }
}

// Query processing
async function processQuery() {
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();
    
    if (!query) {
        showAlert('Please enter a question', 'warning');
        return;
    }
    
    const queryBtn = document.getElementById('queryBtn');
    const originalText = queryBtn.innerHTML;
    
    queryBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    queryBtn.disabled = true;
    
    try {
        const result = await apiCall('/query', {
            method: 'POST',
            body: JSON.stringify({ query, top_k: 5 })
        });
        
        displayQueryResult(query, result);
        showAlert('Query processed successfully!', 'success');
        
    } catch (error) {
        showAlert(`Error processing query: ${error.message}`, 'danger');
    } finally {
        queryBtn.innerHTML = originalText;
        queryBtn.disabled = false;
    }
}

// Display functions
function displayDocumentProcessed(url, result) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.innerHTML = `
        <div class="alert alert-success">
            <h6><i class="fas fa-check-circle me-2"></i>Document Processed Successfully</h6>
            <p class="mb-2"><strong>Source:</strong> ${url}</p>
            <p class="mb-0"><strong>Test Answer:</strong> ${result.answers[0]}</p>
        </div>
    `;
}

function displayUploadStatus(data) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.innerHTML = `
        <div class="alert alert-success">
            <h6><i class="fas fa-check-circle me-2"></i>Upload Successful</h6>
            <p class="mb-2"><strong>File:</strong> ${data.filename}</p>
            <p class="mb-2"><strong>Document ID:</strong> ${data.document_id}</p>
            <p class="mb-0"><strong>Chunks Created:</strong> ${data.chunk_count}</p>
        </div>
    `;
}

function displayQueryResult(query, result) {
    const resultsSection = document.getElementById('resultsSection');
    const answerContent = document.getElementById('answerContent');
    
    // Determine confidence level and styling
    const confidence = result.confidence || 0;
    let confidenceClass, confidenceText;
    
    if (confidence >= 0.8) {
        confidenceClass = 'confidence-high';
        confidenceText = 'High';
    } else if (confidence >= 0.5) {
        confidenceClass = 'confidence-medium';
        confidenceText = 'Medium';
    } else {
        confidenceClass = 'confidence-low';
        confidenceText = 'Low';
    }
    
    // Build sources HTML
    let sourcesHtml = '';
    if (result.sources && result.sources.length > 0) {
        sourcesHtml = `
            <div class="mt-3">
                <h6>Sources Used:</h6>
                ${result.sources.map((source, index) => `
                    <div class="source-item">
                        <strong>Source ${index + 1}:</strong> ${source.source || 'Unknown'}<br>
                        <small class="text-muted">
                            Similarity: ${(source.similarity_score || 0).toFixed(3)} | 
                            Type: ${source.chunk_type || 'Unknown'} |
                            Categories: ${(source.content_categories || []).join(', ') || 'None'}
                        </small>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Build query analysis HTML
    let analysisHtml = '';
    if (result.query_analysis) {
        const analysis = result.query_analysis;
        analysisHtml = `
            <div class="query-analysis mb-3">
                <h6><i class="fas fa-search me-2"></i>Query Analysis</h6>
                <p><strong>Type:</strong> ${analysis.query_type}</p>
                ${analysis.intent_categories.length > 0 ? 
                    `<p><strong>Intent:</strong> ${analysis.intent_categories.join(', ')}</p>` : ''}
                ${analysis.key_entities.length > 0 ? 
                    `<p><strong>Entities:</strong> ${analysis.key_entities.map(e => 
                        `<span class="entity-tag">${e.type}: ${e.value}</span>`
                    ).join('')}</p>` : ''}
            </div>
        `;
    }
    
    answerContent.innerHTML = `
        <div class="mb-3">
            <h6><i class="fas fa-question-circle me-2"></i>Question</h6>
            <p class="text-muted">${query}</p>
        </div>
        
        ${analysisHtml}
        
        <div class="answer-box">
            <div class="d-flex justify-content-between align-items-start mb-3">
                <h6><i class="fas fa-lightbulb me-2"></i>Answer</h6>
                <span class="confidence-badge ${confidenceClass}">
                    Confidence: ${confidenceText} (${(confidence * 100).toFixed(0)}%)
                </span>
            </div>
            <p class="mb-0">${result.answer}</p>
        </div>
        
        ${sourcesHtml}
        
        <div class="mt-3">
            <details>
                <summary class="text-muted">Processing Details</summary>
                <div class="mt-2">
                    <small class="text-muted">
                        <strong>Processing Time:</strong> ${result.processing_time || 0}s<br>
                        <strong>Chunks Used:</strong> ${result.chunks_used || 0}<br>
                        <strong>Context Quality:</strong> ${result.context_quality || 0}<br>
                        ${result.reasoning ? `<strong>Reasoning:</strong> ${result.reasoning}` : ''}
                    </small>
                </div>
            </details>
        </div>
    `;
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// API Testing
async function testAPI() {
    const documentUrl = document.getElementById('apiDocumentUrl').value.trim();
    const questionsText = document.getElementById('apiQuestions').value.trim();
    const responseDiv = document.getElementById('apiResponse');
    
    if (!documentUrl || !questionsText) {
        showAlert('Please provide both document URL and questions', 'warning');
        return;
    }
    
    let questions;
    try {
        questions = JSON.parse(questionsText);
        if (!Array.isArray(questions)) {
            throw new Error('Questions must be an array');
        }
    } catch (error) {
        showAlert('Invalid JSON format for questions', 'warning');
        return;
    }
    
    responseDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing API request...';
    
    try {
        const requestData = {
            documents: documentUrl,
            questions: questions
        };
        
        const result = await apiCall('/hackrx/run', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
        
        responseDiv.innerHTML = JSON.stringify(result, null, 2);
        showAlert('API test completed successfully!', 'success');
        
    } catch (error) {
        responseDiv.innerHTML = `Error: ${error.message}`;
        showAlert(`API test failed: ${error.message}`, 'danger');
    }
}

// System status
async function showSystemStatus() {
    const statusContent = document.getElementById('status-content');
    statusContent.innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    statusModal.show();
    
    try {
        const status = await apiCall('/status');
        
        const vectorStats = status.vector_store_stats || {};
        const dbStats = status.database_stats || {};
        const components = status.components || {};
        
        statusContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>System Components</h6>
                    <ul class="list-unstyled">
                        ${Object.entries(components).map(([component, status]) => `
                            <li class="mb-2">
                                <span class="status-indicator status-${status === 'ready' ? 'success' : 'warning'}"></span>
                                ${component.replace('_', ' ').toUpperCase()}: <strong>${status}</strong>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Vector Store Statistics</h6>
                    <ul class="list-unstyled">
                        <li>Total Chunks: <strong>${vectorStats.total_chunks || 0}</strong></li>
                        <li>Embedding Dimension: <strong>${vectorStats.embedding_dimension || 0}</strong></li>
                        <li>Model: <strong>${vectorStats.model_name || 'Unknown'}</strong></li>
                        <li>Trained: <strong>${vectorStats.is_trained ? 'Yes' : 'No'}</strong></li>
                        <li>Unique Sources: <strong>${vectorStats.unique_sources || 0}</strong></li>
                    </ul>
                </div>
            </div>
            
            ${dbStats.documents_processed !== undefined ? `
                <div class="row mt-3">
                    <div class="col-12">
                        <h6>Database Statistics</h6>
                        <ul class="list-unstyled">
                            <li>Documents Processed: <strong>${dbStats.documents_processed}</strong></li>
                            <li>Total Chunks: <strong>${dbStats.total_chunks}</strong></li>
                            <li>Queries Processed: <strong>${dbStats.queries_processed}</strong></li>
                        </ul>
                    </div>
                </div>
            ` : ''}
            
            ${vectorStats.content_categories ? `
                <div class="row mt-3">
                    <div class="col-12">
                        <h6>Content Categories Distribution</h6>
                        <div class="row">
                            ${Object.entries(vectorStats.content_categories).map(([category, count]) => `
                                <div class="col-md-4 mb-2">
                                    <small>${category.replace('_', ' ')}: <strong>${count}</strong></small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            ` : ''}
        `;
        
    } catch (error) {
        statusContent.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading system status: ${error.message}
            </div>
        `;
    }
}

async function checkSystemStatus() {
    try {
        const status = await apiCall('/status');
        const isReady = status.system_ready;
        
        if (!isReady) {
            showAlert('System is ready but no documents are loaded. Upload documents to start querying.', 'info');
        }
    } catch (error) {
        showAlert('Unable to connect to the system. Please check if the server is running.', 'warning');
    }
}

// Helper functions
function setQuery(query) {
    document.getElementById('queryInput').value = query;
}

function clearResults() {
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('answerContent').innerHTML = '';
}

function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// Configuration loading
async function loadClientConfig() {
    try {
        const response = await fetch('/api/v1/config');
        if (response.ok) {
            const config = await response.json();
            BEARER_TOKEN = config.bearer_token;
            API_BASE = config.api_base || '/api/v1';
            console.log('Client configuration loaded successfully');
        } else {
            console.warn('Failed to load client configuration, using defaults');
        }
    } catch (error) {
        console.warn('Error loading client configuration:', error.message);
        showAlert('Using default configuration - some features may not work correctly', 'warning');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl+Enter to process query
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const queryInput = document.getElementById('queryInput');
        if (document.activeElement === queryInput && queryInput.value.trim()) {
            processQuery();
        }
    }
});
