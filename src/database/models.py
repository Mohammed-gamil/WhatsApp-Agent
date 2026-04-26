from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
import datetime

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

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True)
    phone_number = Column(String, index=True)
    role = Column(String) # 'user' or 'agent'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
