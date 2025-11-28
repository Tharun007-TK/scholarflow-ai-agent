from typing import List, Dict, Any
from ..adk.tools import Tool

import numpy as np
import json
import os
import uuid
import google.generativeai as genai
from typing import List, Dict, Any

class SimpleVectorStore:
    """A lightweight, NumPy-based vector store."""
    def __init__(self, persist_path: str = "vector_store.json"):
        self.persist_path = persist_path
        self.documents = []
        self.metadatas = []
        self.embeddings = []
        self.load()

    def add(self, text: str, embedding: List[float], metadata: Dict[str, Any]):
        self.documents.append(text)
        self.embeddings.append(embedding)
        self.metadatas.append(metadata)
        self.save()

    def search(self, query_embedding: List[float], n_results: int = 3) -> List[Dict[str, Any]]:
        if not self.embeddings:
            return []
        
        # Calculate cosine similarity
        query_vec = np.array(query_embedding)
        doc_vecs = np.array(self.embeddings)
        
        # Normalize vectors
        norm_query = np.linalg.norm(query_vec)
        norm_docs = np.linalg.norm(doc_vecs, axis=1)
        
        # Avoid division by zero
        if norm_query == 0:
            return []
        
        similarities = np.dot(doc_vecs, query_vec) / (norm_docs * norm_query)
        
        # Get top N indices
        top_indices = np.argsort(similarities)[::-1][:n_results]
        
        results = []
        for idx in top_indices:
            results.append({
                "content": self.documents[idx],
                "metadata": self.metadatas[idx],
                "score": float(similarities[idx])
            })
        return results

    def save(self):
        data = {
            "documents": self.documents,
            "metadatas": self.metadatas,
            "embeddings": self.embeddings
        }
        with open(self.persist_path, 'w') as f:
            json.dump(data, f)

    def load(self):
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadatas = data.get("metadatas", [])
                    self.embeddings = data.get("embeddings", [])
            except Exception:
                pass

class EmbeddingSearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="embedding_search",
            description="Searches memory using embeddings.",
            args_schema=None
        )
        self.vector_store = SimpleVectorStore()

    def _get_embedding(self, text: str) -> List[float]:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def index_document(self, text: str, metadata: Dict[str, Any]):
        """Chunks and indexes the document text."""
        # Simple chunking by paragraphs or fixed size
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        
        for chunk in chunks:
            try:
                embedding = self._get_embedding(chunk)
                self.vector_store.add(chunk, embedding, metadata)
            except Exception as e:
                print(f"Error indexing chunk: {e}")

    def run(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        try:
            query_embedding = self._get_embedding(query)
            return self.vector_store.search(query_embedding, n_results)
        except Exception as e:
            print(f"Error searching: {e}")
            return []

class CalendarTool(Tool):
    def __init__(self):
        super().__init__(
            name="calendar_tool",
            description="Checks date validity.",
            args_schema=None
        )

    def run(self, date_str: str) -> bool:
        # Mock implementation
        return True
