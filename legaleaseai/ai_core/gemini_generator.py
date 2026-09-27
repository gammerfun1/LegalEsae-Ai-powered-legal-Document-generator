import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


SYSTEM_INSTRUCTION = """
You are LegalEase, an AI assistant for drafting general legal-document templates.

Create a clear, editable legal-document DRAFT from the user's supplied information.

Do not invent names, dates, addresses, amounts, laws, citations, registration
numbers, or other facts that were not provided.

Use professional and neutral language.

Use placeholders such as [ADDRESS], [AMOUNT], or [GOVERNING LAW] only when
they are genuinely needed.

Return plain text only. Do not use Markdown, HTML, or code fences.

Include:
- Document title
- Relevant sections
- Numbered clauses
- Signature section
"""


class GeminiDocumentGenerator:

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY", "").strip()
        )

        self.model_name = (
            model_name
            or os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash",
            )
        )

        self.client = (
            genai.Client(api_key=self.api_key)
            if self.api_key
            else None
        )

    def _prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        return f"""
Draft a {document_type} using only the supplied information.

PARTIES:
{parties}

TERMS / CONDITIONS:
{terms}

DATE INFORMATION:
{dates}

Requirements:

1. Create a professional editable legal-document draft.
2. Include the supplied parties accurately.
3. Include the supplied date information accurately.
4. Convert the supplied terms into clear clauses.
5. Use appropriate standard sections.
6. Do not invent missing facts.
7. Include signature blocks for the relevant parties.
"""

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        if not self.client:
            raise ValueError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self._prompt(
                    document_type,
                    parties,
                    terms,
                    dates,
                ),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2,
                    max_output_tokens=12000,
                ),
            )

        except Exception as exc:
            raise RuntimeError(
                f"Gemini request failed: {exc}"
            ) from exc

        text = (response.text or "").strip()

        if not text:
            raise RuntimeError(
                "Gemini returned an empty document."
            )

        max_chars = int(
            os.getenv(
                "MAX_GENERATION_CHARS",
                "30000",
            )
        )

        return text[:max_chars]