from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required

# Create your views here.

@login_not_required
def index_view(request):
    """show all session_client"""
    return render(request, 'base/index.html')

