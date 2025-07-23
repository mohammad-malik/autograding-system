from fpdf import FPDF
import sys

def text_to_pdf(text_file, pdf_file):
    """
    Convert a text file to PDF
    
    Args:
        text_file: Path to the text file
        pdf_file: Path to the output PDF file
    """
    try:
        # Read the text file
        with open(text_file, 'r') as file:
            content = file.read()
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Split text into lines and add to PDF
        for line in content.split('\n'):
            pdf.cell(0, 10, txt=line, ln=True)
        
        # Save PDF
        pdf.output(pdf_file)
        print(f"PDF created successfully: {pdf_file}")
        return True
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_pdf.py <input_text_file> <output_pdf_file>")
        sys.exit(1)
    
    text_file = sys.argv[1]
    pdf_file = sys.argv[2]
    
    text_to_pdf(text_file, pdf_file) 