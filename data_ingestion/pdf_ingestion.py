from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from dotenv import load_dotenv
import os
import logging
import openai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def pdf_ingestion(file_name: str):
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YourAPIKey')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'YourAPIKey')
    PINECONE_API_ENV = os.getenv('PINECONE_API_ENV', 'us-east1-gcp')

    try:
        loader = PyPDFLoader(file_path=f"./data/{file_name}.pdf")
        data = loader.load()
        logging.info("Documento loaded.")
    except Exception as err:
        logging.error(f"Try again to load the document. Error: {err}")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(data)
    logging.info("Text splitted.")

    try:
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_API_ENV
        )
        index_name = "rag-app"

        Pinecone.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)
        logging.info("Data ingested successfully.")

    except openai.AuthenticationError as err:
        logging.error(f"OpenAI API request was not authorized: {err}")
        logging.info("Verify OpenAI key.")
    
    except openai.APITimeoutError as err:
        logging.error(f"OpenAI API request timed out: {err}")
        logging.info("Verify internet conection.")

    except openai.RateLimitError as err:
        logging.error(f"OpenAI API request exceeded rate limit: {err}")
        logging.info("Verify limite rates.")

    except Exception as err:
        logging.error(f"Error: {err}")
    

#chose here the name of pdf file to be ingested.
pdf_ingestion("niagara_falls")
