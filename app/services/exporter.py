from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ResumeExporter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, text: str, output_format: str) -> str | None:
        if output_format == "text":
            path = self.output_dir / f"optimized_resume_{uuid4().hex[:8]}.txt"
            path.write_text(text, encoding="utf-8")
            return str(path)
        if output_format == "docx":
            return self._to_docx(text)
        if output_format == "pdf":
            return self._to_pdf(text)
        return None

    def _to_docx(self, text: str) -> str:
        path = self.output_dir / f"optimized_resume_{uuid4().hex[:8]}.docx"
        document = Document()
        for block in text.split("\n\n"):
            document.add_paragraph(block)
        document.save(path)
        return str(path)

    def _to_pdf(self, text: str) -> str:
        path = self.output_dir / f"optimized_resume_{uuid4().hex[:8]}.pdf"
        pdf = canvas.Canvas(str(path), pagesize=letter)
        width, height = letter
        y = height - 50
        for line in text.splitlines():
            if y < 60:
                pdf.showPage()
                y = height - 50
            pdf.drawString(40, y, line[:110])
            y -= 16
        pdf.save()
        return str(path)
