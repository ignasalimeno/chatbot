import db_helper
import os
import json, random
from flask import session
from pymongo import MongoClient
import datetime
import secrets

# --- Set variables
MONGO_DB_PATH= os.environ.get('MONGO_DB_PATH')
MONGO_DB_NAME=os.environ.get('MONGO_DB_NAME')
MONGO_DB_COLLECTION_RES=os.environ.get('MONGO_DB_COLLECTION_RES')
MONGO_DB_COLLECTION_QUE=os.environ.get('MONGO_DB_COLLECTION_QUE')
FIRST_QUESTION = os.environ.get('FIRST_QUESTION')


def get_complete_question(id, language):
    response = db_helper.find_document_by_criteria_rdcom(id)
    
    text = ""

    #tomo la pregunta 1 que inicia todo
    if response:

        #Agrego el texto de la pregunta que traje de la BD
        for txt in response["text"]:
            if txt["language"] == language:
                text = text + txt["text"]

        #Agrego las opciones de la pregunta
        for options in response["options"]:
            for txt in options["text"]:
                if txt["language"] == language:
                    text = text + "<br>" + txt["text"]

        return text
    else: 
        return None

def save_new_response(user_id, selected_value, next_question):
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
    collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name
    
    #traigo respuesta anterior y armo el udpdate
    response_saved = db_helper.find_response_by_user(user_id)
    
    index = 0
    if response_saved:
        responses = response_saved["responses"]
        index = len(responses)-1
        field_to_update = "option_selected"
    
    print("index: " + str(index))
    # Update the responses element for a specific document
    query = {"user_id": user_id}
    update = {"$set": {f"responses.{index}.{"option_selected"}": selected_value}}
    result = collection.update_one(query, update)

    # Update the responses element
    print("Number of documents updated:", result.modified_count)

    new_response = {"question_id": next_question, "option_selected": ""}
    query = {"user_id": user_id}
    update = {"$push": {"responses": new_response}}
    result = collection.update_one(query, update)
    print("Number of documents added:", result.modified_count)
    
    
    return result.modified_count

def first_question(token, language):
    # --- Insertar un elemento vacío
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
    collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

    first_layer = {
      "layer_id": "1",
      "last_layer_id": "",
      "last_option_id": "",
      "question_id": "pregunta1",
      "checked": "False",
      "option_selected": []
    }

    mydict = { "user_id": token, "date": datetime.datetime.now(), "layers": [first_layer], "sypmtoms": [] }

    x = collection.insert_one(mydict)        
    if x:
        response = get_complete_question(FIRST_QUESTION, language)
    
    if response:
        return response
    else: 
        return None
    
def get_options_for_text(text):
    try:
        validate_options = []
        selected_options = text.split(",")
        
        for x in selected_options:
            validate_options.append(x.strip())

        return validate_options
    except:
        return None
    
def validate_options(user_options, question_id, language):
    try:
        response = db_helper.find_document_by_criteria_rdcom(question_id)
        allCorrectOptions = True
        print(response["options"])
        print(user_options)
        
        for opt in user_options:
            optionExist = False
           
            for option in response["options"]:
                for txt in option["text"]:
                    if txt["language"] == language:
                        if txt["values"] == opt:
                            optionExist = True
                            print(optionExist)
                
            if optionExist == False:
                allCorrectOptions = False

        return allCorrectOptions
    except:
        return None
    
