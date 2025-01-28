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
    """Main application logic"""
    data = {}
    
    # Set page configuration
    st.set_page_config(
    page_title="Car Rental Recommendations",
    layout="wide"
    )
 #setting bckground colors and image
    st.markdown(
        """
        <style>
        .main {
            background-color: #87CEEB; /* Sky blue background for the whole app */
            padding: 0; /* Remove default padding */
            margin: 0; /* Remove default margin */
        }
        .header {
            background-color: #333; /* Dark background for header */
            padding: 10px;
            text-align: center;
            margin-bottom: 0; /* Remove margin below the header */
        }
        .header h1 {
            color: #FFA500; /* Orange color for the header text */
        }
        .container {
            background-color: #f5f5f5; /* Light grey background for the container */
            padding: 20px;
            border-radius: 10px;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50; /* Green background for buttons */
            color: white; /* White text */
            border-radius: 12px; /* Rounded corners */
            padding: 10px 24px; /* Padding */
            font-size: 16px; /* Font size */
        }
        </style>
        """, unsafe_allow_html=True
    )
    # Title of the application
    st.markdown("<h1 style='text-align: center; color: Black;'>Car Rental Recommendations &#128663;</h1>", unsafe_allow_html=True)
 
    # Container for user inputs
    container = st.container(border=True)
 
    with container:
        # Row 1
        col11, col12, col13 = st.columns([10, 3, 6])
        # Pick-up location input
        pickup_location = col11.text_input('pickuplocation', label_visibility='hidden', placeholder='Enter your pick-up location or zip code')
        st.write('Please enter a Pick-up Location')
        # Pick-up date
        pickup_date = col12.date_input('pickupdate', label_visibility='hidden', key='pickup_date', value=None)
        # Pickup time
        pickup_time = col13.selectbox("time", ['Morning', 'Noon', 'Night'],index = None, label_visibility='hidden')
        # Row 2
        col21, col22, col23 = st.columns([10, 3, 6])
        # Return location
        drop_off_location = col21.text_input('dropoffloaction', label_visibility='hidden', placeholder='Return to same Location')
        # Drop-off date input
        drop_off_date = col22.date_input('dropofftime', label_visibility='hidden', key='drop_off_date', value=None)
        # Drop-off time
        Timeend = col23.selectbox('timeend', ['Morning', 'Noon', 'Night'],index = None, label_visibility='hidden')
        # Row 3
        col31, col32, col33, col34, col35, col36 = st.columns([3, 5, 3, 3, 3, 3])
        # Age verification checkbox
        age_verification = col31.selectbox('Age:', ['18+', '25+', '35+', '45+', '55+'], index=None, placeholder="Age*")
        # Selectbox for country
        country_options = ['USA', 'India', 'Canada', 'UK', 'Australia']
        country = col32.selectbox('I live in:',country_options, index=None, placeholder="Select country")
        # Input field for Customer ID
        customer_id = col33.text_input('customer', label_visibility='hidden', placeholder='Add Customer ID*')
        # Dropdown for selecting the number of adults
        no_of_adults = col34.selectbox('noofadults', [1, 2, 3, 4, 5, 6, 7], index=None, placeholder="No. of Adults*", label_visibility='hidden')
        # Dropdown for selecting the number of children
        no_of_children = col35.selectbox('noofchilderen', [0, 1, 2, 3, 4, 5, 6], index=None, placeholder="No. of Children", label_visibility='hidden')
        # Dropdown menu for selecting vehicle type
        vehicle_type = col36.selectbox('vechiletype', ['Sedan', 'SUV', 'Sports', 'Pickup Truck', 'Luxury'], index=None, placeholder="Vehicle Type*", label_visibility='hidden')
        #row4
        col40 = st.columns([1])
        #Asking customer for anything, this will be injected into prompt
        preference = col40[0].text_input('Tell us something about your trip so that we can suggest a car and associated ancillaries more suited for you', placeholder='Ex: Suggest a vehicle and essentials for a family with pets planning a long drive to the countryside.')
    # Retrieve the data from the container and get recommendations
    if st.button('Search', use_container_width=True):
        data = {
                'pickup_location': pickup_location,
                'pickup_date': pickup_date,
                'pickup_time': pickup_time,
                'drop_off_location': drop_off_location,
                'drop_off_date': drop_off_date,
                'drop_off_time': Timeend,
                'age_verification': age_verification,
                'country': country,
                'customer_id': customer_id,
                'no_of_adults': no_of_adults,
                'no_of_children': no_of_children,
                'vehicle_type': vehicle_type,
                'preference': preference
            }
        #this are the required fields
        required = {
            'pickup_location':'Pick Up Location', 'pickup_date':'Pick Up Date', 'pickup_time':'Pick up Time',
            'age_verification': 'Age', 'country':'Country', 'customer_id':'Customer ID', 'no_of_adults':'Number of Adults', 'vehicle_type':'Vehicle Type'
        }
        #getting the missing
        missing = []
        for field,display_name in required.items():
            value = locals().get(field)
            if value in [None,""]:
                missing.append(display_name)
        if not missing:
            try:
                #getting the recommendations from the model
                output = model.get_output(data)
           
                #Display the response received from the model
                st.write(output)
            except Exception as e:
                st.error(f"Error generating recommendation: {e}")
        else:
            missing_values = ", ".join(missing)
            st.warning(f"Please provide the following information: {missing_values}")
    
    # Rest of your existing application code here...
    # (Keep all the existing code from the context)

# Main flow control

# Initialize session state for logged_in status


# Main flow control 
if not st.session_state['logged_in']:
    login_page()
else:
    main_app()


