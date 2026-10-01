import os
import io
import docx
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class BaseExporter(ABC):
    @abstractmethod
    def export(self, cdm_data: Dict[str, Any], publisher_code: str = "IEEE") -> Tuple[bytes, str, str]:
        """
        Exports CDM to file bytes.
        Returns: (file_bytes, file_extension, mime_type)
        """
        pass


class PdfExporter(BaseExporter):
    def export(self, cdm_data: Dict[str, Any], publisher_code: str = "IEEE") -> Tuple[bytes, str, str]:
        metadata = cdm_data.get("metadata", {})
        sections = cdm_data.get("sections", [])
        references = cdm_data.get("references", [])

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            alignment=1,  # Centered
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=12
        )
        author_style = ParagraphStyle(
            'DocAuthor',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            leading=12,
            alignment=1,
            textColor=colors.HexColor('#475569'),
            spaceAfter=15
        )
        heading_style = ParagraphStyle(
            'DocHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155'),
            spaceAfter=8
        )

        story = []
        
        # Publisher Header Badge
        story.append(Paragraph(f"<b>[{publisher_code} Format Export]</b>", ParagraphStyle('PubTag', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#2563EB'), alignment=1)))
        story.append(Spacer(1, 8))

        # Title
        story.append(Paragraph(metadata.get("title", "Research Paper"), title_style))

        # Authors
        authors = metadata.get("authors", [])
        if authors:
            auth_str = ", ".join([a.get("name", "") + (f" ({a.get('affiliation')})" if a.get("affiliation") else "") for a in authors])
            story.append(Paragraph(auth_str, author_style))

        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=12))

        # Abstract
        abstract = metadata.get("abstract", "")
        if abstract:
            story.append(Paragraph("<b>Abstract</b>", heading_style))
            story.append(Paragraph(f"<i>{abstract}</i>", body_style))
            story.append(Spacer(1, 10))

        # Sections
        for sec in sections:
            story.append(Paragraph(sec.get("title", "Section"), heading_style))
            content = sec.get("content", "")
            # Split paragraphs
            paragraphs = content.split("\n\n")
            for p in paragraphs:
                if p.strip():
                    story.append(Paragraph(p.strip(), body_style))

        # References
        if references:
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>References</b>", heading_style))
            for ref in references:
                ref_text = ref.get("text") or f"{ref.get('key', '[1]')} {ref.get('title', 'Reference item')}"
                story.append(Paragraph(ref_text, ParagraphStyle('RefStyle', parent=body_style, fontSize=9, leading=12)))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes, ".pdf", "application/pdf"


class DocxExporter(BaseExporter):
    def export(self, cdm_data: Dict[str, Any], publisher_code: str = "IEEE") -> Tuple[bytes, str, str]:
        metadata = cdm_data.get("metadata", {})
        sections = cdm_data.get("sections", [])
        references = cdm_data.get("references", [])

        doc = docx.Document()
        
        # Header / Title
        p_title = doc.add_heading(metadata.get("title", "Research Paper"), level=0)
        p_title.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER

        authors = metadata.get("authors", [])
        if authors:
            auth_str = ", ".join([a.get("name", "") + (f" ({a.get('affiliation')})" if a.get("affiliation") else "") for a in authors])
            p_auth = doc.add_paragraph(auth_str)
            p_auth.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER

        # Abstract
        abstract = metadata.get("abstract", "")
        if abstract:
            doc.add_heading("Abstract", level=1)
            p_abs = doc.add_paragraph(abstract)
            p_abs.runs[0].italic = True

        # Sections
        for sec in sections:
            doc.add_heading(sec.get("title", "Section"), level=sec.get("level", 1))
            content = sec.get("content", "")
            for para in content.split("\n\n"):
                if para.strip():
                    doc.add_paragraph(para.strip())

        # References
        if references:
            doc.add_heading("References", level=1)
            for ref in references:
                ref_text = ref.get("text") or f"{ref.get('key', '[1]')} {ref.get('title', 'Reference item')}"
                doc.add_paragraph(ref_text)

        buffer = io.BytesIO()
        doc.save(buffer)
        docx_bytes = buffer.getvalue()
        buffer.close()
        return docx_bytes, ".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class LatexExporter(BaseExporter):
    def export(self, cdm_data: Dict[str, Any], publisher_code: str = "IEEE") -> Tuple[bytes, str, str]:
        metadata = cdm_data.get("metadata", {})
        sections = cdm_data.get("sections", [])
        references = cdm_data.get("references", [])

        title = metadata.get("title", "Research Document")
        abstract = metadata.get("abstract", "")
        authors = metadata.get("authors", [])

        auth_latex = " \\and ".join([a.get("name", "Author") for a in authors]) if authors else "Author"

        tex_lines = [
            "\\documentclass[10pt,journal,compsoc]{IEEEtran}",
            "\\usepackage{cite}",
            "\\usepackage{amsmath,amssymb,amsfonts}",
            "\\usepackage{graphicx}",
            "\\begin{document}",
            f"\\title{{{title}}}",
            f"\\author{{{auth_latex}}}",
            "\\maketitle",
        ]

        if abstract:
            tex_lines.extend([
                "\\begin{abstract}",
                abstract,
                "\\end{abstract}"
            ])

        for sec in sections:
            sec_title = sec.get("title", "Section")
            tex_lines.append(f"\\section{{{sec_title}}}")
            content = sec.get("content", "")
            tex_lines.append(content)

        if references:
            tex_lines.extend([
                "\\begin{thebibliography}{10}",
            ])
            for idx, ref in enumerate(references, start=1):
                ref_text = ref.get("text", "Reference item")
                tex_lines.append(f"\\bibitem{{ref{idx}}} {ref_text}")
            tex_lines.append("\\end{thebibliography}")

        tex_lines.append("\\end{document}")

        latex_str = "\n\n".join(tex_lines)
        return latex_str.encode("utf-8"), ".tex", "application/x-tex"


class HtmlExporter(BaseExporter):
    def export(self, cdm_data: Dict[str, Any], publisher_code: str = "IEEE") -> Tuple[bytes, str, str]:
        metadata = cdm_data.get("metadata", {})
        sections = cdm_data.get("sections", [])
        references = cdm_data.get("references", [])

        title = metadata.get("title", "Research Document")
        abstract = metadata.get("abstract", "")
        authors = metadata.get("authors", [])
        authors_html = ", ".join([f"<span>{a.get('name')}</span>" for a in authors])

        sections_html = ""
        for sec in sections:
            sections_html += f"<section><h2>{sec.get('title')}</h2><p>{sec.get('content')}</p></section>"

        references_html = ""
        if references:
            references_html = "<section><h2>References</h2><ol>" + "".join([f"<li>{r.get('text', 'Reference')}</li>" for r in references]) + "</ol></section>"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Times New Roman', Times, serif; margin: 40px auto; max-width: 800px; color: #111; line-height: 1.6; }}
        h1 {{ text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 8px; }}
        .authors {{ text-align: center; font-style: italic; color: #555; margin-bottom: 24px; }}
        .abstract {{ background: #f8fafc; padding: 16px; border-left: 4px solid #2563eb; margin-bottom: 24px; }}
        h2 {{ font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 4px; color: #1e293b; margin-top: 24px; }}
        section {{ margin-bottom: 16px; }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <div class="authors">{authors_html}</div>
    </header>
    {f'<div class="abstract"><strong>Abstract — </strong>{abstract}</div>' if abstract else ''}
    <main>
        {sections_html}
        {references_html}
    </main>
</body>
</html>"""

        return html_content.encode("utf-8"), ".html", "text/html"


class ExporterFactory:
    @staticmethod
    def get_exporter(export_format: str) -> BaseExporter:
        fmt = export_format.upper()
        if fmt == "PDF":
            return PdfExporter()
        elif fmt in ["DOCX", "DOC"]:
            return DocxExporter()
        elif fmt in ["LATEX", "TEX"]:
            return LatexExporter()
        elif fmt == "HTML":
            return HtmlExporter()
        else:
            return PdfExporter()
