from flask import Flask, request, jsonify
from pymongo import MongoClient
from hdfs import InsecureClient
import json

app = Flask(__name__)

# MongoDB connection settings
mongo_host = 'localhost'
mongo_port = 27017
mongo_db_name = 'hdfs'
mongo_collection_name ='nginx'

# HDFS connection settings
hdfs_host = 'localhost'
hdfs_namenode_port = 9870
hdfs_user = 'hdoop'
hdfs_root = '/BENCHMARK'

# Create a MongoDB client
mongo_client = MongoClient(mongo_host, mongo_port)
db = mongo_client[mongo_db_name]
collection = db[mongo_collection_name]

# Create an HDFS client
hdfs_client = InsecureClient(f'http://{hdfs_host}:{hdfs_namenode_port}', user=hdfs_user)

@app.route('/insert_data', methods=['GET'])
def insert_data():
    try:
        # Get the JSON file path from the request
        json_file_path = "/BENCHMARK/Nginx/process/data_combined.json"



        # Read the JSON data from HDFS
        with hdfs_client.read(json_file_path) as reader:
            json_data = json.loads(reader.read().decode('utf-8'))

        # Insert the JSON data into MongoDB
        inserted_data = collection.insert_one(json_data)

        return jsonify({"message": "Data inserted successfully", "inserted_id": str(inserted_data.inserted_id)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


