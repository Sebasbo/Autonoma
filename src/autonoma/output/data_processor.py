
from utils import process_item, filter_items
from functools import reduce

def data_processing(data):
    # Use map to process each item in the data
    processed_data = map(process_item, data)
    
    # Use filter to filter processed data
    filtered_data = filter(filter_items, processed_data)
    
    # Use reduce to accumulate a final result (e.g., sum)
    result = reduce(lambda x, y: x + y, filtered_data, 0)
    
    return result

def main():
    sample_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = data_processing(sample_data)
    print(result)
