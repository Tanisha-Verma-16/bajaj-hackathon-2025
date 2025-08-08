import os
import json
import logging
from typing import List, Dict, Any, Optional
from mistralai import Mistral
from document_processor import AdvancedDocumentProcessor, SmartChunkManager
from vector_store import SimpleVectorStore, HybridRetriever
import requests
import tempfile
from pathlib import Path
import time

class EnhancedRAGSystem:
    """Enhanced RAG system with multi-layer processing and comprehensive context extraction"""
    
    def __init__(self):
        # Initialize Mistral client
        self.mistral_client = Mistral(api_key="EDCCtoTed2RK7dLQCqrEeA1hyLvi2AaZ")
        
        # Initialize components
        self.document_processor = AdvancedDocumentProcessor()
        self.chunk_manager = SmartChunkManager(chunk_size=1000, chunk_overlap=200)
        self.vector_store = SimpleVectorStore()
        self.hybrid_retriever = HybridRetriever(self.vector_store)
        
        # Query analysis patterns
        self.query_patterns = {
            'coverage_query': ['cover', 'coverage', 'covered', 'include', 'included'],
            'exclusion_query': ['exclude', 'excluded', 'not covered', 'exception', 'limitation'],
            'waiting_period': ['waiting period', 'wait', 'minimum duration', 'cooling period'],
            'eligibility': ['eligible', 'eligibility', 'qualify', 'qualification', 'criteria'],
            'cost_query': ['cost', 'premium', 'deductible', 'copay', 'price', 'fee'],
            'procedure_query': ['surgery', 'procedure', 'treatment', 'operation'],
            'condition_query': ['condition', 'disease', 'illness', 'diagnosis'],
            'benefit_query': ['benefit', 'advantage', 'discount', 'bonus']
        }
        
        logging.info("Enhanced RAG System initialized")
    
    def process_document_from_url(self, document_url: str, document_name: str = None) -> Dict[str, Any]:
        """Download and process document from URL"""
        try:
            # Download document
            response = requests.get(document_url, timeout=30)
            response.raise_for_status()
            
            # Determine file extension from URL or content type
            if document_name is None:
                document_name = document_url.split('/')[-1].split('?')[0]
            
            file_extension = Path(document_name).suffix.lower()
            if not file_extension:
                content_type = response.headers.get('content-type', '')
                if 'pdf' in content_type:
                    file_extension = '.pdf'
                elif 'word' in content_type or 'docx' in content_type:
                    file_extension = '.docx'
                else:
                    file_extension = '.txt'
                document_name = f"document{file_extension}"
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            try:
                # Process document
                result = self.process_document(temp_path, document_name)
                return result
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            logging.error(f"Error processing document from URL {document_url}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to process document: {str(e)}',
                'document_name': document_name or 'unknown'
            }
    
    def process_document(self, file_path: str, document_name: str = None) -> Dict[str, Any]:
        """Process a document and add it to the vector store"""
        try:
            if document_name is None:
                document_name = os.path.basename(file_path)
            
            # Extract document content
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                document_data = self.document_processor.extract_text_from_pdf(file_path)
            elif file_extension == '.docx':
                document_data = self.document_processor.extract_text_from_docx(file_path)
            elif file_extension in ['.txt', '.md']:
                document_data = self.document_processor.extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            if not document_data['text'].strip():
                raise ValueError("No text content extracted from document")
            
            # Create intelligent chunks
            chunks = self.chunk_manager.create_smart_chunks(document_data, document_name)
            
            if not chunks:
                raise ValueError("No chunks created from document")
            
            # Add to vector store
            success = self.vector_store.add_documents(chunks)
            
            if not success:
                raise ValueError("Failed to add chunks to vector store")
            
            logging.info(f"Successfully processed document {document_name} with {len(chunks)} chunks")
            
            return {
                'success': True,
                'document_name': document_name,
                'chunk_count': len(chunks),
                'metadata': document_data.get('metadata', {}),
                'structure_type': document_data.get('structure_type', 'unknown')
            }
            
        except Exception as e:
            logging.error(f"Error processing document {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'document_name': document_name or os.path.basename(file_path)
            }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to understand intent and extract key information"""
        query_lower = query.lower()
        
        analysis = {
            'original_query': query,
            'query_type': 'general',
            'intent_categories': [],
            'key_entities': [],
            'urgency_level': 'normal',
            'requires_specific_answer': False
        }
        
        # Detect query types
        for pattern_type, keywords in self.query_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                analysis['intent_categories'].append(pattern_type)
        
        # Extract key entities (simple extraction)
        entities = []
        
        # Medical/procedure terms
        medical_terms = ['surgery', 'procedure', 'treatment', 'diagnosis', 'condition', 'disease']
        for term in medical_terms:
            if term in query_lower:
                entities.append({'type': 'medical_procedure', 'value': term})
        
        # Body parts/conditions
        body_parts = ['knee', 'heart', 'brain', 'liver', 'kidney', 'eye', 'dental', 'maternity']
        for part in body_parts:
            if part in query_lower:
                entities.append({'type': 'body_part', 'value': part})
        
        # Financial terms
        financial_terms = ['premium', 'deductible', 'copay', 'cost', 'price', 'discount']
        for term in financial_terms:
            if term in query_lower:
                entities.append({'type': 'financial', 'value': term})
        
        analysis['key_entities'] = entities
        
        # Determine primary query type
        if analysis['intent_categories']:
            analysis['query_type'] = analysis['intent_categories'][0]
        
        # Check for specific answer requirements
        question_words = ['what', 'when', 'where', 'how', 'why', 'which', 'who']
        if any(word in query_lower for word in question_words):
            analysis['requires_specific_answer'] = True
        
        return analysis
    
    def retrieve_relevant_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context using hybrid approach"""
        try:
            # Analyze query to create targeted search
            query_analysis = self.analyze_query(query)
            
            # Create search filters based on query analysis
            filters = {}
            
            # Filter by content categories if specific intent detected
            if 'coverage_query' in query_analysis['intent_categories']:
                filters['content_categories'] = ['coverage_limits', 'eligibility_criteria']
            elif 'waiting_period' in query_analysis['intent_categories']:
                filters['content_categories'] = ['waiting_periods']
            elif 'procedure_query' in query_analysis['intent_categories']:
                filters['has_medical_terms'] = True
            
            # Use hybrid retriever for better results
            relevant_chunks = self.hybrid_retriever.retrieve(query, top_k * 2)
            
            # Apply additional filtering based on query analysis
            if filters:
                filtered_chunks = self.vector_store.search_with_filters(
                    query, filters, top_k * 2, score_threshold=0.2
                )
                # Combine results, prioritizing filtered matches
                seen_ids = set()
                combined_chunks = []
                
                for chunk in filtered_chunks:
                    chunk_id = chunk.get('vector_id')
                    if chunk_id not in seen_ids:
                        combined_chunks.append(chunk)
                        seen_ids.add(chunk_id)
                
                for chunk in relevant_chunks:
                    chunk_id = chunk.get('vector_id')
                    if chunk_id not in seen_ids and len(combined_chunks) < top_k * 2:
                        combined_chunks.append(chunk)
                        seen_ids.add(chunk_id)
                
                relevant_chunks = combined_chunks
            
            return relevant_chunks[:top_k]
            
        except Exception as e:
            logging.error(f"Error retrieving context: {str(e)}")
            return []
    
    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive answer using LLM with retrieved context"""
        try:
            if not context_chunks:
                return {
                    'answer': "I don't have enough relevant information to answer your query. Please ensure the document has been processed and contains relevant content.",
                    'confidence': 0.0,
                    'sources': [],
                    'reasoning': "No relevant context found in processed documents."
                }
            
            # Prepare context for LLM
            context_text = ""
            source_info = []
            
            for i, chunk in enumerate(context_chunks):
                context_text += f"\n--- Context {i+1} (Score: {chunk.get('combined_score', chunk.get('similarity_score', 0)):.3f}) ---\n"
                context_text += chunk['text']
                context_text += f"\n[Source: {chunk.get('source', 'Unknown')}]"
                
                source_info.append({
                    'source': chunk.get('source', 'Unknown'),
                    'similarity_score': chunk.get('similarity_score', 0),
                    'content_categories': chunk.get('content_categories', []),
                    'chunk_type': chunk.get('semantic_type', 'unknown')
                })
            
            # Create system prompt
            system_prompt = """You are an expert document analysis assistant specializing in insurance, legal, HR, and compliance domains. Your task is to provide accurate, detailed answers based on the provided document context.

