import os
from collections import defaultdict
from time import sleep

from .Phases import Phase2

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view

# Creating an instance of Phase1 class
phase_object = Phase2()
phase_object.load_index()


# Create your views here.
def index(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase2/index.html')


def index_construction_page(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase2/index_construction.html')


def index_compression_page(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase2/index_compression.html')


def add_document_page(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase2/add_document.html')


def remove_document_page(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase2/remove_document.html')


def set_initial_state():
    """Sets the initial state for phase object."""
    phase_object.state = [0, "Starting...", '']


@api_view(['POST'])
def add_document_single_api(request):
    input_dir = request.data.get('inputDirPath')
    doc_id = Phase2.next_doc_id()
    phase_object.file_name[doc_id] = input_dir
    set_initial_state()

    try:
        with open(input_dir, 'r', encoding='utf-8') as file:
            data = file.read()
        phase_object.add_document_single(doc_id, data)
    except IOError as e:
        print(f"Error reading file '{input_dir}': {e}")

    phase_object.save_index()
    return JsonResponse({'status': 'success'})


@api_view(['POST'])
def remove_document_single_api(request):
    doc_id = int(request.data.get('inputDirPath'))
    set_initial_state()

    try:
        with open(phase_object.file_name[doc_id], 'r', encoding='utf-8') as file:
            data = file.read()
        phase_object.remove_document_single(doc_id, data)
    except IOError as e:
        print(f"Error reading file '{phase_object.file_name[doc_id]}': {e}")

    except KeyError as e:
        return JsonResponse({'status': 'error', 'message': f'Can\'t find this document !'})

    phase_object.save_index()
    return JsonResponse({'status': 'success'})


@api_view(['POST'])
def index_document_api(request):
    input_dir = request.data.get('inputDirPath')

    params = {key: request.data.get(key, False) for key in ['non-positional', 'positional', 'wildcard']}
    set_initial_state()

    try:
        inputs = [i for i in os.listdir(input_dir)]
    except OSError as e:
        print(f"Error reading directory {input_dir}: {e}")
        return JsonResponse({'status': 'error', 'message': f'Can\'t find this directory!'})

    done = 0
    process_length = len(inputs)

    # clear previous files
    Phase2.doc_id = 0
    phase_object.file_name = dict()
    phase_object.non_positional_index = defaultdict(set)
    phase_object.positional_index = defaultdict(lambda: defaultdict(list))
    phase_object.wildcard_index = defaultdict(set)

    for x, filename in enumerate(inputs, start=1):
        doc_id = Phase2.next_doc_id()
        phase_object.file_name[doc_id] = os.path.join(input_dir, filename)

        try:
            with open(phase_object.file_name[doc_id], 'r', encoding='utf-8') as file:
                data = file.read()
            phase_object.add_document(doc_id, data, **params)
            phase_object.state_updater(done, process_length, "Adding...")
            done += 1
        except IOError as e:
            print(f"Error reading file '{phase_object.file_name[doc_id]}': {e}")

    phase_object.state_updater(done, process_length, "Done!")
    phase_object.save_index()
    return JsonResponse({'status': 'success'})


@api_view(['POST'])
def index_compression_api(request):
    params = {key: request.data.get(key, False) for key in ['variable_byte', 'gamma']}
    message = []

    # Calculate memory size before compression
    original_size = (
            phase_object.get_memory_size(phase_object.non_positional_index) +
            phase_object.get_memory_size(phase_object.positional_index) +
            phase_object.get_memory_size(phase_object.wildcard_index)
    )
    message.append(f"Original Size: {original_size} bytes")

    if params['variable_byte']:
        # Compress using Variable Byte Encoding
        compressed_index_vb = phase_object.compress_index(method='variable_byte')
        compressed_size_vb = phase_object.get_memory_size(compressed_index_vb)
        message.append(f"Variable Byte Compressed Size: {compressed_size_vb} bytes")

    if params['gamma']:
        # Compress using Gamma Encoding
        compressed_index_gamma = phase_object.compress_index(method='gamma')
        compressed_size_gamma = phase_object.get_memory_size(compressed_index_gamma)
        message.append(f"Gamma Compressed Size: {compressed_size_gamma} bytes")

    return JsonResponse({'status': 'success', 'message': "<br/><br/>".join(message)})


@api_view(['GET'])
def progress(request):
    """API endpoint for progress."""
    return JsonResponse({'progress': phase_object.state[0], 'state': get_progress_state()})


def validate_directories(input_dir, output_dir):
    """Validates input and output directories."""
    if not all(os.path.isdir(d) for d in [input_dir, output_dir]):
        return False, 'Directories does not exist!'
    if not os.listdir(input_dir):
        return False, 'Input directory is empty!'
    return True, 'All good!'


def get_progress_state():
    """Gets progress state."""
    state = phase_object.state
    return f'{state[2]}/{state[1]}' if state[2] else state[1]
