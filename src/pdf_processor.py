import os
from PyPDF2 import PdfReader
import requests
import openai
import pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI and Pinecone API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Ensure the API keys are set
if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise ValueError("API keys for OpenAI and Pinecone must be set in the environment variables.")

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY)

# Check if Pinecone index exists; if not, create one
index_name = "pdf_embeddings"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=512)  # Adjust dimension based on your model's output
index = pinecone.Index(index_name)

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def extract_text(self):
        """Extract text from a PDF file."""
        text_content = []
        with PdfReader(self.file_path) as reader:
            for page in reader.pages:
                text_content.append(page.extract_text())
        return " ".join(text_content)

def embed_text_with_openai(text):
    """Embed text using OpenAI's API."""
    openai.api_key = OPENAI_API_KEY
    response = openai.Embedding.create(input=[text], engine="text-similarity-babbage-001")
    embedding = response['data'][0]['embedding']
    return embedding

def store_embedding_in_pinecone(embedding, doc_id):
    """Store the embedding vector in Pinecone."""
    index.upsert(vectors={doc_id: embedding})
    print(f"Stored embedding for document {doc_id} in Pinecone.")

if __name__ == "__main__":
    pdf_path = "path_to_your_pdf.pdf"  # Update this to the path of your PDF file
    processor = PDFProcessor(pdf_path)
    text = processor.extract_text()
    embedding = embed_text_with_openai(text)
    document_id = os.path.basename(pdf_path)  # Using the file name as the document ID
    store_embedding_in_pinecone(embedding, document_id)

