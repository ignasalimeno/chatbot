from pymongo import MongoClient

def find_document_by_criteria(criteria):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['entelai']  
    collection = db['entelai']  

    criteria = {"med_id": criteria}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None


def find_document_by_criteria_rdcom(criteria):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['rdcom']  
    collection = db['questions']  

    criteria = {"question_id": criteria}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None

def find_response_by_user(token):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['rdcom']  
    collection = db['responses']  

    criteria = {"user_id": token}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None 


def check_if_token_exist(token):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['rdcom']  
    collection = db['responses']  

    criteria = {"user_id": token}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None
