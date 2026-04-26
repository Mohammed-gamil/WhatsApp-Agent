from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class SalesLead(Base):
    __tablename__ = 'sales_leads'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    company = Column(String)
    status = Column(String, default="new")
    notes = Column(Text)

class KnowledgeDocument(Base):
    __tablename__ = 'knowledge_documents'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536)) # OpenAI embedding size
