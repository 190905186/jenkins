from pymongo import MongoClient
from datetime import datetime
import requests  # Import the requests library

# Set your MongoDB connection details
mongodb_uri = 'mongodb://localhost:27017'
db_name = 'flag'
flagging_collection = 'flag'
transfer_database="transfer"
base_transfer_url = 'http://localhost:3000/{}/add'  # Base URL for data transfer
base_delete_url = 'http://localhost:3000/{}/delete'  # Base URL for data removal

# List of database names to handle
databases = ['personal', 'educationDetails', 'issues', 'posessions', 'project', 'leaves']

# Connect to MongoDB
client = MongoClient(mongodb_uri)
db = client[db_name]

# Get the current date for comparison
current_date = datetime.now()

# Find records in flaggingDatabase where terminationDate is completed (in the past)
flagging_records = db[flagging_collection].find({"terminationDate": {"$lt": current_date}})

# Loop through flagging records and process them
for record in flagging_records:
    employee_id = record["employeeId"]
    
    # Process transfer and removal for all databases
    for database in databases:
        action = record[database + 'Db']
        if action == "transfer":
            # Use the delete URL for data removal and retrieval
            delete_url = base_delete_url.format(database)

            # Send a removal request to the delete endpoint via an HTTP DELETE request
            response = requests.delete(delete_url, json={"employeeId": employee_id})

            if response.status_code == 200:
                data_to_transfer = response.json()

                # Prepare the endpoint URLs with the appropriate database name
                transfer_url = base_transfer_url.format(transfer_database)

                # Send data to the transfer endpoint via an HTTP POST request
                response = requests.post(transfer_url, json=data_to_transfer)

                if response.status_code == 200:
                    print(f"Transferred {database} data for employee {employee_id} successfully")
                else:
                    print(f"Failed to transfer {database} data for employee {employee_id}")

        elif action == "removal":
            # Use the delete URL for data removal
            delete_url = base_delete_url.format(database)

            # Send a removal request to the delete endpoint via an HTTP DELETE request
            response = requests.delete(delete_url, json={"employeeId": employee_id})

            if response.status_code == 200:
                print(f"Removed {database} data for employee {employee_id} successfully")
            else:
                print(f"Failed to remove {database} data for employee {employee_id}")

# Close the MongoDB connection
client.close()
