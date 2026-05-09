from sqlmodel import Session, SQLModel, create_engine
from config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url, 
    echo=False,
    connect_args={"check_same_thread": False} # due to Sqlite's threading limitations
)

def create_db_and_tables():
    """Create the database and tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Provide a database session."""
    with Session(engine) as session:
        yield session