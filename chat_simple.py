from db_helper import find_document_by_criteria as find
import json
from flask import session

def get_response_fromDB(id):
    try:
        #Con el med_id busco en la BD
        response = find(id)
        print(response)

        #retorno si encuentro data
        if response:
            #response = json.load(response)
            return response
        else:
            return None
    except:
        return None
    
#del json de la bd, me trae el texto para devolver al usuario
def get_text(response):
    if response['text'] != "":
        return response['text']
    else:
        return None

def get_next_answer(userMsg,last_answer_id):
    #revisar respuesta y comparar con opciones anteriores
    print("Paso por acá")
    print(userMsg)
    print(last_answer_id)

    next_question = ""

    if last_answer_id:
        #print(last_answer_id)

        last_answer = get_response_fromDB(last_answer_id)
        print(last_answer)
        if last_answer["trigger_action"]["type"] == "choice":
            for option in last_answer["trigger_action"]:
                if userMsg == str(option):
                    next_question = last_answer["trigger_action"][option]
            
        if next_question == "":
            #No hay respuesta valida
            return None
        else: 
            session["lastanswerid"] = next_question
            return get_text(get_response_fromDB(next_question))
    else:
        return None



    
    

    
