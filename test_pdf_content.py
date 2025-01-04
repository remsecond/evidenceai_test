import PyPDF2
from pathlib import Path

def main():
    # Read the PDF
    pdf_path = Path("input/OFW_Messages_Report_Dec.pdf")
    
    with open(pdf_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)
        
        # Print basic info
        print(f"Total pages: {len(pdf.pages)}\n")
        
        # Print first page content
        print("First page content:")
        print("-" * 80)
        print(pdf.pages[0].extract_text())
        print("-" * 80)
        
        # Print second page content sample
        if len(pdf.pages) > 1:
            print("\nSecond page sample:")
            print("-" * 80)
            print(pdf.pages[1].extract_text()[:500])
            print("-" * 80)

if __name__ == "__main__":
    main()