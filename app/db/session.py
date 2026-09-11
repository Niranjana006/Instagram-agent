from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from influencer_agent.app.core.config import settings

# Create the engine that connects to Postgres
# pool_pre_ping=True helps handle lost connections
engine = create_engine(str(settings.DATABASE_URL), pool_pre_ping=True)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
