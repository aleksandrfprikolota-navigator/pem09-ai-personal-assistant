"""
Vector Index for RAG.
Creates and manages embeddings using ChromaDB.
"""

from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from config import DATA_DIR, OPENAI_API_KEY, DOCUMENTS_DIR
from utils.logging import logger
from rag.loader import document_loader


class VectorIndex:
    """Manages vector embeddings and similarity search."""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """
        Initialize vector index.
        
        Args:
            persist_directory: Directory to persist embeddings
        """
        if persist_directory is None:
            persist_directory = DATA_DIR / "chroma_db"
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Official OpenAI embeddings endpoint. ProxyAPI is not used.
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY
        )
        self.manifest_path = DATA_DIR / "index_manifest.txt"
        
        # Initialize or load vector store
        self.vectorstore = None
        self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self):
        """Load existing vectorstore or create new one."""
        try:
            # Try to load existing vectorstore
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            logger.info("Loaded existing vector store")
        except Exception as e:
            logger.warning(f"Could not load existing vectorstore: {e}")
            # Create new vectorstore
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            logger.info("Created new vector store")
    
    def add_documents(self, documents: List) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document chunks
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return
            
            self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 3
    ) -> List:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of relevant document chunks
        """
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            logger.debug(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 3
    ) -> List[tuple]:
        """
        Search for similar documents with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of (document, score) tuples
        """
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.debug(f"Found {len(results)} similar documents with scores")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {e}")
            raise
    
    def index_documents_directory(
        self,
        directory: Path = DOCUMENTS_DIR,
        force_reindex: bool = False
    ) -> int:
        """
        Index all documents from a directory.
        
        Args:
            directory: Directory containing documents
            force_reindex: If True, clear existing index first
        
        Returns:
            Number of documents indexed
        """
        try:
            signature = self._sources_signature(directory)

            if not signature:
                logger.warning("No documents found to index")
                return 0

            if not force_reindex and self._manifest_matches(signature):
                count = self.get_stats().get("total_documents", 0)
                if count:
                    logger.info(
                        f"Knowledge base is up to date ({count} chunks). "
                        "Use /index to rebuild."
                    )
                    return count

            logger.info("Rebuilding vector index from data/documents")
            self.clear_index()

            documents = document_loader.load_directory(directory)
            if not documents:
                logger.warning("No documents found to index")
                return 0

            self.add_documents(documents)
            self.manifest_path.write_text(signature, encoding="utf-8")

            logger.info(f"Indexed {len(documents)} document chunks")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
    
    def _sources_signature(self, directory: Path) -> str:
        """Строка из имён, размеров и времени изменения исходных файлов."""
        parts = []
        directory = Path(directory)
        if not directory.exists():
            return ""

        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file() and file_path.suffix.lower() in {".pdf", ".txt", ".md"}:
                stat = file_path.stat()
                parts.append(f"{file_path.name}:{stat.st_size}:{stat.st_mtime_ns}")
        return "|".join(parts)

    def _manifest_matches(self, signature: str) -> bool:
        if not self.manifest_path.exists():
            return False
        current = self.manifest_path.read_text(encoding="utf-8").strip()
        return current == signature

    def clear_index(self):
        """Clear the entire vector store."""
        try:
            # Delete and recreate
            import shutil
            if self.persist_directory.exists():
                shutil.rmtree(self.persist_directory)
            
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self._load_or_create_vectorstore()
            
            logger.info("Vector store cleared")
            
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            raise
    
    def get_stats(self) -> dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        try:
            # ChromaDB collection stats
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "total_documents": count,
                "persist_directory": str(self.persist_directory)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}


# Global index instance
vector_index = VectorIndex()

