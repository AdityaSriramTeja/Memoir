from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# psql -d "postgres://postgres:password@localhost/postgres"
URL_DATABASE = "postgresql://postgres:password@localhost/postgres"

engine = create_engine(URL_DATABASE)

# Create vector extension if it doesn't exist
with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()