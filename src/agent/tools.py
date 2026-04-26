from src.database.session import SessionLocal
from src.database.models import SalesLead

def query_sales_leads(company_name: str) -> str:
    """Useful for finding lead information in the SQL database."""
    db = SessionLocal()
    try:
        leads = db.query(SalesLead).filter(SalesLead.company.ilike(f"%{company_name}%")).all()
        if not leads:
            return f"No leads found for {company_name}."
        return f"Found {len(leads)} leads. Top lead: {leads[0].name}, Status: {leads[0].status}"
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        db.close()

def search_knowledge_base(query: str) -> str:
    """Useful for retrieving company expertise, product details, or policy information."""
    # Placeholder for actual vector search
    # In reality: query -> embed -> pgvector cosine distance -> return content
    return f"Expertise info for '{query}': Our solutions expand what your team can do by streamlining workflows."
