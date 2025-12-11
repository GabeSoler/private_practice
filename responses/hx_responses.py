from django_htmx.http import retarget,trigger_client_event,reswap
from django.shortcuts import render

def ok_response_modal(request,title:str,text:str,
                      re_target:str=None,
                      event:str=None,
                      event_target:str=None,
                      re_swap:str=None,
                      partial:str=True):
    template = "_modal_ok_response.html"
    if partial:
        template += "#ok-inner-partial"
    context = {"title":title,"text":text}
    response = render(request,template,context)
    if re_target:
        response = retarget(response,re_target)
    if event:
        target = event_target or "me"
        response = trigger_client_event(response,event,{"target":target})
    if re_swap:
        response = reswap(response)
    return response

def ok_response(request,re_target:str=None,event:str=None,event_target:str=None,re_swap:str=None):
    response = render(request,"_ok.html")
    if re_target:
        response = retarget(response,re_target)
    if event:
        target = event_target or "me"
        response = trigger_client_event(response,event,{"target":target})
    if re_swap:
        response = reswap(response)
    return response

def ups_response(request,text:str=None,re_target:str=None,
                 event:str=None,
                 event_target:str=None,
                 re_swap:str=None,
                 overlaps=None):
    context = {}
    if text:
        context["text"] = text
    if overlaps:
        context["overlaps"] = overlaps
    response = render(request,"_ups.html",context)
    if re_target:
        response = retarget(response,re_target)
    if event:
        target = event_target or "me"
        response = trigger_client_event(response,event,{"target":target})
    if re_swap:
        response = reswap(response)
    return response
