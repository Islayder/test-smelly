"""Converte o Markdown do relatório para PDF sem serviço externo.

Requer Python 3 e reportlab (python -m pip install reportlab).
Uso, na raiz do projeto: python docs/gerar_relatorio.py
"""

from html import escape
from pathlib import Path
import os
import re

from PIL import Image as RasterImage, ImageDraw, ImageFont

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, XPreformatted,
)


ROOT = Path(__file__).resolve().parent
FONT_DIR = Path(os.environ['WINDIR']) / 'Fonts'
FONT_FILES = {
    'Arial': 'arial.ttf', 'Arial-Bold': 'arialbd.ttf',
    'Arial-Italic': 'ariali.ttf', 'Consolas': 'consola.ttf',
}
for name, filename in FONT_FILES.items():
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily(
    'Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic',
    boldItalic='Arial-Bold',
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='BodyReport', fontName='Arial', fontSize=10.2, leading=13.2,
    alignment=TA_JUSTIFY, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name='SectionReport', fontName='Arial-Bold', fontSize=14, leading=18,
    textColor=colors.HexColor('#18324b'), spaceBefore=7, spaceAfter=10,
    keepWithNext=True,
))
styles.add(ParagraphStyle(
    name='CodeReport', fontName='Consolas', fontSize=8.6, leading=10.7,
    backColor=colors.HexColor('#f2f4f6'), borderPadding=7,
    spaceBefore=4, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name='CellReport', fontName='Arial', fontSize=9, leading=11.5,
))
styles.add(ParagraphStyle(
    name='CoverReport', fontName='Arial', fontSize=13, leading=22,
    alignment=TA_CENTER, spaceAfter=17,
))
styles.add(ParagraphStyle(
    name='CoverTitleReport', fontName='Arial-Bold', fontSize=23, leading=30,
    alignment=TA_CENTER, textColor=colors.HexColor('#18324b'), spaceAfter=30,
))
styles.add(ParagraphStyle(
    name='CaptionReport', fontName='Arial-Italic', fontSize=8.5, leading=11,
    spaceBefore=4, spaceAfter=8,
))


def render_lint_evidence():
    """Representa o log real como imagem; não simula uma captura histórica."""
    log = (ROOT / 'eslint-inicial.txt').read_text(encoding='utf-8').strip()
    command = '$ npx eslint test/userService.smelly.test.js'
    lines = [command, '', *log.splitlines()]
    font = ImageFont.truetype(str(FONT_DIR / 'consola.ttf'), 24)
    symbol_font = ImageFont.truetype(str(FONT_DIR / 'seguisym.ttf'), 24)
    line_height = 34
    padding = 30
    width = int(max(font.getlength(line) for line in lines)) + 2 * padding
    height = len(lines) * line_height + 2 * padding
    canvas = RasterImage.new('RGB', (width, height), '#101820')
    draw = ImageDraw.Draw(canvas)
    for index, line in enumerate(lines):
        y = padding + index * line_height
        if line.startswith('✖'):
            draw.text((padding, y), line[0], font=symbol_font, fill='#e8edf2')
            draw.text((padding + font.getlength(line[0]), y), line[1:],
                      font=font, fill='#e8edf2')
        else:
            draw.text((padding, y), line, font=font, fill='#e8edf2')
    canvas.save(ROOT / 'eslint-inicial.png')


def inline(text):
    text = escape(text)
    text = re.sub(r'`([^`]+)`', r'<font name="Consolas">\1</font>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(
        r'\[([^\]]+)\]\((https?://[^)]+)\)',
        r'<link href="\2" color="#234e75">\1</link>', text,
    )
    return text


def footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor('#c5ced6'))
        canvas.line(44, 35, A4[0] - 44, 35)
        canvas.setFont('Arial', 8)
        canvas.setFillColor(colors.HexColor('#536371'))
        canvas.drawString(44, 23, 'PUC Minas | Teste de Software | Test Smells')
        canvas.drawRightString(A4[0] - 44, 23, str(doc.page - 1))
    canvas.restoreState()


def build():
    render_lint_evidence()
    source = (ROOT / 'Relatorio_Test_Smells.md').read_text(encoding='utf-8')
    lines = source.splitlines()
    story = [Spacer(1, 92)]
    cover = True
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line == '<!-- pagebreak -->':
            story.append(PageBreak())
            cover = False
            i += 1
            continue
        if line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            story.append(XPreformatted(escape('\n'.join(code)), styles['CodeReport']))
            i += 1
            continue
        image_match = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        if image_match:
            image_path = ROOT / image_match.group(2)
            with RasterImage.open(image_path) as asset:
                width, height = asset.size
            display_width = A4[0] - 88
            story.append(Image(str(image_path), width=display_width,
                               height=display_width * height / width))
            story.append(Paragraph(inline(image_match.group(1)), styles['CaptionReport']))
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                row = [cell.strip() for cell in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+', cell) for cell in row):
                    rows.append([
                        Paragraph(inline(cell), styles['CellReport']) for cell in row
                    ])
                i += 1
            table = Table(rows, colWidths=[155, A4[0] - 88 - 155], repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e7edf3')),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#bdc9d3')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 7),
                ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.extend([table, Spacer(1, 10)])
            continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]), styles['CoverTitleReport']))
            i += 1
            continue
        if line.startswith('## '):
            story.append(Paragraph(inline(line[3:]), styles['SectionReport']))
            i += 1
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip():
            if lines[i].startswith(('```', '#', '|', '<!--')):
                break
            paragraph.append(lines[i])
            i += 1
        story.append(Paragraph(
            inline(' '.join(paragraph)),
            styles['CoverReport' if cover else 'BodyReport'],
        ))

    doc = SimpleDocTemplate(
        str(ROOT / 'Relatorio_Test_Smells.pdf'), pagesize=A4,
        leftMargin=44, rightMargin=44, topMargin=39, bottomMargin=45,
        title='Refatoração de Testes e Detecção de Test Smells',
        author='Islayder Jackson Ribeiro de Oliveira',
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print('PDF gerado:', ROOT / 'Relatorio_Test_Smells.pdf')


if __name__ == '__main__':
    build()
