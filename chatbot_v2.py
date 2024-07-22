import os
import json, random
from pymongo import MongoClient
import datetime
import secrets
import psycopg2

# --- Set variables
#MONGO_DB_PATH='mongodb://localhost:27017/'
#MONGO_DB_NAME='rdcom'

MONGO_DB_PATH = 'mongodb+srv://ignacio:3DCWrdMyumZEvfNm@rdcom-bot-questions.2wk6eiw.mongodb.net/'
MONGO_DB_NAME = 'rdcom-bot'
MONGO_DB_COLLECTION_RES="responses"
MONGO_DB_COLLECTION_QUE="questions"

FIRST_QUESTION = "pregunta1"

POSTGRE_DB_HOST = "rditbot2.claoesjfa0zq.us-east-1.rds.amazonaws.com"
POSTGRE_DB_PORT = "5432"
POSTGRE_DB_NAME = "postgres"
POSTGRE_DB_USER = "postgres"
POSTGRE_DB_PASS = "RDCom2024"


def readDB(query):
    # Establecer la conexión con la base de datos
    conn = psycopg2.connect(
        database=POSTGRE_DB_NAME,
        user=POSTGRE_DB_USER,
        password=POSTGRE_DB_PASS,
        host=POSTGRE_DB_HOST,
        port=POSTGRE_DB_PORT
    )

    # Crear un cursor para ejecutar consultas SQL
    cur = conn.cursor()

    # Ejecutar una consulta de lectura
    cur.execute(query)

    # Obtener los resultados de la consulta
    rows = cur.fetchall()

    # Mostrar los resultados
    # for row in rows:
    #     print(row)

    # Cerrar el cursor y la conexión
    cur.close()
    conn.close()

    return rows

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

def get_complete_question(id, language):
    response = find_document_by_criteria_rdcom(id)
    
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
    rows = readDB("select cat_id, name from public.categories where type = 'system' order by 2")
    return rows

def get_subcategories(cat):
    query = "select cat_id, name from public.categories where cat_id in " + \
                "(select cat_id_2 from public.categories_categories where cat_id_1  = '" + cat + "') order by 2"
    print("query subcats",query)
    rows = readDB(query)

    if len(rows) > 0:
        return rows
    
    return None

def get_sympthoms(list_pat, list_subcat):
    query_1 = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_subcat[0] + \
                            "' and pat_id in (" + list2query(list_pat) + ")"
    
    query_2 = "select distinct sym_id from public.pathologies_symptoms where pat_id in (" + query_1
    query_2 += ") and sym_id in (select distinct sym_id from public.categories_symptoms where cat_id in ('" + list_subcat[0] + "'))"

    query_2_2 = "select sym_id, name from public.symptoms where sym_id in (" + query_2 + ") order by 2"
    list_symp = readDB(query_2_2)

    if len(list_symp):
        return list_symp
    
    return None

def get_pat_from_subcategories(list_pat, list_subcat):
    query_1 = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_subcat[0] + \
                            "' and pat_id in (" + list2query(list_pat) + ")"
    query_1_2 = "select pat_id, name from public.pathologies where pat_id in (" + query_1 + ")" 
    list_pat = readDB(query_1_2)
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
        list_pat = readDB(query)
    else:
        query = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_cat[0]
        list_pat = readDB(query)

    if len(list_pat) > 0:
        return list_pat
    else:
        return None
    
def get_pat_from_symptoms(list_pat,sym):
    query = ""
    query += "select * from public.pathologies where pat_id in ( "
    query += "select pat_id from public.pathologies_symptoms where sym_id = '" + sym[0] + "' and pat_id in (" + list2query(list_pat)
    query += ")) order by name"
    list_pat = readDB(query)

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
        "next_cat": "",
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
    
    for i in range(len(options)):
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
        response = find_document_by_criteria_rdcom(question_id)
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


def show_data(data,data2show):
    response = "Las patologías que detectamos que contienen los síntomas indicados son:<br><br>"
    if data2show == "pat":
        for x in data["pat"]:
            response += ". " + x[1] + "<br>"
    return response

def sort_cats(list_cat):
    list_sorted = []
    cats = ""
    for cat in list_cat:
        cats += "'" + cat + "',"
    cats = cats[:len(cats)-1]
    
    list = []
    for cat in list_cat:
        query = "select cat_id, count(0) from public.categories_symptoms where cat_id = '" + cat + "' group by cat_id order by 2"
        rows = readDB(query)
        list.append(rows)
    
    print("lista no ordenada", list)
    list = sorted(list, key=lambda x: x[0][1])
    print("lista ordenada", list)

    flat_list = [item[0][0] for item in list]
    if flat_list:
        print("Flat List", flat_list)
        return flat_list
    
    #Old code
    query = "select cat_id, count(0) from public.categories_symptoms where cat_id in (" + cats + ") group by cat_id order by 2"
    rows = readDB(query)

    for cat in rows:
        list_sorted.append(cat[0])

    if len(list_sorted) > 0:
        print(list_sorted)
        return list_sorted
    
    return None

