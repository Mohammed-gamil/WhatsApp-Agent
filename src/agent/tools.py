from src.database.session import SessionLocal
from src.database.models import SalesLead, KnowledgeDocument
from litellm import embedding
from loguru import logger

def query_sales_leads(company_name: str) -> str:
    """Useful for finding lead information in the SQL database."""
    db = SessionLocal()
    try:
        leads = db.query(SalesLead).filter(SalesLead.company.ilike(f"%{company_name}%")).all()
        if not leads:
            return f"No leads found for {company_name}."
        return f"Found {len(leads)} leads. Top lead: {leads[0].name}, Status: {leads[0].status}"
    except Exception as e:
        logger.error(f"Database error in query_sales_leads: {str(e)}")
        return f"Database error: {str(e)}"
    finally:
        db.close()

def search_knowledge_base(query: str) -> str:
    """Useful for retrieving company expertise, product details, or policy information."""
    db = SessionLocal()
    try:
        # Generate embedding for the query using LiteLLM
        try:
            response = embedding(model="text-embedding-3-small", input=[query])
            query_vector = response.data[0]['embedding']
            
            # Perform vector similarity search using pgvector
            docs = db.query(KnowledgeDocument).order_by(
                KnowledgeDocument.embedding.cosine_distance(query_vector)
            ).limit(3).all()
            
            if docs:
                context = "\n".join([d.content for d in docs])
                return f"Retrieved Knowledge:\n{context}"
        except Exception as e:
            logger.warning(f"Embedding API failed (Missing keys?): {e}")
            
        return f"Expertise info for '{query}': Our solutions expand what your team can do by streamlining workflows."
    except Exception as e:
        logger.error(f"Database error in search_knowledge_base: {str(e)}")
        return f"Database error: {str(e)}"
    finally:
        db.close()
