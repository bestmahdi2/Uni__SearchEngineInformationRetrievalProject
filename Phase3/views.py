from .Phases import Phase3, part1, part2

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Creating an instance of Phase1 class
phase_object = Phase3()
phase_object.load_index()


def set_initial_state():
    """Sets the initial state for phase object."""
    phase_object.state = [0, "Starting...", '']


def index(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase3/index.html')


def search_retrieve_page(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase3/search_retrieve_page.html')


def measure_system_page(request):
    """Renders the home page for Learning Log."""
    return render(request, 'Phase3/measure_system_page.html')


@api_view(['GET'])
def progress(request):
    """API endpoint for progress."""
    return JsonResponse({'progress': phase_object.state[0], 'state': get_progress_state()})


def get_progress_state():
    """Gets progress state."""
    state = phase_object.state
    return f'{state[2]}/{state[1]}' if state[2] else state[1]


@api_view(['POST'])
def search_retrieve_api(request):
    input_query = request.data.get('inputQuery')

    phase_object.load_index()
    set_initial_state()

    ranked_results, phrase_results, matching_terms = part1(phase_object, input_query)
    ranked_results = [
        f'{i["rank"]}. [{i["doc_id"]}] <a href="file://{i["path"]}">{i["file_name"]}</a> [{i["score"]:.8f}]' for
        i in ranked_results]
    phrase_results = [
        f'{i["rank"]}. [{i["doc_id"]}] <a href="file://{i["path"]}">{i["file_name"]}</a> [{i["score"]:.8f}]' for
        i in phrase_results]
    ranked_str = "<br><br>".join(ranked_results)
    phrase_str = "<br><br>".join(phrase_results)

    return JsonResponse({'status': 'success',
                         'ranked_results_values': ranked_str, 'ranked_results_length': len(ranked_results),
                         'phrase_results_values': phrase_str, 'phrase_results_length': len(phrase_results),
                         'matching_terms_values': "<br>".join(matching_terms),
                         'matching_terms_length': len(matching_terms)
                         })


@api_view(['POST'])
def measure_system_api(request):
    input_query = request.data.get('inputQuery')
    input_query = [i.strip() for i in input_query.split(",")]
    input_response = request.data.get('inputResponse')
    input_response = [i.strip().split("-") for i in input_response.split(",")]

    phase_object.load_index()
    set_initial_state()

    input_queries = dict(zip(input_query, input_response))

    res_returns = part2(phase_object, input_queries)
    ranked_str = f"F-Measure: {res_returns['ranked']['f_measure']}<br><br>MAP: {res_returns['ranked']['map']}"
    phrase_str = f"F-Measure: {res_returns['phrase']['f_measure']}<br><br>MAP: {res_returns['phrase']['map']}"

    return JsonResponse({'status': 'success',
                         'ranked_results_values': ranked_str, 'phrase_results_values': phrase_str,
                         })
