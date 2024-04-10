import db_helper
import json, random
from flask import session
from pymongo import MongoClient

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
                    text = text + "\n" + txt["text"]

        return text
    else: 
        return None

def save_new_response(user_id, selected_value, next_question):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['rdcom']  # Replace 'your_database' with your database name
    collection = db['responses']  # Replace 'your_collection' with your collection name
    
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
    client = MongoClient('mongodb://localhost:27017/')
    db = client['rdcom']  # Replace 'your_database' with your database name
    collection = db['responses']  # Replace 'your_collection' with your collection name

    first_layer = {
      "layer_id": "1",
      "last_layer_id": "",
      "last_option_id": "",
      "question_id": "pregunta1",
      "checked": "False",
      "option_selected": []
    }

    mydict = { "user_id": token, "date": "", "layers": [first_layer], "sypmtoms": [] }

    x = collection.insert_one(mydict)        
    if x:
        response = get_complete_question("pregunta1", language)
    
    if response:
        return response
    else: 
        return None

# def middle_question_old_old(text, token, language):
#     #tengo opcion elegida por parametro

#     #busco pregunta anterior que guarde anteriormente
#     response_saved = db_helper.find_response_by_user(token)

#     question_id = ""
    
#     if response_saved:
#         responses = response_saved["responses"]

#         last_response = responses[len(responses)-1]
#         if last_response:
#             question_id = last_response["question_id"]

#     print("Ultima pregunta id: " + question_id)

#     #traigo las opciones de la pregunta
#     next_question = ""

#     if question_id != "":
#         response = db_helper.find_document_by_criteria_rdcom(question_id)
#         print("aca la rta")
#         print(response)

#         #comparo entre las opciones y guardo la opcion elegida
#         if response:
#             for options in response["options"]:
#                 for txt in options["text"]:
#                     if txt["language"] == language:
#                         if txt["values"] == text:
#                             next_question = options["action"]

#     print(next_question)

#     #Verifico si hay opción, guardo respuesta y retorno la nueva pregunta
#     if next_question != "":
#         save_new_response(token, text,next_question)
#         return get_complete_question(next_question, language)
#     else:
#         return None
    
# def middle_question_old(text, token, language):
#     #tengo opcion elegida por parametro

#     #busco pregunta anterior que guarde anteriormente
#     response_saved = db_helper.find_response_by_user(token)

#     question_id = ""
    
#     if response_saved:
#         layer_route = response_saved["layer_route"]

#         for layer in layer_route:
            

#         last_layer = layer_route[len(responses)-1]
#         if last_layer:
#             for layer in response[]
#             question_id = last_response["question_id"]

#     print("Ultima pregunta id: " + question_id)

#     #traigo las opciones de la pregunta
#     next_question = ""

#     if question_id != "":
#         response = db_helper.find_document_by_criteria_rdcom(question_id)
#         print("aca la rta")
#         print(response)

#         if response:
#             #Consulto si es final
#             if response["end_question"] == "No":

#                 #armo dos array para traer las opciones que me indico el usuario y las que voy validando
#                 options_selected = text.split(", ")
#                 options_validated = [] 

#                 #valido las opciones
#                 for options in response["options"]:
#                     for txt in options["text"]:
#                         for selected in options_selected:
#                             if txt["language"] == language:
#                                 if txt["values"] == selected:
#                                     options_validated.append(selected)
                
#                 #valido que toda las opciones hayan sido correctas
#                 if len(options_validated) == len(options_selected):
                    
#                     # TODO: GUARDAR OPCIONES EN LAYER



#     print(next_question)
    
#     #Verifico si hay opción, guardo respuesta y retorno la nueva pregunta
#     if next_question != "":
#         save_new_response(token, text,next_question)
#         return get_complete_question(next_question, language)
#     else:
#         return None
   
def middle_question(text, token, language):
    #separo las opciones recibidas
    selected_options = text.split(", ")
    print("opciones:")
    print(selected_options)
    #TODO: validar que las opciones elegidas estén dentro de las opciones posibles

    #obtengo el elemento completo del usuario y me traigo la ultima layer
    response_saved = db_helper.find_response_by_user(token)
    layers = response_saved["layers"]
    last_layer = layers[len(layers)-1]

    print("last layer")
    print(last_layer)

    # guardo las opciones que ingreso el usuario 
    client = MongoClient('mongodb://localhost:27017/')
    db = client['rdcom']  # Replace 'your_database' with your database name
    collection = db['responses']  # Replace 'your_collection' with your collection name

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

def save_next_layer(token, layer_id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['rdcom']  # Replace 'your_database' with your database name
    collection = db['responses']  # Replace 'your_collection' with your collection name

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
                query = { "layers.layer_id": layer_id }
                update = {"$set": {"layers.$.checked": "True"}}
                result = collection.update_one(query, update)
                
                #TODO: actualizar en layer anterior la opción que estoy parado
                last_layer_id = layer["last_layer_id"]
                last_question_id = layer["question_id"]
                query = {"layers.layer_id": last_layer_id, "layers.option_selected.next_question": last_question_id}
                
                update = {"$set": {"layers.$.option_selected.$[elem].checked": "True"}}
                array_filters = [{"elem.next_question": last_question_id}]
                print(query)
                print(update)
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
    
    if db_helper.check_if_token_exist(token):
        print("token existe")
        return middle_question(texto, token, language)
        
    else:

        print("token existe")
        return first_question(token, language)
        # print("token no existe")
        # return first_question(texto, language)

    return None