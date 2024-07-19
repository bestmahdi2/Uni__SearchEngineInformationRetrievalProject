import os
import sys
import json
from collections import defaultdict


class InvertedIndex:
    pass

# Example usage:
index = InvertedIndex()
PATH = 'Inputs'

try:
    inputs = [i for i in os.listdir(PATH)]
except OSError as e:
    print(f"Error reading directory {PATH}: {e}")
    inputs = []

for x, filename in enumerate(inputs, start=1):
    try:
        with open(os.path.join(PATH, filename), 'r', encoding='utf-8') as file:
            data = file.read()
        index.add_document(x, data)
    except IOError as e:
        print(f"Error reading file {filename}: {e}")

# Calculate memory size before compression
original_size = (
        index.get_memory_size(index.non_positional_index) +
        index.get_memory_size(index.positional_index) +
        index.get_memory_size(index.wildcard_index)
)

# Compress using Variable Byte Encoding
compressed_index_vb = index.compress_index(method='variable_byte')
compressed_size_vb = index.get_memory_size(compressed_index_vb)

# Compress using Gamma Encoding
compressed_index_gamma = index.compress_index(method='gamma')
compressed_size_gamma = index.get_memory_size(compressed_index_gamma)

print(f"Original Size: {original_size} bytes")
print(f"Compressed Size with Variable Byte Encoding: {compressed_size_vb} bytes")
print(f"Compressed Size with Gamma Encoding: {compressed_size_gamma} bytes")

# Uncomment the following lines if you want to remove a document or save/load the index
# index.remove_document(1, data)
# index.save_index("index.json")
# index.load_index("index.json")
