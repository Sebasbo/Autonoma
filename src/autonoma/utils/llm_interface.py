import openai


class LLMInterface:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate(self, user_prompt, system_prompt=""):
        client = openai.Client(api_key=self.api_key)
        messages = [{"role": "user", "content": user_prompt}]
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
