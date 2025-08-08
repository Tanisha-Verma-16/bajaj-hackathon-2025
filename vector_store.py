import os
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
import re
import math

class SimpleVectorStore:
    """Simple in-memory vector store for semantic search using keyword matching"""
    
    def __init__(self, embedding_model: str = "simple", dimension: int = 384):
        self.embedding_model_name = embedding_model
        self.dimension = dimension
        
        # Simple storage
        self.chunk_metadata = []
        self.is_trained = False
        
        # Storage paths
        self.metadata_path = "chunk_metadata.json"
        
        # Load existing index if available
        self._load_index()
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add document chunks to the vector store"""
        try:
            if not chunks:
                return False
            
            # Store metadata with simple vector IDs
            for i, chunk in enumerate(chunks):
                chunk_meta = chunk.copy()
                chunk_meta['vector_id'] = len(self.chunk_metadata) + i
                chunk_meta['keywords'] = self._extract_keywords(chunk['text'])
                self.chunk_metadata.append(chunk_meta)
            
            self.is_trained = True
            self._save_index()
            
            logging.info(f"Added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logging.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def search(self, query: str, top_k: int = 10, score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Search for relevant chunks using keyword matching"""
        try:
            if not self.is_trained or len(self.chunk_metadata) == 0:
                logging.warning("Vector store is empty or not trained")
                return []
            
            # Extract query keywords
            query_keywords = self._extract_keywords(query)
            
            # Score chunks based on keyword overlap
            results = []
            for chunk in self.chunk_metadata:
                score = self._calculate_similarity(query_keywords, chunk.get('keywords', []), chunk['text'], query)
                if score >= score_threshold:
                    chunk_meta = chunk.copy()
                    chunk_meta['similarity_score'] = score
                    results.append(chunk_meta)
            
            # Sort by similarity score (descending)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Return top_k results
            results = results[:top_k]
            
            logging.info(f"Found {len(results)} relevant chunks for query")
            return results
            
        except Exception as e:
            logging.error(f"Error searching vector store: {str(e)}")
            return []
    
    def search_with_filters(self, query: str, filters: Dict[str, Any] = None, 
                           top_k: int = 10, score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Search with additional metadata filters"""
        try:
            # Get initial search results
            initial_results = self.search(query, top_k * 2, score_threshold)  # Get more for filtering
            
            if not filters:
                return initial_results[:top_k]
            
            # Apply filters
            filtered_results = []
            for result in initial_results:
                matches_filter = True
                
                for filter_key, filter_value in filters.items():
                    if filter_key in result:
                        if isinstance(filter_value, list):
                            # Check if any filter value matches
                            if not any(fv in str(result[filter_key]).lower() for fv in filter_value):
                                matches_filter = False
                                break
                        elif filter_value not in str(result[filter_key]).lower():
                            matches_filter = False
                            break
                
                if matches_filter:
                    filtered_results.append(result)
                
                if len(filtered_results) >= top_k:
                    break
            
            logging.info(f"Filtered results: {len(filtered_results)} from {len(initial_results)}")
            return filtered_results
            
        except Exception as e:
            logging.error(f"Error in filtered search: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_chunks': len(self.chunk_metadata),
            'embedding_dimension': self.dimension,
            'model_name': self.embedding_model_name,
            'is_trained': self.is_trained,
            'unique_sources': len(set(chunk.get('source', '') for chunk in self.chunk_metadata)),
            'content_categories': self._get_category_distribution()
        }
    
    def _get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of content categories"""
        category_counts = {}
        for chunk in self.chunk_metadata:
            categories = chunk.get('content_categories', [])
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts
    
    def _save_index(self):
        """Save metadata"""
        try:
            # Save metadata
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.chunk_metadata, f, ensure_ascii=False, indent=2, default=str)
            
            logging.info("Vector store saved successfully")
            
        except Exception as e:
            logging.error(f"Error saving vector store: {str(e)}")
    
    def _load_index(self):
        """Load existing metadata"""
        try:
            if os.path.exists(self.metadata_path):
                # Load metadata
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.chunk_metadata = json.load(f)
                
                self.is_trained = len(self.chunk_metadata) > 0
                logging.info(f"Loaded vector store with {len(self.chunk_metadata)} vectors")
            
        except Exception as e:
            logging.error(f"Error loading vector store: {str(e)}")
            # Reset to empty state on error
            self.chunk_metadata = []
            self.is_trained = False
    
    def clear(self):
        """Clear all data from vector store"""
        try:
            self.chunk_metadata = []
            self.is_trained = False
            
            # Remove saved files
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            logging.info("Vector store cleared")
            
        except Exception as e:
            logging.error(f"Error clearing vector store: {str(e)}")

