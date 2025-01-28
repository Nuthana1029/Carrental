import main as model

data = {
    'pickup_location': 'Hyderabad',
    'pickup_date': '02-09-2024',
    'pickup_time': 'Morning',
    'drop_off_location': 'Bangalore',
    'drop_off_date': '09-09-2024',
    'drop_off_time': 'Noon',
    'age_verification': '18+',
    'country': 'India',
    'customer_id': 123,
    'no_of_adults': 2,
    'no_of_children': 2,
    'vehicle_type': 'Sedan',
    'preference': 'suggest me the car that suitable for a family of four planning a beach vacation.'
}

output = model.get_output(data)

print(output)