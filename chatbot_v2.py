import db_helper, postgre_helper
import os
import json, random
from flask import session
from pymongo import MongoClient
import datetime
import secrets

# --- Set variables
# MONGO_DB_PATH= os.environ.get('MONGO_DB_PATH')
# MONGO_DB_NAME=os.environ.get('MONGO_DB_NAME')
#MONGO_DB_PATH = 'mongodb+srv://ignacio:3DCWrdMyumZEvfNm@rdcom-bot-questions.2wk6eiw.mongodb.net/'
#MONGO_DB_NAME = 'rdcom-bot'
MONGO_DB_PATH='mongodb://localhost:27017/'
MONGO_DB_NAME='rdcom'
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

def list2query(list):
    try:
        query = ""
        for i in range(len(list)-1):
            query += ("'" + list[i][0] + "',")
        query += "'" + list[len(list)-1][0] + "'"
        return query
    except:
        print("error")

def get_categories():
    list_cats = []
    rows = postgre_helper.readDB("select cat_id, name from public.categories where type = 'system'")
    return rows

def get_subcategories(list_cat):
    cats = ""
    for cat in list_cat:
        cats += "'" + cat + "',"
    cats = cats[:len(cats)-1]
    
    print("cats", cats)

    query = "select cat_id, name from public.categories where cat_id in " + \
                "(select cat_id_2 from public.categories_categories where cat_id_1 in (" + cats + "))"
    
    rows = postgre_helper.readDB(query)

    if len(rows) > 0:
        return rows
    
    return None

def get_sympthoms(list_pat, list_subcat):
    query_1 = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_subcat[0] + \
                            "' and pat_id in (" + list2query(list_pat) + ")"
    
    query_2 = "select distinct sym_id from public.pathologies_symptoms where pat_id in (" + query_1
    query_2 += ") and sym_id in (select distinct sym_id from public.categories_symptoms where cat_id in ('" + list_subcat[0] + "'))"

    query_2_2 = "select sym_id, name from public.symptoms where sym_id in (" + query_2 + ")"
    list_symp = postgre_helper.readDB(query_2_2)

    print("query sym",query_2_2)
    if len(list_symp):
        return list_symp
    
    return None

def get_pat_from_subcategories(list_pat, list_subcat):
    query_1 = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_subcat[0] + \
                            "' and pat_id in (" + list2query(list_pat) + ")"
    query_1_2 = "select pat_id, name from public.pathologies where pat_id in (" + query_1 + ")" 
    list_pat = postgre_helper.readDB(query_1_2)
    if len(list_pat) > 0:
        return list_pat

    return None

def get_pat_from_categories(list_cat):
    query = ""
    if len(list_cat) > 1:
        for i in range(len(list_cat) - 1):
            query += "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_cat[i] + "' and pat_id in ("
        query += "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_cat[len(list_cat)-1] + "'"
        query += ")))))))))))))"[-(len(list_cat)-1):]
        list_pat = postgre_helper.readDB(query)
    else:
        query = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_cat[0]
        list_pat = postgre_helper.readDB(query)

    if len(list_pat) > 0:
        return list_pat
    else:
        return None
    
def get_pat_from_symptoms(list_pat,sym):
    query = ""
    query += "select * from public.pathologies where pat_id in ( "
    query += "select pat_id from public.pathologies_symptoms where sym_id = '" + sym[0] + "' and pat_id in (" + list2query(list_pat)
    query += "))"
    list_pat = postgre_helper.readDB(query)

    if len(list_pat) > 0:
        return list_pat
    else:
        return None

def first_question(token, language):
    # --- Insertar un elemento vacío
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
    collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

    first_layer = {
        "cat": [],
        "sub_cat": [],
        "sym": [],
        "sub_sub_cat": [],
        "pat": []
    }

    ques_options = []
    questions = [{"question_id": "pregunta1", "options": ques_options}]

    mydict = { 
        "user_id": token, 
        "date": datetime.datetime.now(), 
        "data": first_layer, 
        "last_question": "pregunta1", 
        "show_data": "false", 
        "data_2_show": "",
        "questions": questions 
    }

    response = get_complete_question(FIRST_QUESTION, language)

    options = get_categories()
    
    for i in range(len(options) -1):
        data = {"id": i+1, "value": str(options[i][1]), "db_id": str(options[i][0])}
        ques_options.append(data)

        response = response + "<br>" + str(i+1) + ") " + str(options[i][1])
    
    x = collection.insert_one(mydict)        

    if x:
        if response:
            return response
        else: 
            return None    
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

