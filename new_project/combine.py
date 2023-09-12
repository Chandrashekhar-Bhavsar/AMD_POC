import json
import os
local_folder = '/home/hdoop/new_project/'  # Replace with the path to your local folder containing JSON files
output_file_path = '/home/hdoop/new_project/data_combined.json'  # Replace with the desired output file path

def combine():
    local_files = [f for f in os.listdir(local_folder) if f.endswith('.json')]

    combined_data = {}

    for local_file in local_files:
        local_file_path = os.path.join(local_folder, local_file)
        with open(local_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            combined_data.update(data)

    # Convert the combined data to a JSON string
    json_data = json.dumps(combined_data, indent=4)

    # Write the JSON data to the output JSON file in the local file system
    with open(output_file_path, 'w', encoding='utf-8') as writer:
        writer.write(json_data)

    return {"msg": "Data is parsed successfully. You can now run queries."}

# Call the combine() function to perform the operation
result = combine()
print(result)  # Print the result or handle it as needed
