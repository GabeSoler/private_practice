# views for base app in dreamy
from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required
from django.views.i18n import set_language
from .models import Page


@login_not_required
def index_view(request):
    if request.session.has_key("splash"):
        request.session["splash"] = False
        splash = False
    else:
        request.session["splash"] = True
        splash = True
    context = {"splash": splash}
    return render(request, "base/index.html", context)


@login_not_required
def set_language_wrapper_view(request):
    return set_language(request)


def about_view(request):
    page = Page.objects.filter(title="About").latest("modified")
    template = "base/info-page.html"
    return render(request, template, {"page": page})


def data_policy_view(request):
    page = Page.objects.filter(title="Data Policy").latest("modified")
    template = "base/info-page.html"
    return render(request, template, {"page": page})
