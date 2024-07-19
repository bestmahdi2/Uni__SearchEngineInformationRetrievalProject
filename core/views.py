from django.shortcuts import render


def index(request):
    """Renders the home page for Learning Log."""
    return render(request, 'core/index.html')
