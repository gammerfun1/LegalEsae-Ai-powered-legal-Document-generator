from io import BytesIO
import re

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def sanitize_text(text: str) -> str:
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def format_txt(content: str) -> bytes:
    return sanitize_text(content).encode("utf-8")


def format_docx(
    content: str,
    title: str = "LegalEase Document",
) -> bytes:
    document = Document()

    document.add_heading(
        sanitize_text(title),
        level=1,
    )

    for block in re.split(r"\n\s*\n", content):
        block = block.strip()

        if not block:
            continue

        paragraph = document.add_paragraph(
            sanitize_text(block)
        )
        paragraph.paragraph_format.space_after = 8

    output = BytesIO()
    document.save(output)

    return output.getvalue()


def format_pdf(
    content: str,
    title: str = "LegalEase Document",
) -> bytes:
    output = BytesIO()

    pdf = canvas.Canvas(
        output,
        pagesize=A4,
    )

    width, height = A4
    margin = 50
    y = height - 50

    pdf.setTitle(sanitize_text(title))

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(
        margin,
        y,
        sanitize_text(title),
    )

    y -= 35

    pdf.setFont("Helvetica", 10)

    text_object = pdf.beginText(
        margin,
        y,
    )
    text_object.setLeading(15)

    for paragraph in content.splitlines():

        line = sanitize_text(paragraph.strip())

        if not line:
            text_object.textLine("")
            continue

        words = line.split()
        current_line = ""

        for word in words:

            test_line = (
                f"{current_line} {word}"
                if current_line
                else word
            )

            if len(test_line) > 95:
                text_object.textLine(test_line[:95])
                current_line = ""
                y -= 15

                if y < 60:
                    pdf.drawText(text_object)
                    pdf.showPage()

                    pdf.setFont("Helvetica", 10)

                    text_object = pdf.beginText(
                        margin,
                        height - 50,
                    )
                    text_object.setLeading(15)
                    y = height - 50

            else:
                current_line = test_line

        if current_line:
            text_object.textLine(current_line)
            y -= 15

            if y < 60:
                pdf.drawText(text_object)
                pdf.showPage()

                pdf.setFont("Helvetica", 10)

                text_object = pdf.beginText(
                    margin,
                    height - 50,
                )
                text_object.setLeading(15)
                y = height - 50

    pdf.drawText(text_object)
    pdf.save()

    return output.getvalue()