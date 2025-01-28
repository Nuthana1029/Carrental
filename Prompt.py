def get_prompt(content, result_salient, result_history, data, ancillaries):
    prompt = f"""
    You are an expert car recommendation assistant. Based on the following details provided by a customer, please recommend the best matching cars: 3 cars from the {result_salient} and {result_history} along with the best ancillaries available that would be a good match for them.
 
    Customer Details:
    -  Pickup Location: {data.get('pickup_location')}
    -  Pickup Date: {data.get('pickup_date')}
    -  Drop-off Location: {data.get('drop_off_location')}
    -  Drop-off Date: {data.get('drop_off_date')}
    -  Country: {data.get('country')}
    -  Number of Adults: {data.get('no_of_adults')}
    -  Number of Children: {data.get('no_of_children')}
    -  Vehicle Type: {data.get('vehicle_type')}
    -  Preference: {data.get('preference')}
    -  Ancillaries: {ancillaries}
    -  Inventory Source: {data.get('inventory_source')}  # New parameter to specify inventory source
 
    Content for Ancillaries:
    {content}
 
    Guidelines:
    1. Analyze the Context: Consider the route and weather conditions for the pickup and drop-off locations and dates.
    2. Car Model: Use the customer's preferences, similar preference i.e data from {result_salient} and {result_history} and vehicle type to best suit the recommendations.
    3. Ancillaries: Recommend suitable ancillaries that enhance the customer's experience based on their specific needs and the context of their trip, using the provided {content} and data from {result_salient} and {result_history}.
    4. Give only the cars from my {result_salient}
 
    Example:
    If the pickup location is Hyderabad, the pickup date is 2024-07-25 (i.e., rainy season), the vehicle type is an SUV, and the number of children is 2, the response should be as follows:
 
    Based on the preference you gave, the cars are as follows from our inventory:
 
    | Car Model   | Ancillaries Available                        |Reason                                                                                                       |
    |-------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------------|
    | Toyota      | All Season Tire (AST), Insurance (INS),      |The Toyota model is recommended as it provides better traction and stability in adverse weather conditions.  |
    |             |Curb Side Pickup (CUR), GPS Navigation (GPS), |The insurance ancillary is also a good option to have for any unexpected situations during the trip.         |
    |             |Child Seat (CHS)                              |The curb side pickup option could be convenient for the customer, especially if the roads are muddy,         |
    |             |                                              |and the GPS navigation would be helpful for navigating the countryside during the rainy season.              |
 
    Explanation:
    1. Explain in 1-2 sentences why each car is a good match for the customer's needs and preferences.
    2. Mention what the weather will be at the destination.
    3. Ensure the recommendations are based on the customer's specific requirements and the conditions of the route and weather.
 
    Please return the output in the following tabular format.
    please also give the input data {data}
    please give the output from my inventory source
    previous car preference data also show
    display the {result_salient} and {result_history}
    """ 
    return prompt
  
 