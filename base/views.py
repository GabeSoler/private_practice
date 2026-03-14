# views for base app in dreamy
from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required
from django.views.i18n import set_language


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


@login_not_required
def set_language_wrapper_view(request):
    return set_language(request)
