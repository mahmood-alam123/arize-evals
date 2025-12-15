"""
RAG workflow implementation with embeddings-based retrieval.

This module demonstrates a realistic RAG pattern:
1. Document embeddings stored in-memory
2. Query embedding for semantic search
3. Cosine similarity-based retrieval
4. Context-grounded answer generation
"""

import os
import numpy as np
from typing import List, Dict, Tuple, Optional
from openai import OpenAI


# Sample knowledge base for our fictional SaaS product
KNOWLEDGE_BASE = [
    {
        "id": "doc_001",
        "title": "Getting Started with API Authentication",
        "content": """To authenticate with our API, you need to create an API token. 
        Navigate to Settings > API Tokens in your dashboard. Click 'Generate New Token', 
        give it a descriptive name, and set the appropriate permissions. The token will 
        only be shown once, so save it securely. Include it in requests using the 
        'Authorization: Bearer YOUR_TOKEN' header."""
    },
    {
        "id": "doc_002",
        "title": "Billing and Pricing Plans",
        "content": """We offer three pricing tiers: Starter ($29/month), Professional ($99/month), 
        and Enterprise (custom pricing). All plans include unlimited users and 99.9% uptime SLA. 
        The Starter plan includes 10,000 API calls per month, Professional includes 100,000 calls, 
        and Enterprise includes unlimited calls. You can upgrade or downgrade at any time, 
        and changes take effect immediately. We accept credit cards and invoice billing for 
        annual Enterprise contracts."""
    },
    {
        "id": "doc_003",
        "title": "Webhook Configuration",
        "content": """Webhooks allow you to receive real-time notifications when events occur. 
        To set up a webhook, go to Settings > Webhooks and click 'Add Endpoint'. Enter your 
        endpoint URL (must be HTTPS) and select which events to subscribe to. We'll send a 
        POST request to your endpoint with a JSON payload. Verify webhook signatures using 
        the secret key provided. Webhooks have a 5-second timeout and will retry up to 3 times 
        with exponential backoff."""
    },
    {
        "id": "doc_004",
        "title": "Data Export and Backup",
        "content": """You can export your data at any time in JSON or CSV format. Go to 
        Settings > Data Management and click 'Export Data'. Select the date range and 
        data types you want to include. Large exports are processed asynchronously and you'll 
        receive an email with a download link when ready. We automatically back up all data 
        daily with 30-day retention. Enterprise customers can request custom backup schedules."""
    },
    {
        "id": "doc_005",
        "title": "Security and Compliance",
        "content": """Our platform is SOC 2 Type II certified and GDPR compliant. All data 
        is encrypted at rest using AES-256 and in transit using TLS 1.3. We support SSO via 
        SAML 2.0 and OAuth 2.0. Two-factor authentication (2FA) is available and required 
        for Enterprise plans. We conduct regular security audits and penetration testing. 
        Customer data is stored in AWS data centers with geographic redundancy."""
    },
    {
        "id": "doc_006",
        "title": "Rate Limits and Throttling",
        "content": """API rate limits are enforced per token and vary by plan. Starter: 
        100 requests/minute, Professional: 500 requests/minute, Enterprise: 2000 requests/minute. 
        When you exceed the limit, you'll receive a 429 status code with a Retry-After header. 
        Implement exponential backoff in your client code. Rate limits reset every minute. 
        Burst allowances permit brief spikes up to 2x the limit for up to 10 seconds."""
    }
]


