from autonoma import AutonomaAgent
from autonoma.utils.llm_interface import LLMInterface
from autonoma.config.settings import OPENAI_API_KEY
import json
import os
from autonoma.models.agent import CodeFile


def main():
    llm_interface = LLMInterface(os.getenv("OPENAI_API_KEY"))
    autonoma = AutonomaAgent(llm_interface)
    query = "Refactor the functions in data_processor.py and utils.py to use higher-order functions like map, filter, and reduce instead of for loops"
    codebase = [
        {
            "path": "data_processor.py",
            "content": """
from utils import is_even, process_item, filter_items
import tensorflow

def data_processing(data):
    processed_data = []
    for item in data:
        processed_data.append(process_item(item))
    
    filtered_data = []
    for item in processed_data:
        if filter_items(item):
            filtered_data.append(item)
    return filtered_data

def main():
    sample_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = data_processing(sample_data)
    print(result)
    """,
        },
        {
            "path": "utils.py",
            "content": """
def is_even(number):
    return number % 2 == 0

def process_item(item):
    if is_even(item):
        return item * 3
    else:
        return item + 1

def filter_items(item):
    return item > 10
    """,
        },
    ]

    result = autonoma.process_query(query, [CodeFile(**file) for file in codebase])


if __name__ == "__main__":
    main()