def middle_question_bkp(text, token, language):
    try:
        #separo las opciones recibidas
        selected_options = get_options_for_text(text)

        #obtengo el elemento completo del usuario y me traigo la ultima layer
        response_saved = db_helper.find_response_by_user(token)

        #obtengo la ultima pregunta para saber que tipo de pregunta tengo que mostrar
        last_question = response_saved["last_question"]

        if last_question == "pregunta1":
            print("Pregunta 1")

        #--- PASO A PASO
        # 1) tomar la respuesta, separarla en diferentes valores
        # 2) con la "last_question", buscar en la respuesta del usuario y ver que opciones eligio y que ids son
        # 3) guardo las cat en la data del json y proceso la busqueda de patologias 
        # 4) traigo las sub categorias de esos sintomas elegidos y los tengo que presentar

        #--- Paso 2 -----
        rta_selected = []
        last_options = []
        questions = response_saved["questions"]
        for quest in questions:
            if quest["question_id"] == last_question:
                last_options = quest["options"]
        
        for sel_opt in selected_options:
            for opt in last_options:
                if opt["id"] == sel_opt:
                    rta_selected.append(str(opt["db_id"]))
        #---------------

        print(rta_selected)

        layers = response_saved["layers"]
        last_layer = layers[len(layers)-1]

        # TODO: revisar el validate
        # if validate_options(selected_options, last_layer["question_id"],language) == False:
        #     raise Exception()

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

def show_data(data,data2show):
    response = ""
    if data2show == "pat":
        for x in data["pat"]:
            response += ". " + x[1] + "<br>"
    return response