def get_name_cat(cat_id):
    try:
        query = "select name from public.categories where cat_id = '"+ cat_id + "'"
    
        rows = readDB(query)
        
        text_cat = ""
        
        for cat in rows:
            text_cat = cat[0]
        return text_cat
    
    except:
        return None

def middle_question(text, token, language):
    try:
        client = MongoClient(MONGO_DB_PATH)
        db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
        collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

        #separo las opciones recibidas
        selected_options = get_options_for_text(text)

        #obtengo el elemento completo del usuario y me traigo la ultima layer
        response_saved = find_response_by_user(token)

        #obtengo la ultima pregunta para saber que tipo de pregunta tengo que mostrar
        last_question = response_saved["last_question"]
        list_of_yesoptions = ["si","Sí","Si","sí","yes","sep","sip"]

        if response_saved["show_data"] == "true":
            if selected_options[0] in list_of_yesoptions:
                response = show_data(response_saved["data"],response_saved["data_2_show"])
                response += "<br>Desea ingresar otro síntoma? (SI/NO)"
            else:
                response = "Desea ingresar otro síntoma? (SI/NO)"
            query = { "user_id": token}
            update = {"$set": {"show_data": "moredata", "data_2_show": ""}}
            result = collection.update_one(query, update)
            if response:
                return response
        
        if response_saved["show_data"] == "moredata":
            if selected_options[0] in list_of_yesoptions:
                # list_cats = response_saved["data"]["cat"]
                # actual_cat = response_saved["data"]["next_cat"]
                # if actual_cat == "":
                #     return "Ya no hay más sistemas seleccionados inicialmente. Muchas gracias por haber utilizado el RDiBot"
                
                # next_cat = ""

                # for x in range(len(list_cats)-1):
                #     if list_cats[x] == actual_cat:
                #         next_cat = list_cats[x+1]
                #         break

                list_cats = response_saved["data"]["cat"]
                actual_cat_position = response_saved["data"]["next_cat"]
                if actual_cat_position > len(list_cats)-1:
                    return "Ya no hay más sistemas seleccionados inicialmente. Muchas gracias por haber utilizado el RDiBot"
                
                actual_cat = list_cats[actual_cat_position]

                next_cat = actual_cat_position +1

                query = {"user_id": token}
                update = {"$set": {"data.next_cat": next_cat}}
                result = collection.update_one(query, update)
            
                list_subcats = get_subcategories(actual_cat)

                ##Agrego nombre de la cateogira que voy a mostrar
              
                response = get_complete_question("pregunta2", language)
                response += "<br> <br>" + get_name_cat(actual_cat) + "<br>"
            
                ques_options = []
                question = {"question_id": "pregunta2", "options": ques_options}

                for i in range(len(list_subcats)):
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

            # TODO: Ordenar las cat por mayor a menor cantidad de pat 
            list_cats = sort_cats(rta_selected)

            #--- Paso 3 -----
            query = {"user_id": token}
            # update = {"$set": {f"data.cat": list_cats, "data.next_cat": list_cats[1]}}
            update = {"$set": {f"data.cat": list_cats, "data.next_cat": 1}}

            result = collection.update_one(query, update)


            # Busco y guardo las patologias
            list_pat = get_pat_from_categories(rta_selected)
            query = {"user_id": token}
            update = {"$set": {f"data.pat": list_pat}}
            result = collection.update_one(query, update)
            response = "La cantidad de patologias que quedan filtradas son {}, continuaremos con las consultas para reducir la búsqueda.<br>".format(len(list_pat))

            #--- Paso 4 -----

            #busco sub cat
            list_subcats = get_subcategories(list_cats[0])

            response += get_complete_question("pregunta2", language)
            response += "<br> <br>" + get_name_cat(list_cats[0]) + "<br>"
            
            ques_options = []
            question = {"question_id": "pregunta2", "options": ques_options}
            print("Antes del for subcats", list_subcats)
            for i in range(len(list_subcats)):
                data = {"id": i+1, "value": str(list_subcats[i][1]), "db_id": str(list_subcats[i][0])}
                ques_options.append(data)
                response = response + "<br>" + str(i+1) + ") " + str(list_subcats[i][1])
            
            print("Dsp del for subcats")
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
            response = "La cantidad de patologias que quedan filtradas son {}, continuaremos con las consultas para reducir la búsqueda.<br>".format(len(list_pat))
   
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
            response = "La cantidad de patologias que quedan filtradas son {}.<br>".format(len(list_pat))
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

    response_saved = find_response_by_user(token)

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

    if check_if_token_exist(token):
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
    response_saved = find_response_by_user(token)
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