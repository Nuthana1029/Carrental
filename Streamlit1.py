 
import main as model
import streamlit as st
from datetime import datetime
import psycopg2
from Universal_Variables import *          
import boto3
import json
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
 
def get_db_connection():
    """Create database connection using AWS Secrets Manager"""
    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
       
        # Get secret value
        secret_name = "rds!db-7a18b7b9-0ae8-4955-a46d-33def5d7059b"
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
       
        # Parse secret string
        secret = json.loads(get_secret_value_response['SecretString'])
       
        # Create database connection
        conn = psycopg2.connect(
            host='database-2.ctk2ke8se56b.us-west-2.rds.amazonaws.com',
            port='5432',
            database='postgres',
            user=secret['username'],
            password=secret['password']
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None
 
def authenticate(username, password):
    """Check if username/password combination exists in database"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Query to check credentials
            cur.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result is not None
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return False
    return False
 
def login_page():
    """Display the login page"""
    if 'show_login' not in st.session_state:
        st.session_state['show_login'] = True
       
    st.markdown("<h1 style='text-align: center; color: Black;'>Car Rental Login</h1>", unsafe_allow_html=True)
   
    if st.session_state['show_login']:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            col1, col2 = st.columns(2)
            submit = col1.form_submit_button("Login")
            create_acc = col2.form_submit_button("Create Account")
           
            if submit:
                if authenticate(username, password):
                    st.session_state['logged_in'] = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")
                   
            if create_acc:
                st.session_state['show_login'] = False
                st.rerun()
    else:
        create_account()
        if st.button("Back to Login"):
            st.session_state['show_login'] = True
            st.rerun()
def create_account():
    """Create a new user account"""
    st.markdown("<h1 style='text-align: center; color: Black;'>Create Account</h1>", unsafe_allow_html=True)
   
    with st.form("create_account_form"):
        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Create Account")
       
        if submit:
            if new_password != confirm_password:
                st.error("Passwords do not match!")
                return
               
            if not new_username or not new_password:
                st.error("Username and password are required!")
                return
               
            conn = get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                   
                    # Check if username already exists
                    cur.execute(
                        "SELECT username FROM users WHERE username = %s",
                        (new_username,)
                    )
                    if cur.fetchone():
                        st.error("Username already exists!")
                        return
                       
                    # Insert new user
                    cur.execute(
                        "INSERT INTO users (username, password) VALUES (%s, %s)",
                        (new_username, new_password)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                   
                    st.success("Account created successfully! Please log in.")
                    st.session_state['show_login'] = True
                    st.rerun()
                   
                except Exception as e:
                    st.error(f"Error creating account: {e}")
                    return
            else:
                st.error("Database connection failed!")
def main_app():
    """Main application logic for chatbot interface"""
   
    # Set page configuration
    st.set_page_config(
        page_title="Car Rental Chatbot",
        layout="wide"
    )
 
    # Title of the application
    st.markdown("<h1 style='text-align: center; color: Black;'>Car Rental Chatbot 🚗</h1>", unsafe_allow_html=True)
 
    # Initialize session state for conversation
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        # Add initial welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm your car rental assistant. To help you find the perfect car, I'll need some information. Let's start with your pickup location - where would you like to rent the car from?"
        })
 
    # Initialize data dictionary to store user inputs
    if 'data' not in st.session_state:
        st.session_state.data = {
            'pickup_location': None,
            'pickup_date': None,
            'pickup_time': None,
            'drop_off_location': None,
            'drop_off_date': None,
            'drop_off_time': None,
            'age_verification': None,
            'country': None,
            'customer_id': None,
            'no_of_adults': 0,  # Initialize with 0 instead of None
            'no_of_children': 0, # Initialize with 0 instead of None
            'vehicle_type': None,
            'preference': None
        }
 
    # Initialize conversation state
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 'pickup_location'
 
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
 
    # Chat input
    if prompt := st.chat_input("Type your response here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
 
        # Process user input based on current question
        if st.session_state.current_question == 'pickup_location':
            st.session_state.data['pickup_location'] = prompt
            st.session_state.current_question = 'pickup_date'
            response = "Great! When would you like to pick up the car? (Please provide date in YYYY-MM-DD format)"
 
        elif st.session_state.current_question == 'pickup_date':
            try:
                st.session_state.data['pickup_date'] = datetime.strptime(prompt, '%Y-%m-%d').date()
                st.session_state.current_question = 'pickup_time'
                response = "What time would you prefer for pickup? (Morning/Noon/Night)"
            except ValueError:
                response = "Please enter a valid date in YYYY-MM-DD format."
 
        elif st.session_state.current_question == 'pickup_time':
            if prompt.lower() in ['morning', 'noon', 'night']:
                st.session_state.data['pickup_time'] = prompt
                st.session_state.current_question = 'drop_off_location'
                response = "Where would you like to drop off the car?"
            else:
                response = "Please select from Morning, Noon, or Night."
 
        elif st.session_state.current_question == 'drop_off_location':
            st.session_state.data['drop_off_location'] = prompt
            st.session_state.current_question = 'drop_off_date'
            response = "When would you like to drop off the car? (Please provide date in YYYY-MM-DD format)"
 
        elif st.session_state.current_question == 'drop_off_date':
            try:
                st.session_state.data['drop_off_date'] = datetime.strptime(prompt, '%Y-%m-%d').date()
                st.session_state.current_question = 'drop_off_time'
                response = "What time would you prefer for drop off? (Morning/Noon/Night)"
            except ValueError:
                response = "Please enter a valid date in YYYY-MM-DD format."
 
        elif st.session_state.current_question == 'drop_off_time':
            if prompt.lower() in ['morning', 'noon', 'night']:
                st.session_state.data['drop_off_time'] = prompt
                st.session_state.current_question = 'age_verification'
                response = "Please tell me your age group: (18+/25+/35+/45+/55+)"
            else:
                response = "Please select from Morning, Noon, or Night."
       
        elif st.session_state.current_question == 'age_verification':
            if prompt in ['18+', '25+', '35+', '45+', '55+']:
                st.session_state.data['age_verification'] = prompt
                st.session_state.current_question = 'country'
                response = "Which country are you from? (USA/India/Canada/UK/Australia)"
            else:
                response = "Please select a valid age group: 18+/25+/35+/45+/55+"
 
        elif st.session_state.current_question == 'country':
            if prompt.upper() in ['USA', 'INDIA', 'CANADA', 'UK', 'AUSTRALIA']:
                st.session_state.data['country'] = prompt
                st.session_state.current_question = 'customer_id'
                response = "Please provide your Customer ID:"
            else:
                response = "Please select from USA, India, Canada, UK, or Australia."
 
        elif st.session_state.current_question == 'customer_id':
            st.session_state.data['customer_id'] = prompt
            st.session_state.current_question = 'no_of_adults'
            response = "How many adults will be traveling? (1-7)"
 
        elif st.session_state.current_question == 'no_of_adults':
            if prompt.isdigit() and 1 <= int(prompt) <= 7:
                st.session_state.data['no_of_adults'] = int(prompt)
                st.session_state.current_question = 'no_of_children'
                response = "How many children will be traveling? (0-6)"
            else:
                response = "Please enter a number between 1 and 7."
 
        elif st.session_state.current_question == 'no_of_children':
            if prompt.isdigit() and 0 <= int(prompt) <= 6:
                st.session_state.data['no_of_children'] = int(prompt)
                st.session_state.current_question = 'vehicle_type'
                response = "What type of vehicle would you prefer? (Sedan/SUV/Sports/Pickup Truck/Luxury)"
            else:
                response = "Please enter a number between 0 and 6."
 
        elif st.session_state.current_question == 'vehicle_type':
            if prompt.title() in ['Sedan', 'SUV', 'Sports', 'Pickup Truck', 'Luxury']:
                st.session_state.data['vehicle_type'] = prompt
                st.session_state.current_question = 'preference'
                response = "Finally, tell me about your trip so I can suggest the best car and accessories for you:"
            else:
                response = "Please select from Sedan, SUV, Sports, Pickup Truck, or Luxury."
 
        elif st.session_state.current_question == 'preference':
            st.session_state.data['preference'] = prompt
            try:
                # Get recommendations from the model
                output = model.get_output(st.session_state.data)
                response = f"Based on your requirements, here are my recommendations:\n\n{output}"
                # Reset conversation
                st.session_state.current_question = 'complete'
            except Exception as e:
                response = f"Error generating recommendation: {e}"
 
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
 
if not st.session_state['logged_in']:
    login_page()
else:
    main_app()
 
 
 
 
