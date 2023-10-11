from pymongo import MongoClient
from datetime import datetime
import requests  # Import the requests library
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JENKINS LOGGER")

# Set your MongoDB connection details
mongodb_uri = 'mongodb://localhost:27017/'
db_name = 'testdb'
flags_collection = 'flags'
transfers_collection = "transfers"
port = '8081'
host = 'localhost'
base_transfer_url = 'http://{}:{}/{}/add'  # Base URL for data transfer
# Base URL for data update in transfer collection
base_transfer_update_url = 'http://{}:{}/{}/update'
base_delete_url = 'http://{}:{}/{}/deleteById'  # Base URL for data removal
base_get_by_id_url = 'http://{}:{}/{}/getById'  # Base URL for data retrieval


# List of database names to handle
databases = ['personalDetails', 'educationDetails', 'issues', 'possessions', 'projects', 'leaves']
# databases = ['possessions']

# Establishing a connection to mongodb server
try:
    logging.info("connecting to the mongodb server ......")
    # Connect to MongoDB
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    logging.info("connected to the mongodb server")
except Exception as e:
    logging.exception(e)
    logging.warn("Exiting the process")
    exit(1)


# Get the current date for comparison
current_date = datetime.now()

# Find records in flagsDatabase where terminationDate is completed (in the past)
flags_records = db[flags_collection].find(
    {"terminationDate": {"$lt": current_date}})


for record in flags_records:
    logging.info(record)
    employee_id = record["_id"]
    data_to_transfer = {}
    # Flag to check if transfer action is performed for this employee
    transfer_requested = False

    # Process transfer and removal for all databases
    for database in databases:
        action = record[database + 'Db']
        logging.info(f"{database}:{action}")
        data_to_transfer["employeeId"] = employee_id
        # if action == "transfer":
        #     logger.info("started the transfer process")
        #     transfer_requested = True  # Mark that transfer is requested for this employee

        #     # Use the delete URL for data removal and retrieval
        #     delete_url = base_delete_url.format(host, port, database)

        #     logging.info(
        #         f"requesting for deletion of the instance from the {database} collection......")
        #     # Send a removal request to the delete endpoint via an HTTP DELETE request
        #     response = requests.delete(
        #         delete_url, params={"id": employee_id})

        #     if response.status_code == 200:
        #         logging.info("deleted the instance successfully")
        #         data = response.json()
        #         # Add the specific field from this database to the data_to_transfer dictionary
        #         field_name = f"{database}List"
        #         if field_name in data:
        #             data_to_transfer[field_name] = data[field_name]
        #     else:
        #         logging.error(response.content)
        #         logging.error(f"Failed to remove the {database} data for employee {employee_id}")

        if action == "remove":

            logging.info("started deletion process")
            # Use the delete URL for data removal
            delete_url = base_delete_url.format(host, port, database)

            logging.info(
                f"requesting for deletion of the instance from the {database} collection......")
            # Send a removal request to the delete endpoint via an HTTP DELETE request
            response = requests.delete(
                delete_url, params={"id": employee_id})

            if response.status_code == 200:
                logging.info(f"Removed {database} data for employee {employee_id} successfully")
                logging.info("completed deletion process")
            else:
                logging.error(response.content)
                logging.error(f"Failed to remove the {database} data for employee {employee_id}")

    # if transfer_requested:
    #     # Get the existing record from the transfer database
    #     get_by_id_url = base_get_by_id_url.format(
    #         host, port, transfers_collection)

    #     logging.info(
    #         "requesting to retrieve record if already present in the transfer database")
    #     response = requests.get(get_by_id_url, params={"id": employee_id})

    #     if response.status_code == 200:
    #         logging.info(
    #             "retrieved the record from the transfer database successfully")
    #         existing_record = response.json()

    #         logging.info(
    #             "merging the data to transfer with the records retrieved")
    #         # Merge data_to_transfer with the existing record
    #         for key, value in data_to_transfer.items():
    #             if key in existing_record:
    #                 if isinstance(existing_record[key], list) and isinstance(value, list):
    #                     # Perform the union of lists
    #                     existing_record[key] += value
    #                 else:
    #                     # Overwrite the existing value with the new value
    #                     existing_record[key] = value
    #             else:
    #                 # Key is not present in existing_record, add the key-value pair
    #                 existing_record[key] = value

    #         logging.info("merging completed successfully")
    #         # Prepare the endpoint URL with the appropriate transfer database name
    #         transfer_url = base_transfer_update_url.format(
    #             host, port, transfers_collection)

    #         logging.info(
    #             "making a put request to update the existing record present in the transfer database")
    #         # Send the integrated data to the transfer endpoint via an HTTP POST request
    #         response = requests.put(transfer_url, json=existing_record)

    #         if response.status_code == 200:
    #             logging.info(
    #                 f"updated data for employee {employee_id} in {transfers_collection} collection successfully")
    #         else:
    #             logging.error(
    #                 f"Failed to update data for employee {employee_id} in {transfers_collection} collection. Status code: {response.status_code}")
    #             logging.error(response.content)
    #             logging.error("deletion process ended with an error")

    #     else:
    #         logging.warning(
    #             f"Failed to retrieve existing record for employee {employee_id} from {transfers_collection}. Status code: {response.status_code}")
    #         logging.warning(response.content)

    #         # Prepare the endpoint URL with the appropriate transfer database name
    #         transfer_url = base_transfer_url.format(
    #             host, port, transfers_collection)

    #         logging.info(
    #             "making a post request to insert a new record in the transfers collection")
    #         # Send the integrated data to the transfer endpoint via an HTTP POST request
    #         response = requests.post(transfer_url, json=data_to_transfer)

    #         if response.status_code == 200:
    #             logging.info(
    #                 f"Transferred data for employee {employee_id} to {transfers_collection} successfully")
    #             logging.info("completed transferring process")
    #         else:
    #             logging.error(response.content)
    #             logging.error(
    #                 f"Failed to transfer data for employee {employee_id} to {transfers_collection}. Status code: {response.status_code}")
    #             logging.error("transferring process ended with an error")

# Close the MongoDB connection
client.close()
