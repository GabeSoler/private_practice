from django_htmx.http import retarget, trigger_client_event, reswap
from django.shortcuts import render, HttpResponse
from django.template.loader import render_to_string


def hx_flex_response(response,
                     re_target: str = None,
                     event_and_target: tuple[str, str] = None,
                     re_swap: str = None):
    if re_target:
        response = retarget(response, re_target)
    if event_and_target:
        event, target = event_and_target
        response = trigger_client_event(response, event, {"target": target})
    if re_swap:
        response = reswap(response, re_swap)
    return response


def hx_oob_render(request, template_1, template_2, context_dict):
    """ chains two template renders and adds oob true to context
    returns a HttpResponse
    remember to add '{% if oob %}"hx-swap-oob="true"{% endif %}' to the second element"""
    context_dict['oob'] = True
    render_1 = render_to_string(template_1, context_dict, request)
    render_2 = render_to_string(template_2, context_dict, request)
    return HttpResponse(render_1 + render_2)


def ok_response_modal(request, text: str,
                      title: str = None,
                      re_target: str = None,
                      event_and_target: tuple[str, str] = None,
                      re_swap: str = None,
                      modal_body=True):
    """
    response ok to forms
    it replaces the form with a text and a thumbs up
    """
    template = "_modal_ok_response.html"
    if modal_body:
        template += "#ok-body-partial"
    else:
        template += "#ok-inner-partial"
    context = {"title": title, "text": text}
    response = render(request, template, context)
    response = hx_flex_response(response, re_target, event_and_target, re_swap)
    return response


def ok_response(request, text: str = None,
                re_target: str = None,
                event_and_target: tuple[str, str] = None,
                re_swap: str = None):
    """ creates an ok response with a template and a text"""
    response = render(request, "_ok.html", {"text": text})
    response = hx_flex_response(response, re_target, event_and_target, re_swap)
    return response


def ok_response_render(request, template, context,
                       re_target: str = None,
                       event_and_target: tuple[str, str] = None,
                       re_swap: str = None):
    """ to be able to render and changing target and adding events """
    response = render(request, template, context)
    response = hx_flex_response(response, re_target, event_and_target, re_swap)
    return response


def ups_response(request, text: str = None, re_target: str = None,
                 event: str = None,
                 event_target: str = None,
                 re_swap: str = None,
                 overlaps=None):
    context = {}
    if text:
        context["text"] = text
    if overlaps:
        context["overlaps"] = overlaps
    response = render(request, "_ups.html", context)
    if re_target:
        response = retarget(response, re_target)
    if event:
        target = event_target or "me"
        response = trigger_client_event(response, event, {"target": target})
    if re_swap:
        response = reswap(response)
    return response
