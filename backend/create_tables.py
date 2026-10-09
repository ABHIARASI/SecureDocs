from app.database import Base, engine
from app.models.user import User
from app.models.document import Document
from app.models.chunk import DocumentChunk

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")