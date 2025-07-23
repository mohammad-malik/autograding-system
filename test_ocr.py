import os
import sys
from pathlib import Path
import json
from mistralai import Mistral, DocumentURLChunk
from dotenv import load_dotenv
load_dotenv()

# Get API key from environment
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    print("Error: MISTRAL_API_KEY not found in environment variables.")
    print("Please set the MISTRAL_API_KEY environment variable.")
    sys.exit(1)

# Initialize Mistral client
client = Mistral(api_key=api_key)

def process_pdf(file_path):
    """
    Process PDF document using MistralAI's OCR service
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        Dictionary containing OCR results
    """
    # Verify PDF file exists
    pdf_file = Path(file_path)
    if not pdf_file.is_file():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
        
    try:
        print(f"Processing PDF: {file_path}")
        
        # Upload PDF file to Mistral's OCR service
        uploaded_file = client.files.upload(
            file={
                "file_name": pdf_file.stem,
                "content": pdf_file.read_bytes(),
            },
            purpose="ocr",
        )
        
        print(f"File uploaded with ID: {uploaded_file.id}")
        
        # Get URL for the uploaded file
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        
        # Process PDF with OCR
        pdf_response = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest",
        )
        
        # Extract text from all pages
        extracted_text = ""
        for page in pdf_response.pages:
            extracted_text += page.text + "\n\n"
        
        # Convert response to dictionary
        response_dict = json.loads(pdf_response.model_dump_json())
        
        return extracted_text, response_dict
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None, None

if __name__ == "__main__":
    # Check if a file path was provided
    if len(sys.argv) < 2:
        print("Usage: python test_ocr.py <path_to_pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    extracted_text, response_dict = process_pdf(pdf_path)
    
    if extracted_text:
        print("\n--- Extracted Text (First 500 chars) ---")
        print(extracted_text[:500] + "...")
        
        # Print some metadata
        print("\n--- Document Metadata ---")
        print(f"Number of pages: {len(response_dict['pages'])}")
        
        # Save the extracted text to a file
        output_file = pdf_path + ".txt"
        with open(output_file, "w") as f:
            f.write(extracted_text)
        print(f"\nExtracted text saved to: {output_file}")
    else:
        print("Failed to process PDF.") 