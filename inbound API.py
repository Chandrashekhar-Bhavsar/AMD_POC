import re
import json
import os
from flask import Flask,jsonify, render_template, request
from pyspark.sql import SparkSession
from hdfs import InsecureClient
from pymongo import MongoClient

# MongoDB connection settings
mongo_host = 'localhost'
mongo_port = 27017
mongo_db_name = 'hdfs'
mongo_collection_name ='nginx'
# Create a MongoDB client
mongo_client = MongoClient(mongo_host, mongo_port)
db = mongo_client[mongo_db_name]
collection = db[mongo_collection_name]


app=Flask(__name__)
app.config['MAX_CONTENT_LENGTH']
hdfs_host = 'localhost'
hdfs_namenode_port = 9870
hdfs_user = 'hdoop'
hdfs_root='/BENCHMARK'
hdfs_client = InsecureClient(f'http://{hdfs_host}:{hdfs_namenode_port}', user=hdfs_user)

@app.route('/')
def home():
    return render_template('webpage.html')

@app.route('/list-files')
def list_folders():

    # Define the HDFS directory path
    hdfs_directory = '/BENCHMARK'

    try:
        # List the folders in the HDFS directory
        folders = hdfs_client.list(hdfs_directory)
        return render_template('list_folder.html', folders=folders)
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/view_folder_content/<folder_name>', methods=['GET'])
def view_folder_content(folder_name):
    folder_path = os.path.join(hdfs_root, folder_name)

    try:
        # Get the content of the selected folder in HDFS
        content = hdfs_client.list(folder_path)
        return render_template('folder_content.html', folder_name=folder_name, content=content)
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@app.route('/read', methods=['POST'])
def read_file():
    print("in read api")
    # Get the file name from the request URL parameter
    data = request.get_json()
    file_name = data.get('file_name')
    print(file_name)

    if not file_name:
        return "Please provide a 'file_name' parameter in the URL."

    hdfs_file_path = '/BENCHMARK/Nginx/' + file_name  # Adjust the path as needed

    try:
        with hdfs_client.read(hdfs_file_path) as reader:
            content = reader.read()
        decoded_content = content.decode('utf-8')
        # print(decoded_content)
        #print(decoded_content)
        return jsonify({'content': decoded_content, 'filename': file_name})
        #return render_template('read_file.html', content=decoded_content,filename=file_name)
    except Exception as e:
        return jsonify({'error': str(e)})

'''
@app.route('/convert', methods=['POST'])
def convert_file():
    try:
        # Get the filename from the request JSON
        data = request.get_json()
        file_name = data.get('file_name')

        if not file_name:
            return jsonify({'error': 'Please provide a file_name parameter in the request JSON.'}), 400

        # Construct source and destination paths
        source_file_path = f'{hdfs_root}/Nginx/{file_name}'
        destination_file_path = f'{hdfs_root}/Nginx/process/{file_name}'

        # Read the nested JSON from HDFS
        with hdfs_client.read(source_file_path) as reader:
            nested_json = json.load(reader)

        # Flatten the nested JSON
        flattened_json = flatten_json(nested_json)

        # Convert the flattened JSON to a JSON string
        flattened_json_str = json.dumps(flattened_json, indent=4)

        # Convert the JSON string to bytes
        flattened_json_bytes = flattened_json_str.encode('utf-8')

        # Write the flattened JSON back to HDFS
        with hdfs_client.write(destination_file_path, overwrite=True) as writer:
            writer.write(flattened_json_bytes)

        return jsonify({'message': f'File {file_name} successfully converted and written to {destination_file_path}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
'''
def get_value_by_key_path(data, key_path):
    keys = key_path.split(',')
    current_data = data

    results = {}
    
    for key in keys:
        key_parts = key.strip().split('.')
        temp_data = current_data
        
        for part in key_parts:
            if part in temp_data:
                temp_data = temp_data[part]
            else:
                results[key] = f"Key or key path '{key}' not found in the data."
                break
        else:
            results[key] = temp_data

    return results


@app.route('/api/extract', methods=['GET'])
def extract():
    
    hdfs_file_path = "/BENCHMARK/Nginx/process/data_combined.json"

    try:
        with hdfs_client.read(hdfs_file_path) as reader:
            json_data = json.loads(reader.read().decode('utf-8'))
    except FileNotFoundError:
        return jsonify({"error": f"File not found at {hdfs_file_path}"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": f"Invalid JSON data in the file at {hdfs_file_path}. Please ensure the file contains valid JSON."}), 400

    keys = request.args.get('keys')

    if not keys:
        return jsonify({"error": "No keys provided in the query parameters"}), 400

    results = get_value_by_key_path(json_data, keys)

    return jsonify(results), 200

@app.route('/search', methods=['GET'])
def combine_json():
    return render_template('search.html') 


pattern = r'Requests/sec:\s+([\d.]+)\s+Transfer/sec:\s+([\d.]+\w+)'


@app.route('/combine',methods=['POST'])
def combine():
    # Define the HDFS file path for Nginx logs
    nginx_log_hdfs_path = '/BENCHMARK/Nginx/nginx-log.txt'  # Replace with the HDFS path to your Nginx logs
    
    try:
        # Read the Nginx log data from HDFS
        with hdfs_client.read(nginx_log_hdfs_path) as reader:
            text_data = reader.read().decode('utf-8')
    except FileNotFoundError:
        return jsonify({"error": f"Nginx log file not found at {nginx_log_hdfs_path}"}), 404
    
    # Use regular expression to extract the data
    matches = re.search(pattern, text_data)

    if matches:
        requests_per_second = float(matches.group(1))
        transfer_per_second = matches.group(2)

        # Create a dictionary with the extracted data
        data_dict = {
            'Requests/sec': requests_per_second,
            'Transfer/sec': transfer_per_second
        }

        # Convert the data to JSON format
        json_data = json.dumps(data_dict, indent=4)

        # Define the output JSON file path in HDFS
        output_json_hdfs_path = '/BENCHMARK/Nginx/nginx-data.json'  # Replace with the desired output HDFS path
        
        # Write the extracted data to an output JSON file in HDFS
        with hdfs_client.write(output_json_hdfs_path, overwrite=True) as writer:
            writer.write(json_data.encode('utf-8'))

        hdfs_folder = '/BENCHMARK/Nginx/'
        # List all .json files in the specified HDFS folder
        hdfs_files = hdfs_client.list(hdfs_folder)
        json_files = [file for file in hdfs_files if file.endswith('.json')]
        print(json_files)

        combined_data = {}
    
        for hdfs_file in json_files:
            hdfs_file_path = f'{hdfs_folder}{hdfs_file}'
            with hdfs_client.read(hdfs_file_path) as reader:
                data = json.loads(reader.read())
                combined_data.update(data)

            # Specify the file path in HDFS where you want to save the combined JSON data
        output_file_path = '/BENCHMARK/Nginx/process/data_combined.json'
    
        if hdfs_client.status(output_file_path, strict=False):
            hdfs_client.delete(output_file_path)
        # Convert the combined data to a JSON string
        json_data = json.dumps(combined_data, indent=4)

        # Write the JSON data to the output JSON file in HDFS with the correct text encoding
        with hdfs_client.write(output_file_path, encoding='utf-8') as writer:
            writer.write(json_data)
    return jsonify({"msg":"data is parsed successfully now you can run queries"})


@app.route('/insert_data', methods=['POST'])
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

if __name__ == '__main__':
    app.run()




