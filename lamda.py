import json
import logging
import psycopg2

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event,context):
    
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="RDCom2024",
        host="rditbot2.claoesjfa0zq.us-east-1.rds.amazonaws.com",
        port="5432"
    )
    
    logger.info(event)
    
    if 'body' in event:
        body = event['body']
        body_json = json.loads(body)
        message = body_json.get('message', 'No message provided')
        logger.info(message)

    cur = conn.cursor()

    cur.execute("Select pat_id,name from public.pathologies LIMIT 20")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    # text = event['body']
    # logger.info(text)
    
    token = ""
    
    if 'headers' in event:
        headers = event['headers']
        logger.info(headers['Authorization'])
        token = headers['Authorization'].split()[1]
        
    
    
    if token == "null":
        token = None
    language = "ES"
    
    response = "response"
    # response, new_token = handler(text, token, language)
 
    message = {f"answer": token}

    #return jsonify(message)
    

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message,
            # "location": ip.text.replace("\n", "")
        }),
    }