from django.shortcuts import render,redirect, get_list_or_404,get_object_or_404
from .models import Client,Session
from django.contrib.auth.decorators import login_required
from django.http import Http404,HttpResponse
from .forms import ClientForm, SessionForm,SessionShortForm
from django_htmx.http import retarget
from django.utils import timezone
from django.template.loader import render_to_string

#Function to check owner when calling models without the user
def check_owner(topic_owner,request_user):
    if topic_owner != request_user:
        raise Http404
    
# Create your views here.

def index_view(request):
    """show all session_client"""
    return render(request,'session_client/index.html')


#Session-Client
@login_required
def session_home_view(request):
    """show clients and sessions"""
    clients = Client.objects.filter(user=request.user).order_by('code')
    sessions = Session.objects.filter(user=request.user).order_by('created_at')[:20]
    context = {'clients':clients,'sessions':sessions}
    return render(request,'session_client/client_session/home.html',context)



@login_required
def client_view(request,client_pk):
    """show one client"""
    client = get_object_or_404(Client,pk=client_pk,user=request.user)
    context = {'client':client}
    return render(request,'session_client/client_session/client.html',context)

@login_required
def session_view(request,session_pk):
    """show one session"""
    session = get_object_or_404(Session,pk=session_pk,user=request.user)
    context = {'session':session}
    return render(request,'session_client/client_session/session.html',context)



@login_required
def clients_view(request):
    """show all clients"""
    template = 'session_client/client_session/client_list.html'    
    clients = Client.objects.filter(user=request.user,active=True).order_by('code')
    form = ClientForm()
    if request.htmx:
        form_partial = ClientForm(data=request.POST)
        if form_partial.is_valid():
            assert form_partial.cleaned_data["code"] is not None
            instance = form_partial.save(commit=False)
            instance.user = request.user
            instance.save()
            assert form_partial.cleaned_data["code"] == instance.code,"Code is not passing when saved"
            clients = Client.objects.filter(user=request.user,active=True).order_by('code')
            context = {'clients':clients}
            template = template + "#client-list-partial"
            response = render(request,template,context)
            return retarget(response,"#client-list-wrapper")
        template = template + '#client-form-partial'
        context = {'form':form_partial}
        return render(request,template,context)
    context = {'clients':clients,'form':form,"switch":"False"}
    return render(request,template,context)

def clients_edit_view(request,client_pk):
    """ manages clients htmx calls """
    if request.method == 'PUT':
        occurrence = get_object_or_404(Client,pk=client_pk,user=request.user)
        if occurrence.active is True:
            occurrence.active = False
        else:
            occurrence.active = True
        occurrence.archived_at = timezone.now()
        occurrence.save()
        return HttpResponse() # empty response that empties the li object

@login_required
def client_archived_view(request):
        template = 'session_client/client_session/client_archived_list.html'    
        clients = Client.objects.filter(user=request.user,active=False).order_by('code')
        context = {'clients':clients}
        return render(request,template,context)




@login_required
def sessions_view(request):
    """show all sessions"""
    sessions = Session.objects.filter(user=request.user).order_by('-created_at')
    template = 'session_client/client_session/session_list.html'
    form = SessionShortForm()
    if request.htmx:
        form_partial = SessionShortForm(data=request.POST)
        if form_partial.is_valid():
            instance = form_partial.save(commit=False)
            instance.user = request.user
            instance.save()
            context = {'sessions':sessions}
            assert instance in sessions,"Instance not saved properly"
            template_partial = template + '#session-list-partial'
            response = render(request,template_partial,context)
            return retarget(response,"#session-list-wrapper")
        # render form errors
        template_partial = template + '#session-form-partial'
        context = {'form':form_partial}
        return render(request,template_partial,context)
    context = {'sessions':sessions,'form':form}
    return render(request,template,context)

def sessions_hx_edit_paid(request,session_pk):
    """ manages clients htmx calls """
    if request.method == 'PUT':
        session = get_object_or_404(Session,pk=session_pk,user=request.user)
        if session.paid is True:
            session.paid = False
        else:
            session.paid = True
        session.save()
        template = 'session_client/client_session/session_list.html#session_paid'
        context = {'session':session}
        return render(request,template,context) # empty response that empties the li object

def sessions_hx_edit_open(request,session_pk):
    """ manages clients htmx calls """
    if request.method == 'PUT':
        session = get_object_or_404(Session,pk=session_pk,user=request.user)
        if session.open is True:
            session.open = False
        else:
            session.open = True
        session.save()
        template = 'session_client/client_session/session_list.html#session_open'
        context = {'session':session}
        return render(request,template,context) # empty response that empties the li object


@login_required
def sessions_by_client_view(request,client_pk):
    """show all sessions"""
    sessions = get_list_or_404(Session,user=request.user,client=client_pk)
    sessions = sessions.order_by('created_at')
    client = Client.objects.get(pk=client_pk)
    context = {'sessions':sessions,"client":client}
    return render(request,'session_client/client_session/session_list_by_client.html',context)



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
            return redirect('session_client:client_list')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,'session_client/client_session/add_client.html',context)

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
            return redirect('session_client:index')
    #display a blank or invalid form
    context = {'form':form}
    return render(request,'session_client/client_session/add_session.html',context)

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
            return redirect('session_client:client',client_pk=client_pk)
    context = {'client':Client_i,'form':form}
    return render(request,'session_client/client_session/edit_client.html',context)


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
            return redirect("session_client:session", session.pk)
    context = {'session':session,'form':form}
    return render(request,'session_client/client_session/edit_session.html',context)
