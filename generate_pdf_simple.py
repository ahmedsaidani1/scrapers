"""
Generate PDF Technical Report using ReportLab
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

print("Reading TECHNICAL_REPORT.md...")
with open('TECHNICAL_REPORT.md', 'r', encoding='utf-8') as f:
    content = f.read()

print("Creating PDF...")

# Create PDF
pdf_file = "TECHNICAL_REPORT.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4,
                       rightMargin=72, leftMargin=72,
                       topMargin=72, bottomMargin=18)

# Container for the 'Flowable' objects
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#2c3e50'),
    spaceAfter=30,
    alignment=TA_CENTER
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=colors.HexColor('#34495e'),
    spaceAfter=12,
    spaceBefore=12
)

normal_style = styles['Normal']

# Parse markdown and convert to PDF elements
lines = content.split('\n')
i = 0

while i < len(lines):
    line = lines[i].strip()
    
    if line.startswith('# '):
        # Main title
        text = line[2:].strip()
        elements.append(Paragraph(text, title_style))
        elements.append(Spacer(1, 0.2*inch))
    
    elif line.startswith('## '):
        # Section heading
        text = line[3:].strip()
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(text, heading_style))
        elements.append(Spacer(1, 0.1*inch))
    
    elif line.startswith('### '):
        # Subsection
        text = line[4:].strip()
        elements.append(Paragraph(f"<b>{text}</b>", normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    elif line.startswith('- ') or line.startswith('* '):
        # Bullet point
        text = line[2:].strip()
        # Replace markdown bold
        text = text.replace('**', '<b>').replace('**', '</b>')
        elements.append(Paragraph(f"• {text}", normal_style))
    
    elif line.startswith('```'):
        # Code block
        code_lines = []
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('```'):
            code_lines.append(lines[i])
            i += 1
        code_text = '<br/>'.join(code_lines)
        code_style = ParagraphStyle('Code', parent=normal_style, 
                                    fontName='Courier', 
                                    fontSize=9,
                                    leftIndent=20,
                                    backColor=colors.HexColor('#f4f4f4'))
        elements.append(Paragraph(code_text, code_style))
        elements.append(Spacer(1, 0.1*inch))
    
    elif line and not line.startswith('#'):
        # Regular paragraph
        text = line
        # Replace markdown bold
        text = text.replace('**', '<b>').replace('**', '</b>')
        # Replace markdown italic
        text = text.replace('*', '<i>').replace('*', '</i>')
        elements.append(Paragraph(text, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    elif line == '---':
        # Horizontal rule
        elements.append(Spacer(1, 0.2*inch))
    
    i += 1

# Add footer
elements.append(Spacer(1, 0.5*inch))
footer_style = ParagraphStyle('Footer', parent=normal_style, 
                              fontSize=10, 
                              textColor=colors.grey,
                              alignment=TA_CENTER)
elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

# Build PDF
doc.build(elements)

print(f"\n✓ PDF generated successfully: {pdf_file}")
