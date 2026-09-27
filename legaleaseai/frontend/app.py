from pathlib import Path
import sys

import requests
import streamlit as st


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from services.document_formatter import (
    format_docx,
    format_pdf,
    format_txt,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="LegalEase AI",
    page_icon="⚖️",
    layout="wide",
)


BACKEND_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .subtitle {
            font-size: 18px;
            color: #9ca3af;
            margin-bottom: 25px;
        }

        .stTextArea textarea {
            min-height: 120px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">⚖️ LegalEase AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered legal document drafting assistant"
    "</div>",
    unsafe_allow_html=True,
)


st.info(
    "LegalEase creates editable legal-document drafts. "
    "Review the generated document carefully before using it."
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    backend_url = st.text_input(
        "Backend URL",
        value=BACKEND_URL,
    )

    st.divider()

    st.markdown("### 📄 Supported formats")
    st.write("• DOCX")
    st.write("• PDF")
    st.write("• TXT")

    st.divider()

    st.caption(
        "LegalEase is an AI drafting tool and does not replace "
        "professional legal advice."
    )


# ---------------------------------------------------------
# Main form
# ---------------------------------------------------------
st.subheader("Create a Legal Document")

document_type = st.selectbox(
    "Document Type",
    [
        "Non-Disclosure Agreement",
        "Rental Agreement",
        "Employment Agreement",
        "Service Agreement",
        "Partnership Agreement",
        "Sale Agreement",
        "Privacy Agreement",
        "General Legal Agreement",
    ],
)


parties = st.text_area(
    "Parties",
    placeholder=(
        "Example:\n"
        "Party A: Alice Johnson\n"
        "Party B: Example Technologies Pvt Ltd"
    ),
)


terms = st.text_area(
    "Terms / Conditions",
    placeholder=(
        "Example:\n"
        "Confidentiality must be maintained; "
        "payment of ₹50,000; "
        "agreement duration of 12 months; "
        "termination with 30 days notice."
    ),
)


dates = st.text_input(
    "Effective Date / Date Information",
    placeholder="Example: 01 October 2026",
)


# ---------------------------------------------------------
# Generate document
# ---------------------------------------------------------
generate_button = st.button(
    "✨ Generate Document",
    type="primary",
    use_container_width=True,
)


if generate_button:

    if not parties.strip():
        st.error("Please enter the parties.")
        st.stop()

    if not terms.strip():
        st.error("Please enter the terms / conditions.")
        st.stop()

    if not dates.strip():
        st.error("Please enter the date information.")
        st.stop()

    payload = {
        "document_type": document_type,
        "parties": parties,
        "terms": terms,
        "dates": dates,
    }

    with st.spinner("Generating your legal document..."):

        try:
            response = requests.post(
                f"{backend_url.rstrip('/')}/generate",
                json=payload,
                timeout=120,
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Backend server is not running.\n\n"
                "Start it with:\n"
                "`python -m uvicorn backend.main:app --reload`"
            )
            st.stop()

        except requests.exceptions.Timeout:
            st.error("❌ Backend request timed out.")
            st.stop()

        except requests.RequestException as exc:
            st.error(f"❌ Request failed: {exc}")
            st.stop()

    if response.status_code == 200:

        data = response.json()

        generated_content = data.get("content", "").strip()

        if not generated_content:
            st.error("The AI returned an empty document.")
            st.stop()

        st.session_state["generated_content"] = generated_content
        st.session_state["document_type"] = document_type

        st.success("✅ Document generated successfully!")

    else:

        try:
            error_data = response.json()
            error_message = error_data.get(
                "detail",
                "Unknown backend error.",
            )
        except ValueError:
            error_message = response.text

        st.error(
            f"❌ Document generation failed.\n\n"
            f"{error_message}"
        )


# ---------------------------------------------------------
# Display generated document
# ---------------------------------------------------------
if "generated_content" in st.session_state:

    st.divider()

    st.subheader("📄 Generated Document")

    generated_content = st.session_state["generated_content"]
    generated_title = st.session_state.get(
        "document_type",
        "Legal Document",
    )

    edited_content = st.text_area(
        "Edit your document",
        value=generated_content,
        height=600,
    )

    # Keep edited version
    st.session_state["generated_content"] = edited_content

    st.divider()

    st.subheader("⬇️ Download")

    col1, col2, col3 = st.columns(3)

    # -----------------------------------------------------
    # TXT
    # -----------------------------------------------------
    with col1:

        txt_data = format_txt(edited_content)

        st.download_button(
            label="📄 Download TXT",
            data=txt_data,
            file_name="LegalEase_Document.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # -----------------------------------------------------
    # DOCX
    # -----------------------------------------------------
    with col2:

        docx_data = format_docx(
            edited_content,
            generated_title,
        )

        st.download_button(
            label="📝 Download DOCX",
            data=docx_data,
            file_name="LegalEase_Document.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------
    with col3:

        pdf_data = format_pdf(
            edited_content,
            generated_title,
        )

        st.download_button(
            label="📕 Download PDF",
            data=pdf_data,
            file_name="LegalEase_Document.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.divider()

st.caption(
    "LegalEase AI • AI-generated legal drafts should be reviewed "
    "for accuracy and applicable local requirements."
)