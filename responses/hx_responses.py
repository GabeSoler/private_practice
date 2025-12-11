from django_htmx.http import retarget,trigger_client_event,reswap
from django.shortcuts import render

def ok_response(request,title,text,re_target:None,event:None,event_target:None,re_swap:None):
    template = "_modal_ok_response.html"
    context = {"title":title,"text":text}
    response = render(request,template,context)
    if re_target:
        response = retarget(response,re_target)
    if event:
        response = trigger_client_event(response,event,{"target":event_target})
    if re_swap:
        response = reswap(response)
    return response
