from .Phases import Phase1

import os.path
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Creating an instance of Phase1 class
phase_object = Phase1()


def index(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase1/index.html')


def preprocess_text_page(request):
    """Renders the text input page."""
    set_initial_state()
    return render(request, 'Phase1/index_compression.html')


def preprocess_file_page(request):
    """Renders the file input page."""
    set_initial_state()
    return render(request, 'Phase1/index_construction.html')


def set_initial_state():
    """Sets the initial state for phase object."""
    phase_object.state = [0, "Starting...", '']


@api_view(['POST'])
def preprocess_text_api(request):
    """API endpoint for text preprocessing."""
    input_text, preprocess_params = get_input_and_params(request)
    set_initial_state()
    result_text = phase_object.preprocess_text(input_text, **preprocess_params)
    return JsonResponse({'status': 'success', 'values': format_results(result_text), 'length': len(result_text.keys())})


@api_view(['POST'])
def preprocess_file_api(request):
    """API endpoint for file preprocessing."""
    input_dir, output_dir, preprocess_params = get_file_input_and_params(request)
    validate, text = validate_directories(input_dir, output_dir)
    if not validate:
        return JsonResponse({'status': 'failed', 'message': text})

    set_initial_state()
    phase_object.preprocess_files(input_directory=input_dir, output_directory=output_dir, **preprocess_params)
    return JsonResponse({'status': 'success'})


@api_view(['GET'])
def progress(request):
    """API endpoint for progress."""
    return JsonResponse({'progress': phase_object.state[0], 'state': get_progress_state()})


def get_input_and_params(request):
    """Extracts input text and preprocessing parameters from request."""
    input_text = request.data.get('text', '')
    preprocess_params = {key: request.data.get(key, False) for key in ['normalize', 'tokenize', 'token_spacing',
                                                                       'remove_stopwords', 'lemmatize', 'stem',
                                                                       'remove_punctuations']}
    return input_text, preprocess_params


def get_file_input_and_params(request):
    """Extracts file input, output directories, and preprocessing parameters from request."""
    input_dir = request.data.get('inputDirPath')
    output_dir = request.data.get('outputDirPath')
    preprocess_params = get_input_and_params(request)[1]
    return input_dir, output_dir, preprocess_params


def validate_directories(input_dir, output_dir):
    """Validates input and output directories."""
    if not all(os.path.isdir(d) for d in [input_dir, output_dir]):
        return False, 'Directories does not exist!'
    if not os.listdir(input_dir):
        return False, 'Input directory is empty!'
    return True, 'All good!'


def format_results(result_text):
    """Formats results for JsonResponse."""
    return {key: ''.join(value) if key == 'normalize' else ' '.join(value) for key, value in result_text.items()}


def get_progress_state():
    """Gets progress state."""
    state = phase_object.state
    return f'{state[2]}/{state[1]}' if state[2] else state[1]
