#GIVE THE SIMILAR SEARCH OUTPUT FROM BOTH CARS AND HISTORY_RECORD TABLES
import Embeddings as embed

from Database_Connect import conn
from Model_Id import embedding_model_id

data = {}

# Search the cars table for the most similar car models based on salient features
def search_cars(response, cursor, vehicle, capacity, limit):
    embedding = response.get('embeddings').get('float')[0]
    sql = '''SELECT car_model, cost, capacity
            FROM (SELECT DISTINCT ON (salient_features) *
                FROM cars_table
                ORDER BY salient_features, car_summary_embedding <=> CAST(%s AS VECTOR)
            )
            WHERE capacity >= %s AND type_of_car = %s
            order by car_summary_embedding  <=> CAST(%s AS VECTOR)
            LIMIT %s
            '''
    cursor.execute(sql, (embedding, capacity, vehicle, embedding, limit))
    result = []
    for row in cursor:
        result.append(row)
    return result

# Search the history table for the most similar car models based on preference
def search_history(response, cursor, limit):
    embedding = response.get('embeddings').get('float')[0]
    sql = '''SELECT car_model, ancillary_available
            FROM (
                SELECT DISTINCT ON (car_model) *
                FROM history_record_table
                ORDER BY car_model, booking_summary_embedding <=> CAST(%s AS VECTOR)
            )
            ORDER BY booking_summary_embedding <=> CAST(%s AS VECTOR)
            LIMIT %s
            '''
    cursor.execute(sql, (embedding, embedding, limit))
    result = []
    for row in cursor:
        result.append(row)
    return result

#converting the search results into Json format
def to_Json(result_salient, result_history):
    results = {
                'salient_features': [],
                'history': []
            }
            
    for content in result_salient:
        item = {
                'car_model': str(content[0]),
                'cost': str(content[1]),
                'capacity' : str(content[2])
            }
        results['salient_features'].append(item)
    
    for content in result_history:
        item = {
                'car_model': str(content[0]),
                'ancillary': str(content[1])
            }
        results['history'].append(item)
    
    return results

#returning the results from the search as Json
def get_results():
    text = [str(data.get('preference'))]
    response = embed.generate_text_embeddings(model_id=embedding_model_id, text=text)

    cursor = conn.cursor()
    
    vehicle = data.get('vehicle_type')      #get the vehicle type
    
    capacity = int(data.get('no_of_adults')) + int(data.get('no_of_children'))        #get the total capacity
    
    result_salient = search_cars(response, cursor, vehicle, capacity, limit=10)
    result_history = search_history(response, cursor, limit=10)
    
    results = to_Json(result_history=result_history, result_salient=result_salient)
    
    return results