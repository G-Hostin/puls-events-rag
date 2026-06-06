from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question utilisateur")


class Source(BaseModel):
    uid: str | None
    title: str | None
    city: str | None
    url: str | None


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class RebuildResponse(BaseModel):
    status: str
    events_fetched: int
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str