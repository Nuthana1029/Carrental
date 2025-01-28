#import Bedrock as model
import Bedrock as model
import Similarity_Search as search
 
data = {
    'pickup_location': 'Kolkata',
    'pickup_date': '22-08-2024',
    'pickup_time': 'Morning',
    'drop_off_location': 'Bangalore',
    'drop_off_date': '30-08-2024',
    'drop_off_time': 'Noon',
    'age_verification': '25+',
    'country': 'India',
    'customer_id': 12345,
    'no_of_adults': 4,
    'no_of_children': 0,
    'vehicle_type': 'SUV',
    'preference': 'a long drive on the highway with friends'
}
 
search.data = data
results = search.get_results()
 
model.data = data
model.results = results
output = model.get_output()
 
print(output)