from pymongo import MongoClient
import logging
import traceback, sys

def save_dataframe_to_mongo(collection_name, data):
    print("\n:==== [Attempting to save data to database] ====:")
    # Mongo client connection
    uri = "mongodb+srv://Admin:uZ2hy9*KKSu6@cphbusinesscluster.lz2v4.gcp.mongodb.net/ScrapingDB?retryWrites=true&w=majority"
    client = MongoClient(uri)
    try:
        #Creating database
        db = client["ScrapingDB"]
        
        #Creating collection for db
        collection = db["data"]


        data.reset_index(inplace=True)
        data_dict = data.to_dict("records")
        
        index = 0
        for url in data["url"].values:
            record_exists = check_if_record_exists_in_db_by_query(client, collection, {"url" : url})
            if record_exists != None:
                print("\tUpdating record")
                collection.delete_one(record_exists)
                collection.insert_one(data_dict[index])
            else:
                
                # Record doesn't exists
                print("\tAdding record")
                collection.insert_one(data_dict[index])
            index = index+1       
        print(":==== [Save complete] ====:")
    except :
        logging.warning("Err! Failed to saved to database")
        print("Err! Failed to saved to database")
         # printing stack trace
        traceback.print_exception(*sys.exc_info())
    finally :
        client.close()

def check_if_record_exists_in_db_by_query(client, collection_name, query):
    uri = "mongodb+srv://Admin:uZ2hy9*KKSu6@cphbusinesscluster.lz2v4.gcp.mongodb.net/ScrapingDB?retryWrites=true&w=majority"
    client = MongoClient(uri)
    try:
        #Creating database
        db = client["ScrapingDB"]
        
        #Creating collection for db
        collection = db["data"]

        mydoc = collection.find_one(query)
        return mydoc

        print(":==== [SAVE COMPLETE] ====:")
    except :
        logging.warning("Err! Failed to saved to database")
        print("Err! Failed to saved to database")
         # printing stack trace
        traceback.print_exception(*sys.exc_info())
    finally :
        client.close()