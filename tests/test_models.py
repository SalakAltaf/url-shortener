from app.models import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.database import engine, SessionLocal
# Setup in-memory SQLite DB for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the test DB
Base.metadata.create_all(bind=engine)

def test_url_model():
    session = TestingSessionLocal()
    new_url = URL(target_url="https://example.com", short_code="abc123")
    session.add(new_url)
    session.commit()
    saved_url = session.query(URL).filter_by(short_code="abc123").first()

    assert saved_url is not None
    assert saved_url.target_url == "https://example.com"
    assert saved_url.short_code == "abc123"

    session.close()
