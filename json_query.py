import json
from hdfs import InsecureClient
hdfs_host = 'localhost'
hdfs_namenode_port = 9870
hdfs_user = 'hdoop'
hdfs_root='/BENCHMARK'
hdfs_client = InsecureClient(f'http://{hdfs_host}:{hdfs_namenode_port}', user=hdfs_user)

def get_value_by_key_path(data, key_path):
    keys = key_path.split('.')
    current_data = data

    for key in keys:
        if key in current_data:
            current_data = current_data[key]
        else:
            return f"Key or key path '{key_path}' not found in the data."

    return current_data

def main():
    hdfs_file_path = "/BENCHMARK/Nginx/process/data_combined.json"  # Replace with the HDFS path to your JSON file

    try:
        with hdfs_client.read(hdfs_file_path) as reader:
            json_data = json.loads(reader.read().decode('utf-8'))
    except FileNotFoundError:
        print(f"File not found at {hdfs_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Invalid JSON data in the file at {hdfs_file_path}. Please ensure the file contains valid JSON.")
        return

    user_input = input("Enter key or key path: ")
    result = get_value_by_key_path(json_data, user_input)
    print(result)

if __name__ == "__main__":
    main()
