from django import forms

class ChatForm(forms.Form):
    chat_input = forms.CharField(label='Chat',
                                 help_text="Ask about anything",
                                 max_length=100)

