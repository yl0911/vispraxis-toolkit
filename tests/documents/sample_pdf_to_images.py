"""Render the historical local PDF sample to PNG pages."""
from pathlib import Path
from scripts.documents.render_pdf_pages import run
PDF_FILE=Path("./pdf.pdf");OUTPUT_DIR=Path("./test/pdf_img");ZOOM=1.33333333
def main()->int:
    try:r=run(PDF_FILE,OUTPUT_DIR,zoom=ZOOM)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(f"pages={r.pages} output={OUTPUT_DIR}");return 0
if __name__=="__main__":raise SystemExit(main())
