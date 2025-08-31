"""
Database models and setup for Smart Charter Party Generator
"""

import os
from datetime import datetime
from typing import Optional, List, Any, Dict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_cp_generator.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAlchemy Models
class CPTemplateDB(Base):
    __tablename__ = "cp_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)  # GENCON, NYPE, SHELLTIME, etc.
    file_path = Column(String)
    processed_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RecapDocumentDB(Base):
    __tablename__ = "recap_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    file_path = Column(String)
    parsed_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GeneratedCPDB(Base):
    __tablename__ = "generated_cps"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, index=True)
    recap_id = Column(Integer, index=True)
    output_path = Column(String)
    changes_tracked = Column(JSON)
    format = Column(String)  # docx, pdf, html
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class CPTemplateBase(BaseModel):
    name: str
    type: str
    file_path: str
    processed_data: Dict[str, Any]

class CPTemplateCreate(CPTemplateBase):
    pass

class CPTemplate(CPTemplateBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    def save(self, db: Session) -> int:
        """Save template to database"""
        db_template = CPTemplateDB(**self.dict(exclude={"id"}))
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template.id
    
    @classmethod
    def get_by_id(cls, db: Session, template_id: int) -> Optional["CPTemplate"]:
        """Get template by ID"""
        db_template = db.query(CPTemplateDB).filter(CPTemplateDB.id == template_id).first()
        if db_template:
            return cls.from_orm(db_template)
        return None
    
    @classmethod
    def get_all(cls, db: Session) -> List["CPTemplate"]:
        """Get all templates"""
        db_templates = db.query(CPTemplateDB).all()
        return [cls.from_orm(template) for template in db_templates]

class RecapDocumentBase(BaseModel):
    name: str
    file_path: str
    parsed_data: Dict[str, Any]

class RecapDocumentCreate(RecapDocumentBase):
    pass

class RecapDocument(RecapDocumentBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    def save(self, db: Session) -> int:
        """Save recap document to database"""
        db_recap = RecapDocumentDB(**self.dict(exclude={"id"}))
        db.add(db_recap)
        db.commit()
        db.refresh(db_recap)
        return db_recap.id
    
    @classmethod
    def get_by_id(cls, db: Session, recap_id: int) -> Optional["RecapDocument"]:
        """Get recap document by ID"""
        db_recap = db.query(RecapDocumentDB).filter(RecapDocumentDB.id == recap_id).first()
        if db_recap:
            return cls.from_orm(db_recap)
        return None
    
    @classmethod
    def get_all(cls, db: Session) -> List["RecapDocument"]:
        """Get all recap documents"""
        db_recaps = db.query(RecapDocumentDB).all()
        return [cls.from_orm(recap) for recap in db_recaps]

class GeneratedCPBase(BaseModel):
    template_id: int
    recap_id: int
    output_path: str
    changes_tracked: List[Dict[str, Any]]
    format: str

class GeneratedCPCreate(GeneratedCPBase):
    pass

class GeneratedCP(GeneratedCPBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    def save(self, db: Session) -> int:
        """Save generated CP to database"""
        db_cp = GeneratedCPDB(**self.dict(exclude={"id"}))
        db.add(db_cp)
        db.commit()
        db.refresh(db_cp)
        return db_cp.id
    
    @classmethod
    def get_by_id(cls, db: Session, cp_id: int) -> Optional["GeneratedCP"]:
        """Get generated CP by ID"""
        db_cp = db.query(GeneratedCPDB).filter(GeneratedCPDB.id == cp_id).first()
        if db_cp:
            return cls.from_orm(db_cp)
        return None
    
    @classmethod
    def get_all(cls, db: Session) -> List["GeneratedCP"]:
        """Get all generated CPs"""
        db_cps = db.query(GeneratedCPDB).all()
        return [cls.from_orm(cp) for cp in db_cps]
