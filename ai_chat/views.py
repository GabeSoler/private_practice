
from django.shortcuts import render
from ai_chat.forms import ChatForm
from openai import OpenAI
from ppm_app.settings import OPENAI_API_KEY
from .models import OpenAIUser
from django.contrib.auth.decorators import login_required,permission_required
from .managers import OpenAIManager

@login_required()
def index(request):
    template = 'chat_learn/index.html'
    form = ChatForm()
    if request.htmx:
        form = ChatForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['chat_input']
            openai_manager = OpenAIManager()
            answer = openai_manager.call_model_messages(content)
            template = 'chat_learn/index.html#chat_response'
            content_format = f"**{content}**"
            return render(request,template,{'answer':answer,'question':content_format})
    context = {'form':form}
    return render(request,template,context)


@login_required()
def thread_conversation(request):
    """ thread option for longer and Assistant based conversations """
    template = 'chat_learn/index.html'
    form = ChatForm()
    if request.htmx:
        form = ChatForm(request.POST)
        client = OpenAI(api_key=OPENAI_API_KEY)
        if form.is_valid():
            try:
                user_thread = OpenAIUser.objects.get(user=request.user)
                thread_id = user_thread.thread_id
            except OpenAIUser.DoesNotExist:
                thread = client.beta.threads.create()
                thread_id = thread.id
                # Save to DB
                OpenAIUser.objects.create(user=request.user, thread_id=thread_id)

            # Add a message to the thread
            response = client.beta.assistants.create_and_run(
                assistant_id="your_assistant_id",
                instructions="You are a helpful assistant.",
                messages=[  # this replaces separate thread + message creation
                    {"role": "user", "content": form.cleaned_data["chat_input"]}
                ],
                thread_id=thread_id,
            )
            # Poll until complete
            # Wait for response
            run_id = response.id
            thread_id = response.thread_id
            # Poll for status as before...
            run = client.beta.assistants.runs.retrieve(run_id=run_id, thread_id=thread_id)
            if run.status == "completed":
                responses = client.beta.assistants.runs.responses.list(thread_id=thread_id, run_id=run_id)
                messages = []
                for msg in responses.data:
                    if msg.role == "assistant":
                        messages.append(msg.content[0].text.value)

            template = 'chat_learn/index.html#chat_response'
            return render(request,template,{'messages':messages})
    context = {'form':form}
    return render(request,template,context)