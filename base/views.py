from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required
# Create your views here.

@login_not_required
def index_view(request):
    if request.session.has_key("splash"):
        request.session["splash"] = False
        splash = False
    else:
        request.session["splash"] = True
        splash = True
    context = {"splash": splash}
    return render(request, 'base/index.html', context)

