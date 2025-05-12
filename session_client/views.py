from django.shortcuts import render,redirect, get_list_or_404,get_object_or_404
from .models import Client,Session
from django.contrib.auth.decorators import login_required
from django.http import Http404,HttpResponse
from .forms import ClientForm, SessionForm,SessionShortForm,SearchSessionFrom,SearchClientForm
from django_htmx.http import retarget,reswap
from django.utils import timezone
import pendulum as p
from django.contrib import messages
from django.core.exceptions import FieldError
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

@login_required
def clients_hx_edit(request,client_pk):
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
def client_search_view(request):
    template = 'session_client/client_session/client_search.html'    
    if request.htmx:
        form_partial = SearchClientForm(data=request.POST)
        if form_partial.is_valid():
            search_input = form_partial.cleaned_data['search_input']
            active = form_partial.cleaned_data['active']
            clients = Client.objects.filter(code__icontains=search_input,
                                                active=active,
                                                )
            template_calendar = template + "#client-list-partial"
            context = {'clients':clients}
            return render(request,template_calendar,context)
        else:
            raise Http404(f"The form has errors: {form_partial.errors}")
    clients = Client.objects.none() #? loaded by htmx after load
    form = SearchClientForm()
    context = {'clients':clients,'form':form}
    return render(request,template,context)




@login_required
def client_archived_view(request):
        template = 'session_client/client_session/client_archived_list.html'    
        clients = Client.objects.filter(user=request.user,active=False).order_by('code')
        context = {'clients':clients}
        return render(request,template,context)


#* session

@login_required
def sessions_view(request):
    """show open sessions, add new simple session, update pay status """
    sessions = Session.objects.filter(user=request.user,open=True).order_by('-created_at')
    template = 'session_client/client_session/session_list.html'
    form = SessionShortForm()
    if request.htmx:
        form_partial = SessionShortForm(data=request.POST)
        if form_partial.is_valid():
            instance = form_partial.save(commit=False)
            instance.user = request.user
            instance.session_date = instance.created_at
            instance.save()
            context = {'session':instance}
            template_partial = template + '#row-instance'
            response = render(request,template_partial,context)
            return retarget(response,"#tableBody")
        # render form errors
        template_partial = template + '#session-form-partial'
        context = {'form':form_partial}
        response = render(request,template_partial,context)
        return reswap(response,"innerHTML")
    context = {'sessions':sessions,'form':form}
    return render(request,template,context)

@login_required
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

@login_required
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
def sessions_search(request):
    """ Search sessions by date and client """
    template = "session_client/client_session/session_search.html"
    clients_user = Client.objects.filter(user=request.user) or None # for select
    if request.htmx:
        form_partial = SearchSessionFrom(data=request.POST)
        if form_partial.is_valid():
            start_ref = form_partial.cleaned_data['date_ref_start']
            end_ref = form_partial.cleaned_data['date_ref_end']
            client_ref = form_partial.cleaned_data['client'] or None
            if client_ref:
                # using session date as reference. Added it automatically with quick add option.
                sessions = Session.objects.filter(session_date__gte=start_ref,
                                                session_date__lte=end_ref,
                                                client=client_ref).order_by('session_date')
            else:
                sessions = Session.objects.filter(user=request.user,
                                                session_date__gte=start_ref,
                                                session_date__lte=end_ref,).order_by('session_date')
            template_calendar = template + "#session-list-partial"
            context = {'sessions':sessions}
            return render(request,template_calendar,context)
        else:
            raise Http404(f"The form has errors: {form_partial.errors}")
    sessions = Session.objects.none() #? loaded by htmx after load
    form = SearchSessionFrom()
    form.fields['client'].queryset = clients_user
    context = {'sessions':sessions,'form':form}
    return render(request,template,context)

@login_required
def sessions_search_csv(request):
    """ returns a csv file from a date and client post data"""
    form_partial = SearchSessionFrom(data=request.POST)
    if request.method == 'POST':
        if form_partial.is_valid():
            start_ref = form_partial.cleaned_data['date_ref_start']
            end_ref = form_partial.cleaned_data['date_ref_end']
            client_ref = form_partial.cleaned_data['client'] or None
            if client_ref:
                sessions = Session.objects.filter(session_date__gte=start_ref,
                                                session_date__lte=end_ref,
                                                client=client_ref).order_by('session_date')
            else:
                sessions = Session.objects.filter(user=request.user,
                                                session_date__gte=start_ref,
                                                session_date__lte=end_ref,).order_by('session_date')
            import csv
            start_ref_str = p.instance(start_ref).to_formatted_date_string() #converting for easier formatting
            end_ref_str = p.instance(end_ref).to_formatted_date_string()
            file_name = f"{client_ref}: {start_ref_str}-{end_ref_str}" if client_ref else f"{start_ref_str}-{end_ref_str}"
            response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{file_name}.csv"'})
            fieldnames = ["session_date","client","title","paid"]
            writer = csv.writer(response) # response is the output
            writer.writerow(fieldnames)
            for row in sessions:
                writer.writerow([row.session_date,row.client,row.title,row.paid])
            return response
        else:
            raise Http404(f"The form has errors: {form_partial.errors}")
    else:
        raise Http404("Not a post method")

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
