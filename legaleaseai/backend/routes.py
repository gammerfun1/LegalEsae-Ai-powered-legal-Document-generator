import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from ai_core.gemini_generator import GeminiDocumentGenerator


router = APIRouter()

generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=120,
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=4000,
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=8000,
    )

    dates: str = Field(
        ...,
        min_length=2,
        max_length=500,
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "dates",
    )
    @classmethod
    def strip_fields(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty.")

        return value


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    model: str


@router.post(
    "/generate",
    response_model=DocumentResponse,
    tags=["documents"],
)
def generate_document(request: DocumentRequest):

    try:

        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=content,
            model=generator.model_name,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        if os.getenv("LEGAL_EASE_DEBUG", "").lower() == "true":

            raise HTTPException(
                status_code=500,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=500,
            detail="Document generation failed. Check the backend logs.",
        ) from exc