def middle_question(text, token, language):
    try:
        #separo las opciones recibidas
        selected_options = get_options_for_text(text)

        #TODO: validar que las opciones elegidas estén dentro de las opciones posibles

        #obtengo el elemento completo del usuario y me traigo la ultima layer
        response_saved = db_helper.find_response_by_user(token)
        layers = response_saved["layers"]
        last_layer = layers[len(layers)-1]

        if validate_options(selected_options, last_layer["question_id"],language) == False:
            raise Exception()

        print("last layer")
        print(last_layer)

        # guardo las opciones que ingreso el usuario 
        client = MongoClient(MONGO_DB_PATH)
        db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
        collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

        layer_id = 1
        json_to_save = []
        
        #traer 
        question = db_helper.find_document_by_criteria_rdcom(last_layer["question_id"])
        print(question)
        finalQuestion = question["end_question"] 
        print(finalQuestion)

        # --- Lógica para guardar en la última capa la opción elegida
        for option in selected_options:
            next_question_id = ""
            for opt in question["options"]:
                for txt in opt["text"]:
                    if txt["language"] == language:
                        if txt["values"] == option:
                            next_question_id = opt["action"]
                            
                
            txt = {"option_id": option, "next_question": next_question_id, "next_layer": last_layer["layer_id"] + "." + str(layer_id), "checked": finalQuestion} 
            json_to_save.append(txt)
            layer_id += 1

        print("txt to save")
        print(json_to_save)

        query = {"user_id": token}
        update = {"$set": {f"layers.{len(layers)-1}.{"option_selected"}": json_to_save}}
        result = collection.update_one(query, update)
        # --------------------------------

        # --- Guardo próxima layer y traigo proxima question
        nextQuestion = save_next_layer(token, last_layer["layer_id"])

        #si no hay, significa que termine
        if nextQuestion:
            return get_complete_question(nextQuestion,language)
        else:
            return last_question()
        # -----------------------------------------------
    except:
        return "Hubo un error, por favor responda nuevamente"

def save_next_layer(token, layer_id):
    print("token: " + token)
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
    collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

    json_to_save = {}
    last_layer = ""
    last_option_id = ""
    question_id = ""
    
    existPendingOptions = False
    #existNextQuestion = False

    response_saved = db_helper.find_response_by_user(token)

    for layer in reversed(response_saved["layers"]):
        if layer["layer_id"] == layer_id:
            for opt in layer["option_selected"]:
                if opt["checked"] == "False":
                    #existNextQuestion = True
                    existPendingOptions = True
                    layer_id = opt["next_layer"]
                    last_layer = layer["layer_id"]
                    last_option_id = opt["option_id"]
                    question_id = opt["next_question"]

                    json_to_save = {"layer_id": layer_id,
                    "last_layer_id": last_layer,
                    "last_option_id": last_option_id,
                    "question_id": question_id,
                    "checked": "False",
                    "option_selected": []}

                    query = {"user_id": token}
                    update = {"$push": {"layers": json_to_save}}
                    result = collection.update_one(query, update)

                    break

            if existPendingOptions == False:
                #TODO: actualizar dónde stoy parado
                 
                query = { "user_id": token, "layers.layer_id": layer_id }
                update = {"$set": {"layers.$.checked": "True"}}
                result = collection.update_one(query, update)
                
                #TODO: actualizar en layer anterior la opción que estoy parado
                last_layer_id = layer["last_layer_id"]
                last_question_id = layer["question_id"]
                query = { "user_id": token, "layers.layer_id": last_layer_id, "layers.option_selected.next_question": last_question_id}
                
                update = {"$set": {"layers.$.option_selected.$[elem].checked": "True"}}
                array_filters = [{"elem.next_question": last_question_id}]
                #print(query)
                #print(update)
                result = collection.update_one(query, update, array_filters=array_filters)
                
                question_id = save_next_layer(token, last_layer_id)

                break

    #if existNextQuestion:
    return question_id

def last_question():
    #TODO: Aplicar lógica real

    # initializing list
    test_list = ["Cambio de neumáticos", "Rectificación motor", "Reparación total", "Llevar al tapicero", "Cambiar batería"]
    
    random_1 = random.randrange(len(test_list))
    random_2 = random.randrange(len(test_list))

    text= "Según los problemas mencionados, es probable que usted tenga: " +  test_list[random_1] + ", o sino: " +  test_list[random_2]
    return text

def handler(texto, token, language):
    if token is None:
        token = secrets.token_hex(20)

    if db_helper.check_if_token_exist(token):
        if check_token(token):
            return middle_question(texto, token, language), None
        else:
            token = secrets.token_hex(20)
            return first_question(token, language), token
    else:
        
        return first_question(token, language), token

def check_token(token):
    response_saved = db_helper.find_response_by_user(token)
    saved_time = response_saved["date"]
    seconds = (datetime.datetime.now() - saved_time).total_seconds()

    if seconds <= 5000:
      
        client = MongoClient(MONGO_DB_PATH)
        db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
        collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

        query = {"user_id": token}
        update = {"$set": {f"date": datetime.datetime.now()}}

        result = collection.update_one(query, update)

        return True
    else: 
        return None