class HybridRetriever:
    """Hybrid retrieval combining semantic search with keyword matching"""
    
    def __init__(self, vector_store: SimpleVectorStore):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, top_k: int = 10, 
                semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> List[Dict[str, Any]]:
        """Hybrid retrieval combining semantic and keyword search"""
        try:
            # Get semantic search results
            semantic_results = self.vector_store.search(query, top_k * 2)
            
            # Get keyword matches
            keyword_results = self._keyword_search(query, top_k * 2)
            
            # Combine and re-rank results
            combined_results = self._combine_results(
                semantic_results, keyword_results, 
                semantic_weight, keyword_weight
            )
            
            return combined_results[:top_k]
            
        except Exception as e:
            logging.error(f"Error in hybrid retrieval: {str(e)}")
            return []
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Simple keyword-based search"""
        query_words = set(query.lower().split())
        results = []
        
        for chunk in self.vector_store.chunk_metadata:
            chunk_words = set(chunk['text'].lower().split())
            overlap = len(query_words & chunk_words)
            
            if overlap > 0:
                chunk_copy = chunk.copy()
                chunk_copy['keyword_score'] = overlap / len(query_words)
                results.append(chunk_copy)
        
        # Sort by keyword score
        results.sort(key=lambda x: x['keyword_score'], reverse=True)
        return results[:top_k]
    
    def _combine_results(self, semantic_results: List[Dict[str, Any]], 
                        keyword_results: List[Dict[str, Any]], 
                        semantic_weight: float, keyword_weight: float) -> List[Dict[str, Any]]:
        """Combine and re-rank results from different search methods"""
        combined = {}
        
        # Add semantic results
        for i, result in enumerate(semantic_results):
            chunk_id = result.get('vector_id', f"sem_{i}")
            semantic_score = result.get('similarity_score', 0)
            
            combined[chunk_id] = result.copy()
            combined[chunk_id]['combined_score'] = semantic_score * semantic_weight
            combined[chunk_id]['semantic_score'] = semantic_score
        
        # Add keyword results
        for i, result in enumerate(keyword_results):
            chunk_id = result.get('vector_id', f"key_{i}")
            keyword_score = result.get('keyword_score', 0)
            
            if chunk_id in combined:
                # Combine scores for chunks found by both methods
                combined[chunk_id]['combined_score'] += keyword_score * keyword_weight
                combined[chunk_id]['keyword_score'] = keyword_score
            else:
                combined[chunk_id] = result.copy()
                combined[chunk_id]['combined_score'] = keyword_score * keyword_weight
                combined[chunk_id]['keyword_score'] = keyword_score
        
        # Convert back to list and sort by combined score
        final_results = list(combined.values())
        final_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return final_results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_similarity(self, query_keywords: List[str], chunk_keywords: List[str], chunk_text: str, query: str) -> float:
        """Calculate similarity between query and chunk"""
        if not query_keywords:
            return 0.0
        
        # Keyword overlap score
        overlap = len(set(query_keywords) & set(chunk_keywords))
        keyword_score = overlap / len(query_keywords)
        
        # Text contains exact phrases score
        phrase_score = 0.0
        query_lower = query.lower()
        text_lower = chunk_text.lower()
        
        # Check for exact phrase matches
        if query_lower in text_lower:
            phrase_score = 1.0
        else:
            # Check for partial phrase matches
            query_words = query_lower.split()
            if len(query_words) > 1:
                for i in range(len(query_words) - 1):
                    bigram = ' '.join(query_words[i:i+2])
                    if bigram in text_lower:
                        phrase_score += 0.3
        
        # Combine scores
        final_score = (keyword_score * 0.6) + (min(phrase_score, 1.0) * 0.4)
        return final_score
