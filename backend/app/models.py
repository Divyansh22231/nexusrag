from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class UploadResponse(BaseModel):
    document_id: str
    message: str