Guidelines:
1. Answer based ONLY on the provided context - do not use external knowledge
2. If the context doesn't contain enough information, clearly state this
3. For insurance/policy queries, be specific about coverage conditions, waiting periods, and limitations
4. Include relevant details like amounts, percentages, time periods, and conditions
5. If there are exclusions or limitations, mention them explicitly
6. Structure your response clearly with specific details
7. Always indicate your confidence level in the answer

Response format: Provide a direct, comprehensive answer followed by your reasoning."""

            # Create user prompt
            user_prompt = f"""Query: {query}

Context from documents:
{context_text}

Please provide a comprehensive answer to the query based on the provided context. Include specific details like amounts, conditions, waiting periods, and any relevant limitations or exclusions."""

            # Generate response using Mistral
            response = self.mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for factual accuracy
                max_tokens=1000
            )
            
            # Parse response
            answer = response.choices[0].message.content
            confidence = 0.8
            reasoning = 'Answer generated based on document context.'
            
            # Try to extract JSON from response if present
            try:
                import re
                json_match = re.search(r'\{.*\}', answer, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    if 'answer' in response_data:
                        answer = response_data.get('answer', answer)
                    if 'confidence' in response_data:
                        confidence = response_data.get('confidence', confidence)
                    if 'reasoning' in response_data:
                        reasoning = response_data.get('reasoning', reasoning)
            except:
                pass
            
            # Calculate overall confidence based on context quality
            avg_similarity = sum(chunk.get('similarity_score', 0) for chunk in context_chunks) / len(context_chunks)
            adjusted_confidence = min(confidence, avg_similarity + 0.3)
            
            return {
                'answer': answer,
                'confidence': round(adjusted_confidence, 2),
                'sources': source_info,
                'reasoning': reasoning,
                'context_quality': round(avg_similarity, 3)
            }
            
        except Exception as e:
            logging.error(f"Error generating answer: {str(e)}")
            return {
                'answer': f"Error generating answer: {str(e)}",
                'confidence': 0.0,
                'sources': [],
                'reasoning': f"System error: {str(e)}"
            }
    
    def process_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Process a complete query: analyze, retrieve, and generate answer"""
        start_time = time.time()
        
        try:
            # Step 1: Analyze query
            query_analysis = self.analyze_query(query)
            
            # Step 2: Retrieve relevant context
            context_chunks = self.retrieve_relevant_context(query, top_k)
            
            # Step 3: Generate answer
            result = self.generate_answer(query, context_chunks)
            
            # Add processing metadata
            result.update({
                'query': query,
                'query_analysis': query_analysis,
                'processing_time': round(time.time() - start_time, 3),
                'chunks_used': len(context_chunks),
                'vector_store_stats': self.vector_store.get_statistics()
            })
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing query '{query}': {str(e)}")
            return {
                'query': query,
                'answer': f"Error processing query: {str(e)}",
                'confidence': 0.0,
                'sources': [],
                'reasoning': f"System error during query processing: {str(e)}",
                'processing_time': round(time.time() - start_time, 3)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics"""
        return {
            'vector_store_stats': self.vector_store.get_statistics(),
            'system_ready': self.vector_store.is_trained,
            'components': {
                'document_processor': 'ready',
                'chunk_manager': 'ready',
                'vector_store': 'ready' if self.vector_store.is_trained else 'empty',
                'mistral_client': 'ready' if self.mistral_client else 'not configured'
            }
        }
