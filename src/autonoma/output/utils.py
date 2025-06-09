
from functools import reduce

def is_even(number):
    return number % 2 == 0

def process_items(items):
    return list(map(lambda item: item * 3 if is_even(item) else item + 1, items))

def filter_items(items):
    return list(filter(lambda item: item >= 10, items))

def sum_items(items):
    return reduce(lambda acc, item: acc + item, items)
