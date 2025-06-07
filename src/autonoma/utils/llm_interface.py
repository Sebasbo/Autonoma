import openai


class LLMInterface:
    def __init__(self, api_key: str, model_name: str = "gpt-4o", temperature: float = 0.7):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, user_prompt, system_prompt=""):
        client = openai.Client(api_key=self.api_key)
        messages = [{"role": "user", "content": user_prompt}]
        if system_prompt:
            # Ensure system prompt is added correctly if it's part of the design.
            # OpenAI API typically expects system message first if used.
            # Current structure adds it after user, which is unusual.
            # For now, keeping structure but noting it.
            # A more standard order:
            # if system_prompt:
            #     messages.insert(0, {"role": "system", "content": system_prompt})
            # else:
            #     messages = [{"role": "user", "content": user_prompt}]
            # Given the existing code adds it to the end, I'll maintain that for this refactor.
            messages.append({"role": "system", "content": system_prompt})

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