def middle_question(text, token, language):
    try:
        client = MongoClient(MONGO_DB_PATH)
        db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
        collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

        #separo las opciones recibidas
        selected_options = get_options_for_text(text)

        #obtengo el elemento completo del usuario y me traigo la ultima layer
        response_saved = db_helper.find_response_by_user(token)

        #obtengo la ultima pregunta para saber que tipo de pregunta tengo que mostrar
        last_question = response_saved["last_question"]

        if response_saved["show_data"] == "true":
            if selected_options[0] == "si":
                response = show_data(response_saved["data"],response_saved["data_2_show"])
                response += "Desea agregar más info? (SI/NO)"
            else:
                response = "Desea agregar más info? (SI/NO)"
            query = { "user_id": token}
            update = {"$set": {"show_data": "moredata", "data_2_show": ""}}
            result = collection.update_one(query, update)
            if response:
                return response
        
        if response_saved["show_data"] == "moredata":
            if selected_options[0] == "si":
                list_subcats = get_subcategories(response_saved["data"]["cat"])
                response = get_complete_question("pregunta2", language)
            
                ques_options = []
                question = {"question_id": "pregunta2", "options": ques_options}

                for i in range(len(list_subcats) -1):
                    data = {"id": i+1, "value": str(list_subcats[i][1]), "db_id": str(list_subcats[i][0])}
                    ques_options.append(data)
                    response = response + "<br>" + str(i+1) + ") " + str(list_subcats[i][1])
                
                query = {"user_id": token}
                update = {"$push": {"questions": question}}
                result = collection.update_one(query, update)

                #Actualizo last_question
                query = { "user_id": token}
                update = {"$set": {"last_question": "pregunta2"}}
                result = collection.update_one(query, update)                           
            else:
                response = "Muchas gracias por haber utilizado el RDiBot"
            query = { "user_id": token}
            update = {"$set": {"show_data": "false", "data_2_show": ""}}
            result = collection.update_one(query, update)
            if response:
                return response

        if last_question == "pregunta1":
            print("Pregunta 1")
            #--- PASO A PASO
            # 1) tomar la respuesta, separarla en diferentes valores
            # 2) con la "last_question", buscar en la respuesta del usuario y ver que opciones eligio y que ids son
            # 3) guardo las cat en la data del json y proceso la busqueda de patologias 
            # 4) traigo las sub categorias de esos sintomas elegidos y los tengo que presentar

            #--- Paso 2 -----
            rta_selected = []
            last_options = []
            questions = response_saved["questions"]
            
            for quest in questions:
                if quest["question_id"] == last_question:
                    last_options = quest["options"]
            
            for sel_opt in selected_options:
                for opt in last_options:
                    if str(opt["id"]) == sel_opt:
                        rta_selected.append(str(opt["db_id"]))
            #---------------

            #--- Paso 3 -----
            query = {"user_id": token}
            update = {"$set": {f"data.cat": rta_selected}}
            result = collection.update_one(query, update)
            
            # TODO: Agregar busqueda de pat
            list_pat = get_pat_from_categories(rta_selected)
            query = {"user_id": token}
            update = {"$set": {f"data.pat": list_pat}}
            result = collection.update_one(query, update)
            response = "Se encontraron {} patologías compatibles. <br>".format(len(list_pat))

            #--- Paso 4 -----

            #busco sub cat
            list_subcats = get_subcategories(rta_selected)
            response += get_complete_question("pregunta2", language)
            
            ques_options = []
            question = {"question_id": "pregunta2", "options": ques_options}

            for i in range(len(list_subcats) -1):
                data = {"id": i+1, "value": str(list_subcats[i][1]), "db_id": str(list_subcats[i][0])}
                ques_options.append(data)
                response = response + "<br>" + str(i+1) + ") " + str(list_subcats[i][1])
            
            query = {"user_id": token}
            update = {"$push": {"questions": question}}
            result = collection.update_one(query, update)

            #Actualizo last_question
            query = { "user_id": token}
            update = {"$set": {"last_question": "pregunta2"}}
            result = collection.update_one(query, update)
            
            if result:
                return response
            
        ## --- Pregunta 2
        if last_question == "pregunta2":
            print("Pregunta 2")
            #--- PASO A PASO
            # 1) tomar la respuesta, separarla en diferentes valores
            # 2) con la "last_question", buscar en la respuesta del usuario y ver que opciones eligio y que ids son
            # 3) guardo las cat en la data del json y proceso la busqueda de patologias 
            # 4) traigo las sub categorias de esos sintomas elegidos y los tengo que presentar

            #--- Paso 2 -----
            rta_selected = []
            last_options = []
            questions = response_saved["questions"]
            
            for quest in questions:
                if quest["question_id"] == last_question:
                    last_options = quest["options"]
            
            for sel_opt in selected_options:
                for opt in last_options:
                    if str(opt["id"]) == sel_opt:
                        rta_selected.append(str(opt["db_id"]))
            #---------------

            #--- Paso 3 -----
            query = {"user_id": token}
            #update = {"$set": {f"data.sub_cat": rta_selected}}
            update = {"$push": {f"data.sub_cat": rta_selected}}
            result = collection.update_one(query, update)
            
            # TODO: Agregar busqueda de pat
            list_pat = get_pat_from_subcategories(response_saved["data"]["pat"],rta_selected)
            query = {"user_id": token}
            update = {"$set": {f"data.pat": list_pat}}
            result = collection.update_one(query, update)
            response = "Se encontraron {} patologías compatibles. <br>".format(len(list_pat))
   
            #--- Paso 4 -----

            #busco síntomas
            list_syms = get_sympthoms(response_saved["data"]["pat"],rta_selected)
            response += get_complete_question("pregunta3", language)
            
            ques_options = []
            question = {"question_id": "pregunta3", "options": ques_options}

            # for i in range(len(list_syms) -1):
            #     data = {"id": i+1, "value": str(list_syms[i][1]), "db_id": str(list_syms[i][0])}
            #     ques_options.append(data)
            #     response = response + "<br>" + str(i+1) + ") " + str(list_syms[i][1])
            n = 1
            for sym in list_syms:
                data = {"id": n, "value": str(sym[1]), "db_id": str(sym[0])}
                ques_options.append(data)
                response = response + "<br>" + str(n) + ") " + str(sym[1])
                n += 1
            
            query = {"user_id": token}
            update = {"$push": {"questions": question}}
            result = collection.update_one(query, update)
            

            #Actualizo last_question
            query = { "user_id": token}
            update = {"$set": {"last_question": "pregunta3"}}
            result = collection.update_one(query, update)

            if result:
                return response
        


        if last_question == "pregunta3":
            print("Pregunta 3")
            #--- PASO A PASO
            # 1) tomar la respuesta, separarla en diferentes valores
            # 2) con la "last_question", buscar en la respuesta del usuario y ver que opciones eligio y que ids son
            # 3) guardo las cat en la data del json y proceso la busqueda de patologias 
            # 4) traigo las sub categorias de esos sintomas elegidos y los tengo que presentar

            #--- Paso 2 -----
            rta_selected = []
            last_options = []
            questions = response_saved["questions"]
            
            for quest in questions:
                if quest["question_id"] == last_question:
                    last_options = quest["options"]
            
            for sel_opt in selected_options:
                for opt in last_options:
                    if str(opt["id"]) == sel_opt:
                        rta_selected.append(str(opt["db_id"]))
            #---------------

            #--- Paso 3 -----
            query = {"user_id": token}
            update = {"$set": {f"data.sym": rta_selected}}
            result = collection.update_one(query, update)
            
            # TODO: Agregar busqueda de pat
            print("llega a buscar pat")
            list_pat = get_pat_from_symptoms(response_saved["data"]["pat"],rta_selected)
            query = {"user_id": token}
            update = {"$set": {f"data.pat": list_pat}}
            result = collection.update_one(query, update)
            response = "Se encontraron {} patologías compatibles. <br>".format(len(list_pat))
            response += "<br>Desea ver los datos? (SI/NO)"
            #Actualizo para mostrar data
            query = { "user_id": token}
            update = {"$set": {"show_data": "true", "data_2_show": "pat"}}
            result = collection.update_one(query, update)
            

            #Actualizo last_question
            query = { "user_id": token}
            update = {"$set": {"last_question": "pregunta2"}}
            result = collection.update_one(query, update)

            if result:
                return response
    
       
        return "ok"
    except Exception as e:
        print(e)
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
            print("MiddleQuestion")
            return middle_question(texto, token, language), None
        else:
            token = secrets.token_hex(20)
            print("FirstQuestion")
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