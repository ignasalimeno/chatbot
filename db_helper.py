from pymongo import MongoClient
import os

# --- Set variables
MONGO_DB_PATH= os.environ.get('MONGO_DB_PATH')
MONGO_DB_NAME=os.environ.get('MONGO_DB_NAME')
MONGO_DB_COLLECTION_RES=os.environ.get('MONGO_DB_COLLECTION_RES')
MONGO_DB_COLLECTION_QUE=os.environ.get('MONGO_DB_COLLECTION_QUE')

def find_document_by_criteria_rdcom(criteria):
    # Connect to MongoDB
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  
    collection = db[MONGO_DB_COLLECTION_QUE]  

    criteria = {"question_id": criteria}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None

def find_response_by_user(token):
    # Connect to MongoDB
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  
    collection = db[MONGO_DB_COLLECTION_RES]  

    criteria = {"user_id": token}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None 


def check_if_token_exist(token):
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  
    collection = db[MONGO_DB_COLLECTION_RES]  

    criteria = {"user_id": token}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None
