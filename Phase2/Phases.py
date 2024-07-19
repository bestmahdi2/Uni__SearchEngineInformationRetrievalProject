import os
import pickle
import sys
import json
from collections import defaultdict


class Phase2:
    doc_id = 0

    def __init__(self):
        self.file_name = dict()
        self.non_positional_index = defaultdict(set)
        self.positional_index = defaultdict(lambda: defaultdict(list))
        self.wildcard_index = defaultdict(set)
        self.state = [0, "Not Started Yet!", '']

    @staticmethod
    def next_doc_id():
        Phase2.doc_id += 1
        return Phase2.doc_id

    def state_updater(self, done: int, process_length: int, section: str, directory: str = ''):
        """
            Updates the state of the preprocessing process.

            Args:
                done (int): Number of processed items.
                process_length (int): Total number of items to be processed.
                section (str): Current preprocessing section.
                directory (str, optional): Directory name being processed. Defaults to ''.
        """

        self.state = [round((done / process_length) * 100, 3), section, directory]

    def add_document_single(self, doc_id, text):
        words = text.split()

        done = 0
        process_length = len(words)

        for pos, word in enumerate(words):
            self.non_positional_index[word].add(doc_id)
            self.positional_index[word][doc_id].append(pos)
            self._add_to_wildcard_index(word, doc_id)
            self.state_updater(done, process_length, "Adding...")
            done += 1

        self.state_updater(done, process_length, "Done!")

    def remove_document_single(self, doc_id, text):
        words = text.split()

        done = 0
        process_length = len(words)

        for pos, word in enumerate(words):
            self._remove_from_index(word, doc_id, pos)
            self.state_updater(done, process_length, "Removing...")
            done += 1

        self.state_updater(done, process_length, "Done!")

    def add_document(self, doc_id, text, **kwargs):
        words = text.split()
        for pos, word in enumerate(words):
            if kwargs['non-positional']:
                self.non_positional_index[word].add(doc_id)
            if kwargs['positional']:
                self.positional_index[word][doc_id].append(pos)
            if kwargs['wildcard']:
                self._add_to_wildcard_index(word, doc_id)

    def _remove_from_index(self, word, doc_id, pos):
        if doc_id in self.non_positional_index[word]:
            self.non_positional_index[word].remove(doc_id)
            if not self.non_positional_index[word]:
                del self.non_positional_index[word]
        if doc_id in self.positional_index[word]:
            self.positional_index[word][doc_id].remove(pos)
            if not self.positional_index[word][doc_id]:
                del self.positional_index[word][doc_id]
            if not self.positional_index[word]:
                del self.positional_index[word]
        self._remove_from_wildcard_index(word, doc_id)

    def _add_to_wildcard_index(self, word, doc_id):
        for i in range(len(word)):
            for j in range(i + 1, len(word) + 1):
                self.wildcard_index[word[i:j]].add(doc_id)

    def _remove_from_wildcard_index(self, word, doc_id):
        for i in range(len(word)):
            for j in range(i + 1, len(word) + 1):
                if doc_id in self.wildcard_index[word[i:j]]:
                    self.wildcard_index[word[i:j]].remove(doc_id)
                    if not self.wildcard_index[word[i:j]]:
                        del self.wildcard_index[word[i:j]]

    def save_index(self):
        with open("index.file", "wb") as file:
            pickle.dump({
                "file_names": {str(k): v for k, v in self.file_name.items()},
                "non_positional_index": {str(k): list(v) for k, v in self.non_positional_index.items()},
                "positional_index": {str(k): {str(dk): dv for dk, dv in v.items()} for k, v in
                                     self.positional_index.items()},
                "wildcard_index": {str(k): list(v) for k, v in self.wildcard_index.items()}
            }, file)
        try:
            with open('index.json', 'w', encoding='utf8') as file:
                json.dump(
                    #     {
                    #     "file_names": {str(k): v for k, v in self.file_name.items()},
                    #     "non_positional_index": {k: list(v) for k, v in self.non_positional_index.items()},
                    #     "positional_index": {k: {dk: dv for dk, dv in v.items()} for k, v in self.positional_index.items()},
                    #     "wildcard_index": {k: list(v) for k, v in self.wildcard_index.items()}
                    # }
                    {
                        "file_names": {str(k): v for k, v in self.file_name.items()},
                        "non_positional_index": {str(k): list(v) for k, v in self.non_positional_index.items()},
                        "positional_index": {str(k): {str(dk): dv for dk, dv in v.items()} for k, v in
                                             self.positional_index.items()},
                        "wildcard_index": {str(k): list(v) for k, v in self.wildcard_index.items()}
                    }, file, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving index to 'index.json': {e}")

    def load_index(self):
        # with open("index.file", "rb") as file:
        #     data = pickle.load(file)
        try:
            # with open('index.json', 'r', encoding="utf8") as file:
            #     data = json.load(file)
            with open("index.file", "rb") as file:
                data = pickle.load(file)
                self.file_name = {str(k): v for k, v in data["file_names"].items()}
                self.non_positional_index = defaultdict(set,
                                                        {str(k): set(v) for k, v in
                                                         data["non_positional_index"].items()})
                self.positional_index = defaultdict(lambda: defaultdict(list), {str(k): defaultdict(list, v) for k, v in
                                                                                data["positional_index"].items()})
                self.wildcard_index = defaultdict(set, {str(k): set(v) for k, v in data["wildcard_index"].items()})
        except IOError as e:
            print(f"Error loading index from 'index.json': {e}")

    def get_memory_size(self, obj):
        """Recursively finds the size of objects in bytes."""
        if isinstance(obj, (str, bytes, bytearray)):
            return sys.getsizeof(obj)
        elif isinstance(obj, dict):
            return sys.getsizeof(obj) + sum(self.get_memory_size(k) + self.get_memory_size(v) for k, v in obj.items())
        elif isinstance(obj, (list, set, tuple)):
            return sys.getsizeof(obj) + sum(self.get_memory_size(i) for i in obj)
        return sys.getsizeof(obj)

    def variable_byte_encode(self, numbers, length):
        """Encodes a list of numbers using Variable Byte Encoding."""
        bytes_stream = []
        for number in numbers:
            byte_segments = []
            while True:
                byte_segments.insert(0, number % 128)  # Get 7 least significant bits
                if number < 128:
                    break
                number //= 128
            byte_segments[-1] += 128  # Set the continuation bit
            bytes_stream.extend(byte_segments)
        return bytes_stream

    def gamma_encode(self, number):
        """Encodes a single number using Gamma Encoding."""
        if number == 0:
            return '0'
        binary = bin(number)[2:]
        offset = binary[1:]  # Remove the leading 1
        length = len(offset)
        unary = '1' * length + '0'
        return unary + offset

    def gamma_encode_list(self, numbers):
        """Encodes a list of numbers using Gamma Encoding."""
        return ''.join(self.gamma_encode(number) for number in numbers)

    def compress_index(self, method='variable_byte'):
        """Compresses the index using the specified method ('variable_byte' or 'gamma')."""

        done = 0
        process_length = 3

        if method == 'variable_byte':
            self.state_updater(done, process_length, "Compressing Non-Positional Index...")
            non_positional_index = {
                k: self.variable_byte_encode(list(v), len(self.non_positional_index)) for k, v
                in self.non_positional_index.items()
            }
            done += 1
            self.state_updater(done, process_length, "Compressing Positional Index...")
            positional_index = {
                k: {dk: self.variable_byte_encode(dv, len(self.positional_index)) for dk, dv in v.items()} for k, v
                in self.positional_index.items()
            }
            done += 1
            self.state_updater(done, process_length, "Compressing Wildcard Index...")
            wildcard_index = {
                k: self.variable_byte_encode(list(v), len(self.wildcard_index)) for k, v in
                self.wildcard_index.items()
            }
            done += 1
            self.state_updater(done, process_length, "Done!")
            return {
                "non_positional_index": non_positional_index,
                "positional_index": positional_index,
                "wildcard_index": wildcard_index
            }
        elif method == 'gamma':
            return {
                "non_positional_index": {k: self.gamma_encode_list(list(v)) for k, v in
                                         self.non_positional_index.items()},
                "positional_index": {k: {dk: self.gamma_encode_list(dv) for dk, dv in v.items()} for k, v in
                                     self.positional_index.items()},
                "wildcard_index": {k: self.gamma_encode_list(list(v)) for k, v in self.wildcard_index.items()}
            }
