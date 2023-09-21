import json
from hdfs import InsecureClient

def mongo_style_query(data, query):
    results = []

    # Ensure that data is a list or a dictionary
    if isinstance(data, dict):
        data = [data]  # Convert a single dictionary into a list of one dictionary

    if not isinstance(data, list):
        raise ValueError("Data must be a dictionary or a list of dictionaries")

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each item in data must be a dictionary")

        match = True
        for key, value in query.items():
            if key not in item or item[key] != value:
                match = False
                break
        if match:
            results.append(item)

    return results

# Create an HDFS client

hdfs_host = 'localhost'
hdfs_namenode_port = 9870
hdfs_user = 'hdoop'
hdfs_root='/BENCHMARK'
hdfs_client = InsecureClient(f'http://{hdfs_host}:{hdfs_namenode_port}', user=hdfs_user)

# Specify the path to your JSON file in HDFS
hdfs_file_path = '/BENCHMARK/Nginx/Benchmark.json'

# Read the JSON data from HDFS
with hdfs_client.read(hdfs_file_path) as hdfs_file:
    data = json.load(hdfs_file)

# Example MongoDB-style query
query = {"isPPSummarized":True}

# Perform the query
query_results = mongo_style_query(data, query)

# Print the results
for result in query_results:
    print(result)
