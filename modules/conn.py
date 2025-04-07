import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from sqlalchemy import create_engine
import logging

load_dotenv()
logging.basicConfig(level=logging.WARNING, filename='Run.log', format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

#------------------------------------------- AZURE OPENAI connectivity
endpoint = os.getenv('AZURE_ENDPOINT')
api_key = os.getenv('AZURE_API_KEY')
deployment = os.getenv('DEPLOYMENT')
api_version= os.getenv('APIVERSION')

def createOpenAIClient():
    try:
        client = AzureOpenAI(
            azure_endpoint = endpoint,
            api_key = api_key,
            api_version = api_version
        )
        return client
    except Exception as e:
        logger.error(f"e0c10: {e}")
        return None

#------------------------------------------- HANA database connectivity
host= os.getenv("HANA_HOST")
port= os.getenv("HANA_PORT")
user= os.getenv("HANA_USER")
password= os.getenv("HANA_PASS")
schema= os.getenv("SCHEMA")

def connectHANAdb():
    try:
        url = f"hana+hdbcli://{user}:{password}@{host}:{port}"
        engine = create_engine(url)
        print(f"Connected HANADB@{host}")
        return engine
    except Exception as e:
        logger.error(f"e0c20: {e}")
        return None