from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
import boto3
import json
import main as model
 
app = Flask(__name__)
 
def get_db_connection():
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name='us-west-2'
        )
       
        secret_name = "rds!db-7a18b7b9-0ae8-4955-a46d-33def5d7059b"
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
       
        secret = json.loads(get_secret_value_response['SecretString'])
       
        conn = psycopg2.connect(
            host='database-2.ctk2ke8se56b.us-west-2.rds.amazonaws.com',
            port='5432',
            database='postgres',
            user=secret['username'],
            password=secret['password']
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None
 
def authenticate(username, password):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    return False
 
def save_rental_data(data, username):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO rental_only (
                    username,
                    pickup_location,
                    pickup_date,
                    pickup_time,
                    drop_off_location,
                    drop_off_date,
                    drop_off_time,
                    age_verification,
                    country,
                    no_of_adults,
                    no_of_children,
                    vehicle_type,
                    preference,
                    output
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                username,
                data['pickup_location'],
                data['pickup_date'],
                data['pickup_time'],
                data['drop_off_location'],
                data['drop_off_date'],
                data['drop_off_time'],
                data['age_verification'],
                data['country'],
                data['no_of_adults'],
                data['no_of_children'],
                data['vehicle_type'],
                data['preference'],
                data.get('output', '')
            ))
 
            result = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            return True
 
        except Exception as e:
            print(f"Database error: {str(e)}")
            if conn:
                conn.rollback()
            return False
    return False
 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
   
    if authenticate(username, password):
        return jsonify({'success': True, 'message': 'Login successful'})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
 
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
   
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
       
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
           
            cur.execute(
                "SELECT username FROM users WHERE username = %s",
                (username,)
            )
            if cur.fetchone():
                return jsonify({'success': False, 'message': 'Username already exists'}), 400
               
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
            cur.close()
            conn.close()
           
            return jsonify({'success': True, 'message': 'Account created successfully'})
           
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    return jsonify({'success': False, 'message': 'Database connection failed'}), 500
 
@app.route('/rental/form', methods=['POST'])
def rental_form():
    data = request.get_json()
    username = data.get('username')
   
    required_fields = [
        'pickup_location', 'pickup_date', 'pickup_time',
        'age_verification', 'country', 'no_of_adults', 'vehicle_type'
    ]
   
    missing = [field for field in required_fields if not data.get(field)]
   
    if missing:
        return jsonify({'success': False, 'message': f'Missing required fields: {", ".join(missing)}'}), 400
       
    try:
        output = model.get_output(data)
        data['output'] = output
        if save_rental_data(data, username):
            return jsonify({'success': True, 'output': output})
        return jsonify({'success': False, 'message': 'Failed to save rental data'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
 
@app.route('/rental/chat', methods=['POST'])
def rental_chat():
    data = request.get_json()
    prompt = data.get('prompt')
    username = data.get('username')
   
    if not prompt:
        return jsonify({'success': False, 'message': 'Prompt is required'}), 400
       
    try:
        bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-west-2')
       
        system_prompt = """You are a helpful car rental assistant. Extract rental information from the user's request and format it as JSON."""
       
        claude_prompt = f"""Human: Extract and understand the following information from this car rental request, the age_verfication should return in 18+ or 25+ or 30+ or 45+ or 60+, the pickup_date and dropoff_date should return in YYYY-MM-DD format only, if the picup_location and dropoff_location has short form,spelling mistake then return with correct location, pickup_time and dropoff_time should return in Morning or Noon or Night based on request. Return only a JSON object with these fields:
        pickup_location, pickup_date, pickup_time, drop_off_location, drop_off_date, drop_off_time, age_verification,
        country, no_of_adults, no_of_children, vehicle_type, preference
 
        Request: {prompt}
 
        Assistant: Here is the extracted information in JSON format:"""
 
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "system": system_prompt,
            "messages": [{"role": "user", "content": claude_prompt}],
            "max_tokens": 1000,
            "temperature": 0,
            "top_p": 1
        })
 
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=body
        )
       
        response_body = json.loads(response['body'].read())
        extracted_data = json.loads(response_body['content'][0]['text'])
       
        output = model.get_output(extracted_data)
        extracted_data['output'] = output
       
        if save_rental_data(extracted_data, username):
            return jsonify({'success': True, 'output': output})
        return jsonify({'success': False, 'message': 'Failed to save rental data'}), 500
       
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
 
if __name__ == '__main__':
    app.run(debug=True)
 
