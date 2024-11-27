from django.shortcuts import render,redirect
from .models import Client,Session
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .forms import ClientForm, SessionForm


#Function to check owner when calling models without the user
def check_owner(topic_owner,request_user):
    if topic_owner != request_user:
        raise Http404
    
# Create your views here.

def index_view(request):
    """show all tools"""
    return render(request,'tools/index.html')


#Session-Client
@login_required
def session_home_view(request):
    """show clients and sessions"""
    clients = Client.objects.filter(user=request.user).order_by('code')
    sessions = Session.objects.filter(user=request.user).order_by('created_at')[:20]
    context = {'clients':clients,'sessions':sessions}
    return render(request,'tools/client_session/home.html',context)



@login_required
def client_view(request,client_pk):
    """show one client"""
    try:
        client = Client.objects.get(pk=client_pk)
        check_owner(client.user,request.user)
    except: raise Http404
    context = {'client':client}
    return render(request,'tools/client_session/client.html',context)

@login_required
def session_view(request,session_pk):
    """show one session"""
    session = Session.objects.get(pk=session_pk)
    check_owner(session.user,request.user)
    context = {'session':session}
    return render(request,'tools/client_session/session.html',context)



@login_required
def clients_view(request):
    """show all clients"""
    clients = Client.objects.filter(user=request.user).order_by('code')
    context = {'clients':clients}
    return render(request,'tools/client_session/client_list.html',context)

@login_required
def sessions_view(request):
    """show all sessions"""
    sessions = Session.objects.filter(user=request.user).order_by('created_at')
    context = {'sessions':sessions}
    return render(request,'tools/client_session/session_list.html',context)

@login_required
def sessions_by_client_view(request,client_pk):
    """show all sessions"""
    try:
        sessions = Session.objects.filter(user=request.user,client=client_pk).order_by('created_at')
    except: Http404
    client = Client.objects.get(pk=client_pk)
    context = {'sessions':sessions,"client":client}
    return render(request,'tools/client_session/session_list_by_client.html',context)



@login_required
def add_client_view(request):
    """add new client"""
    if request.method !='POST':
        #no data submitted; create a blank form
        form = ClientForm()
    else:
        #POST data submitted; process data
        form = ClientForm(data=request.POST)
        if form.is_valid():
            isinstance = form.save(commit=False)
            isinstance.user = request.user 
            isinstance.save()
            return redirect('tools:client_list')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,'tools/client_session/add_client.html',context)

@login_required
def add_session_view(request):
    """add new session"""
    if request.method !='POST':
        #no data submitted; create a blank form
        form = SessionForm()
    else:
        #POST data submitted; process data
        form = SessionForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('tools:index')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,'tools/client_session/add_session.html',context)

@login_required
def edit_client_view(request,client_pk):
    """edit an existing entry"""
    Client_i = Client.objects.get(pk=client_pk)
    check_owner(Client_i.user,request.user)
    if request.method != 'POST':
        #initial request;pre-fill form with the current entry
        form = ClientForm(instance=Client_i)
    else:
        #POST data submitted; process data
        form = ClientForm(instance=Client_i,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('tools:client',client_pk=client_pk)
    context = {'client':Client_i,'form':form}
    return render(request,'tools/client_session/edit_client.html',context)


@login_required
def edit_session_view(request,session_pk):
    """edit an existing Session"""
    session = Session.objects.get(pk=session_pk)
    check_owner(session.user,request.user)
    if request.method != 'POST':
        #initial request;pre-fill form with the current entry
        form = SessionForm(instance=session)
    else:
        #POST data submitted; process data
        form = SessionForm(instance=session,data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("tools:session", session.pk)
    context = {'session':session,'form':form}
    return render(request,'tools/client_session/edit_session.html',context)
