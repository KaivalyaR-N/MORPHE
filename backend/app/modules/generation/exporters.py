import os
import io
import docx
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
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

        # Tables
        tables = cdm_data.get("tables", [])
        if tables:
            story.append(Spacer(1, 10))
            for idx, tbl in enumerate(tables, 1):
                caption = tbl.get("caption") or f"Table {idx}"
                story.append(Paragraph(f"<b>{caption}</b>", heading_style))
                headers = tbl.get("headers", [])
                rows = tbl.get("rows", [])
                table_matrix = []
                if headers:
                    table_matrix.append([Paragraph(f"<b>{str(h)}</b>", body_style) for h in headers])
                for r in rows:
                    if isinstance(r, list):
                        table_matrix.append([Paragraph(str(c), body_style) for c in r])
                if table_matrix:
                    rl_tbl = Table(table_matrix, hAlign='LEFT')
                    rl_tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ]))
                    story.append(rl_tbl)
                    story.append(Spacer(1, 8))

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

        # Tables
        tables = cdm_data.get("tables", [])
        for idx, tbl in enumerate(tables, 1):
            caption = tbl.get("caption") or f"Table {idx}"
            doc.add_heading(caption, level=2)
            headers = tbl.get("headers", [])
            rows = tbl.get("rows", [])
            num_cols = max(len(headers), max((len(r) for r in rows), default=0))
            if num_cols > 0:
                t = doc.add_table(rows=0, cols=num_cols)
                t.style = 'Table Grid'
                if headers:
                    hdr_cells = t.add_row().cells
                    for i, h in enumerate(headers):
                        if i < num_cols:
                            hdr_cells[i].text = str(h)
                for r in rows:
                    if isinstance(r, list):
                        row_cells = t.add_row().cells
                        for i, c in enumerate(r):
                            if i < num_cols:
                                row_cells[i].text = str(c)

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
        tables = cdm_data.get("tables", [])

        title = metadata.get("title", "Research Document")
        abstract = metadata.get("abstract", "")
        authors = metadata.get("authors", [])

        auth_latex = " \\and ".join([a.get("name", "Author") for a in authors]) if authors else "Author"

        pub = publisher_code.upper() if publisher_code else "IEEE"
        if pub == "ACM":
            doc_class = "\\documentclass[sigconf]{acmart}"
            author_block = "\n".join([f"\\author{{{a.get('name', 'Author')}}}\n\\affiliation{{\\institution{{{a.get('affiliation', 'Institution')}}}}}" for a in authors]) if authors else "\\author{Author}"
        elif pub == "ELSEVIER":
            doc_class = "\\documentclass[preprint,12pt]{elsarticle}"
            author_block = f"\\author{{{auth_latex}}}"
        elif pub == "SPRINGER":
            doc_class = "\\documentclass{llncs}"
            author_block = f"\\author{{{auth_latex}}}"
        elif pub == "NATURE":
            doc_class = "\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}"
            author_block = f"\\author{{{auth_latex}}}"
        else:  # IEEE default
            doc_class = "\\documentclass[10pt,journal,compsoc]{IEEEtran}"
            author_block = f"\\author{{{auth_latex}}}"

        tex_lines = [
            doc_class,
            "\\usepackage{cite}",
            "\\usepackage{amsmath,amssymb,amsfonts}",
            "\\usepackage{graphicx}",
            "\\usepackage{booktabs}",
            "\\begin{document}",
            f"\\title{{{title}}}",
            author_block,
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

        # Render Tables if any
        for tbl in tables:
            caption = tbl.get("caption", "Table")
            data = tbl.get("data", [])
            if data:
                cols_count = max(len(r) for r in data)
                col_spec = "c" * cols_count
                tbl_tex = [
                    "\\begin{table}[htbp]",
                    f"\\caption{{{caption}}}",
                    "\\centering",
                    f"\\begin{{tabular}}{{{col_spec}}}",
                    "\\toprule"
                ]
                for r_idx, row in enumerate(data):
                    tbl_tex.append(" & ".join(str(cell) for cell in row) + " \\\\")
                    if r_idx == 0:
                        tbl_tex.append("\\midrule")
                tbl_tex.append("\\bottomrule")
                tbl_tex.append("\\end{tabular}")
                tbl_tex.append("\\end{table}")
                tex_lines.append("\n".join(tbl_tex))

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
        tables = cdm_data.get("tables", [])

        title = metadata.get("title", "Research Document")
        abstract = metadata.get("abstract", "")
        authors = metadata.get("authors", [])
        authors_html = ", ".join([f"<span>{a.get('name')}</span>" for a in authors])

        sections_html = ""
        for sec in sections:
            sections_html += f"<section><h2>{sec.get('title')}</h2><p>{sec.get('content')}</p></section>"

        tables_html = ""
        for tbl in tables:
            caption = tbl.get("caption", "Table")
            data = tbl.get("data", [])
            if data:
                rows_html = "".join(["<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>" for row in data])
                tables_html += f"<div class='table-container'><h3>{caption}</h3><table>{rows_html}</table></div>"

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
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        td, th {{ border: 1px solid #cbd5e1; padding: 8px; text-align: left; font-size: 13px; }}
        .table-container h3 {{ font-size: 14px; margin-bottom: 6px; }}
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
        {tables_html}
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
