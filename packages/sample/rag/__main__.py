from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
import logging
import os
import pinecone
from typing import Union
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')

load_dotenv()

def get_completion(prompt: str, model="gpt-3.5-turbo-0613") -> dict:
    openai.api_key  = os.getenv("OPENAI_API_KEY", "")

    messages = [{"role": "user", "content": prompt}]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )

    return {"response":response.choices[0].message.content, "qtt_tokens":response.usage.total_tokens} #qtt_tokens can be used to determine the price of the answer validation to determine if it is worth it.

def get_index_data(OPENAI_API_KEY: str) -> Union['Pinecone', dict]:

    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'YourAPIKey')
    PINECONE_API_ENV = os.getenv('PINECONE_API_ENV', 'us-east1-gcp')

    try:
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_API_ENV
        )

        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

        index_name = "rag-app"
        documents = Pinecone.from_existing_index(index_name, embeddings)
        logging.info("Documents retrieved successfully.")
        return documents
    
    except Exception as err:
        logging.error(f"Unable to connect with Pinecone. Error: {err}")
        return dict()

def main(args: dict) -> dict:
    '''
    Takes an user message, 
    returns a json with the answer to the user message.

        Parameters:
            args: user prompt

        Returns:
            json body: Json response with the answer.
    '''
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_API_ENV = os.getenv("PINECONE_API_ENV", "us-east1-gcp")

    try:
        query = args.get("userprompt")

        documents = get_index_data(OPENAI_API_KEY)
        
        llm = ChatOpenAI(temperature=0.2, openai_api_key=OPENAI_API_KEY)
        chain = load_qa_chain(llm, chain_type="stuff")

        docs = documents.similarity_search(query)

        pdf_content = '\n'.join(doc.page_content for doc in docs)

        response_query = chain.run(input_documents=docs, question=query)
        
        prompt_validation = f"""Content: {pdf_content}
                                Original answer: {response_query}
                                Query: 
                                Check if Original answer is a good response to user Query and if it is based on some parts of the Content.
                                If it is True, answer with 1 and if it is not answer with 0.
                                Answer only with 1 or 0.
                                """

        validation = get_completion(prompt_validation)
        logging.info("Response generated successfully.")

        if int(validation["response"]) == 1:
            return {"response":response_query, "body":"success", "tokens_usage": validation["qtt_tokens"]}
        return {"response":{"Sorry, I don't know about this topic, feel free to ask about something else."},
                "body":"success", 
                "tokens_usage": validation["qtt_tokens"]}

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
    return {"response":"Try again later please.", "body":"failed"}
