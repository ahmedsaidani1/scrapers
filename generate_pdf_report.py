"""
Generate PDF Technical Report from Markdown
"""
import markdown
import pdfkit
from datetime import datetime

print("Reading TECHNICAL_REPORT.md...")
with open('TECHNICAL_REPORT.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

print("Converting Markdown to HTML...")
html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Add CSS styling
html_with_style = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .success {{
            color: #27ae60;
            font-weight: bold;
        }}
        .warning {{
            color: #f39c12;
            font-weight: bold;
        }}
        .error {{
            color: #e74c3c;
            font-weight: bold;
        }}
    </style>
</head>
<body>
{html_content}
<hr>
<p style="text-align: center; color: #7f8c8d; font-size: 12px;">
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</p>
</body>
</html>
"""

print("Generating PDF...")
try:
    # Configure pdfkit options
    options = {
        'page-size': 'A4',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': 'UTF-8',
        'enable-local-file-access': None
    }
    
    pdfkit.from_string(html_with_style, 'TECHNICAL_REPORT.pdf', options=options)
    print("\n✓ PDF generated successfully: TECHNICAL_REPORT.pdf")
    
except Exception as e:
    print(f"\n✗ Error generating PDF: {e}")
    print("\nNote: pdfkit requires wkhtmltopdf to be installed.")
    print("Download from: https://wkhtmltopdf.org/downloads.html")
    print("\nAlternatively, saving as HTML...")
    
    with open('TECHNICAL_REPORT.html', 'w', encoding='utf-8') as f:
        f.write(html_with_style)
    print("✓ HTML version saved: TECHNICAL_REPORT.html")
    print("You can open this in a browser and print to PDF")
