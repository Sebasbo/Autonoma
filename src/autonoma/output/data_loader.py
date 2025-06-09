
import csv
import json
from typing import List, Union


def load_csv(file_path: str) -> List[List[str]]:
    data = []
    try:
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while loading the CSV file: {e}")
    return data


def load_json(file_path: str) -> Union[dict, list, None]:
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON.")
    except Exception as e:
        print(f"An error occurred while loading the JSON file: {e}")
    return None


def save_csv(data: List[List[str]], file_path: str) -> None:
    try:
        with open(file_path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            for row in data:
                csv_writer.writerow(row)
    except Exception as e:
        print(f"An error occurred while saving the CSV file: {e}")


def save_json(data: Union[dict, list], file_path: str) -> None:
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"An error occurred while saving the JSON file: {e}")
    