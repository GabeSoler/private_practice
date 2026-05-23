from openai import OpenAI
from chat_project.settings import OPENAI_API_KEY

class OpenAIManager:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def call_model_messages(self,content:str,model="gpt-4o")->str:
        client = self.client
        content = content
        response = client.chat.completions.create(
            model=model,
            store=True,
            messages=[
                {"role": "system", "content": "You are a helpful assistant expert in education."},
                {"role":"user","content":content}
            ])
        answer = response.choices[0].message.content
        return answer


