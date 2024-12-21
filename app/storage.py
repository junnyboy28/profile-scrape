import json
import csv
import os

def save_data_to_json(data, filename):
    filepath = os.path.join('data', filename)
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def save_data_to_csv(data, filename):
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
