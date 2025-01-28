def get_content(result_history, result_salient):
    content = f"""The cars that previous customers chose with a similar preference were {result_history}.
                The cars from the catalogue matching the customer's preference are {result_salient}
                
            Ancillaries:
            INS - Insurance (used mostly if the car is an expensive one)
            CHS - Child Seat (used if there is any child onboard)
            SNT - Snow tire (used in beach, desert or mountainous locations)
            GPS - Navigation (used for long rides or to any unknown areas)
            WIFI - WIFI
            CUR - Curb side pickup (used to bring the car to the customer's location)
            XMR - Radio
            HT - Highway Touring Tires (used mainly for long rides on the highway)
            ATT - All Terrain Tires (used for all terrain purposes)
            RFT - Run Flat Tires
            SST - Self Sealing Tires
            AST - All Season Tires (used in all seasons)
            SOT - Summer Only Tires (used only for summer)
            """
    return content