class RAGWorkflow:
    """RAG workflow with embeddings-based retrieval."""
    
    def __init__(self, model: str = "gpt-4o-mini", embedding_model: str = "text-embedding-3-small"):
        """
        Initialize the RAG workflow.
        
        Args:
            model: OpenAI model for answer generation
            embedding_model: OpenAI model for embeddings
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model
        self.embedding_model = embedding_model
        self.documents = KNOWLEDGE_BASE
        self.document_embeddings: Optional[Dict[str, np.ndarray]] = None
        
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text string."""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return np.array(response.data[0].embedding)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def index_documents(self):
        """Create embeddings for all documents in the knowledge base."""
        print("Indexing documents...")
        self.document_embeddings = {}
        
        for doc in self.documents:
            # Combine title and content for better retrieval
            text = f"{doc['title']}. {doc['content']}"
            embedding = self._get_embedding(text)
            self.document_embeddings[doc['id']] = embedding
        
        print(f"Indexed {len(self.document_embeddings)} documents")
    
    def retrieve(self, query: str, top_k: int = 2) -> List[Dict]:
        """
        Retrieve most relevant documents for a query.
        
        Args:
            query: User query string
            top_k: Number of documents to retrieve
            
        Returns:
            List of document dictionaries with relevance scores
        """
        if self.document_embeddings is None:
            self.index_documents()
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Calculate similarities
        similarities = []
        for doc in self.documents:
            doc_embedding = self.document_embeddings[doc['id']]
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append({
                'document': doc,
                'score': similarity
            })
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x['score'], reverse=True)
        return similarities[:top_k]
    
    def answer_with_rag(self, query: str, top_k: int = 2) -> Dict[str, any]:
        """
        Answer a query using RAG with embeddings-based retrieval.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            
        Returns:
            Dict with keys:
            - "answer": Generated answer
            - "retrieved_docs": List of retrieved documents with scores
            - "context": Combined context string used
        """
        # Retrieve relevant documents
        retrieved = self.retrieve(query, top_k)
        
        # Build context from retrieved documents
        context_parts = []
        for i, item in enumerate(retrieved, 1):
            doc = item['document']
            score = item['score']
            context_parts.append(
                f"[Document {i}] {doc['title']}\n{doc['content']}"
            )
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using context
        system_prompt = """You are a helpful customer support assistant for a SaaS product.
Answer the user's question using ONLY the information provided in the context documents.

Important guidelines:
- If the answer is not in the context, clearly state "I don't have that information in our documentation."
- Do not make up information or use knowledge outside the provided context
- Be specific and reference relevant details from the context
- If multiple documents are relevant, synthesize information from both"""
        
        user_message = f"""Context documents:
{context}

User question: {query}

Please provide a helpful answer based solely on the context above."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=400
        )
        
        answer = response.choices[0].message.content.strip()
        
        return {
            "answer": answer,
            "retrieved_docs": [
                {
                    "id": item['document']['id'],
                    "title": item['document']['title'],
                    "score": float(item['score'])
                }
                for item in retrieved
            ],
            "context": context
        }


# Global instance for reuse across batch operations
_rag_workflow_instance: Optional[RAGWorkflow] = None


def get_rag_workflow() -> RAGWorkflow:
    """Get or create the global RAG workflow instance."""
    global _rag_workflow_instance
    if _rag_workflow_instance is None:
        _rag_workflow_instance = RAGWorkflow()
        _rag_workflow_instance.index_documents()  # Pre-index on first use
    return _rag_workflow_instance


def answer_with_rag(query: str, context: Optional[str] = None) -> str:
    """
    Simple interface for RAG answer generation.
    
    Args:
        query: User query
        context: Optional pre-provided context (if None, retrieval is performed)
        
    Returns:
        Answer string
    """
    workflow = get_rag_workflow()
    result = workflow.answer_with_rag(query)
    return result["answer"]


def rag_batch_with_retrieval(queries: List[str]) -> List[Dict]:
    """
    Process multiple queries through RAG with retrieval.
    
    Args:
        queries: List of query strings
        
    Returns:
        List of result dictionaries
    """
    workflow = get_rag_workflow()
    results = []
    
    for query in queries:
        try:
            result = workflow.answer_with_rag(query)
            results.append(result)
        except Exception as e:
            results.append({
                "answer": f"ERROR: {str(e)}",
                "retrieved_docs": [],
                "context": ""
            })
    
    return results


# Example usage
if __name__ == "__main__":
    # Test queries
    test_queries = [
        "How do I create an API token?",
        "What are your pricing plans?",
        "Do you support cryptocurrency payments?"  # Should return "no info"
    ]
    
    workflow = RAGWorkflow()
    workflow.index_documents()
    
    print("=" * 70)
    print("RAG WITH EMBEDDINGS - TEST")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query}")
        print('='*70)
        
        result = workflow.answer_with_rag(query)
        
        print("\nRetrieved Documents:")
        for doc_info in result['retrieved_docs']:
            print(f"  • {doc_info['title']} (relevance: {doc_info['score']:.3f})")
        
        print(f"\nAnswer:\n{result['answer']}")
