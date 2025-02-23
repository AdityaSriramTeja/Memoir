from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import insert
from database import Base
from pgvector.sqlalchemy import Vector

class Topics(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, unique=True)

class Connections(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_topic = Column(Integer, index=True)
    target_topic = Column(Integer, index=True)
    __table_args__ = (UniqueConstraint("source_topic", "target_topic", name="two_columns"),)

class Sources(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), index=True)
    vector_2d = Column(Vector(2))  # For visualization
    vector_768d = Column(Vector(768))  # Full embedding for similarity search
    url = Column(String, nullable=True)
    page_type = Column(String, index=True)
    content = Column(String)

class Websites(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String, index=True, unique=True)
    content = Column(Text)
    page_type = Column(String, index=True)
