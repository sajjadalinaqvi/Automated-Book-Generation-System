import pinecone
from django.conf import settings
import hashlib


class PineconeService:
    def __init__(self):
        try:
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            self.index_name = settings.PINECONE_INDEX_NAME
            self.index = pinecone.Index(self.index_name)
            print("Pinecone initialized successfully")
        except Exception as e:
            print(f"Pinecone initialization error: {e}")
            self.index = None
    
    def embed_chapter_summary(self, book_id, chapter_number, summary):
        """Store chapter summary in Pinecone for RAG retrieval"""
        if not self.index:
            print("Pinecone not available, skipping storage")
            return
            
        try:
            vector_id = f"book_{book_id}_chapter_{chapter_number}"
            embedding = self._create_simple_embedding(summary)
            
            metadata = {
                "book_id": str(book_id),
                "chapter_number": chapter_number,
                "content_type": "chapter_summary",
                "text": summary[:1000]
            }
            
            self.index.upsert([(vector_id, embedding, metadata)])
            print(f"✅ Stored chapter {chapter_number} summary in Pinecone")
        except Exception as e:
            print(f"❌ Error storing in Pinecone: {e}")
    
    def retrieve_previous_summaries(self, book_id, current_chapter):
        """Retrieve summaries of previous chapters for context"""
        if not self.index:
            return []
            
        try:
            results = self.index.query(
                vector=[0.0] * 384,
                filter={
                    "book_id": {"$eq": str(book_id)},
                    "chapter_number": {"$lt": current_chapter},
                    "content_type": {"$eq": "chapter_summary"}
                },
                top_k=10,
                include_metadata=True
            )
            
            summaries = [match.metadata["text"] for match in results.matches]
            print(f"✅ Retrieved {len(summaries)} previous summaries from Pinecone")
            return summaries
        except Exception as e:
            print(f"❌ Error retrieving from Pinecone: {e}")
            return []
    
    def _create_simple_embedding(self, text):
        """Create a simple hash-based embedding"""
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        embedding = []
        for i in range(0, len(hash_hex), 2):
            embedding.append(float(int(hash_hex[i:i+2], 16)) / 255.0)
        
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]