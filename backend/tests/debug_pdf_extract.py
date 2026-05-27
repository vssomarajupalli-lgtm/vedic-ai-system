import sys
import os

# Ensure the 'app' package can be resolved when running the script directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.parsers.pdf_text_extractor import PdfTextExtractor

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_pdf_extract.py <path_to_pdf>")
        print("Example: python debug_pdf_extract.py ../sample_reports/sample.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"Error: File not found at '{pdf_path}'")
        sys.exit(1)

    print(f"--- Loading PDF: {pdf_path} ---")
    extractor = PdfTextExtractor()
    extracted_pages = extractor.extract_text(pdf_path)

    print(f"--- Extraction Complete. Found {len(extracted_pages)} valid pages. ---")
    
    for page_num, text in extracted_pages.items():
        print(f"\n{'='*20} PAGE {page_num} {'='*20}")
        for i, row in enumerate(text.splitlines()):
            print(f"[{i:03d}] {repr(row)}")

if __name__ == "__main__":
    main()