import openai
import httpx # Added import


class LLMInterface:
    def __init__(self, api_key: str, model_name: str = "gpt-4o", temperature: float = 0.7):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, user_prompt, system_prompt=""):
        # Instantiate httpx.AsyncClient to pass to openai.Client
        # Note: openai.Client is synchronous, but can accept an httpx.AsyncClient
        # which it will manage internally. For a fully async stack, openai.AsyncClient would be used.
        # Given the current LLMInterface.generate is synchronous, this is the less disruptive change.
        http_client = httpx.Client() # Using synchronous httpx.Client with synchronous openai.Client

        client = openai.Client(api_key=self.api_key, http_client=http_client)
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

if __name__ == "__main__": # Added test block
    print("Testing LLMInterface with explicit httpx.Client...")
    try:
        # Ensure OPENAI_API_KEY is available or use a dummy for structure testing
        import os
        api_key = os.getenv("OPENAI_API_KEY_DUMMY", "dummy_key_for_httpx_test")
        if api_key == "dummy_key_for_httpx_test":
            print("Using dummy API key for LLMInterface httpx test.")

        llm_interface = LLMInterface(api_key=api_key)
        # A dummy call that would previously trigger the proxy error.
        # We don't expect a real OpenAI response with a dummy key,
        # but we want to check if the client initialization itself is fixed.
        # The actual call will likely fail due to auth, which is fine for this test.
        print(f"Attempting to call LLM with model: {llm_interface.model_name}")
        # To prevent actual network call in subtask if not desired,
        # we can just test client instantiation.
        # For this test, let's assume the subtask might not have network access
        # or a valid key. The key is to check if openai.Client() instantiation fails.

        # Test Instantiation only
        # Using synchronous httpx.Client here as openai.Client is synchronous
        http_client_test = httpx.Client()
        test_client = openai.Client(api_key=api_key, http_client=http_client_test)
        print(f"Successfully instantiated openai.Client with httpx.Client: {test_client}")

        # If the subtask environment can make calls and has a key, this can be uncommented:
        # print("Attempting a generate call (this will likely fail with dummy key)...")
        # try:
        #     response = llm_interface.generate(user_prompt="Say 'Hello'")
        #     print(f"LLMInterface generate response: {response}")
        # except Exception as call_e:
        #     print(f"LLMInterface generate call failed as expected or unexpectedly: {call_e}")

        print("LLMInterface initialization test passed (no 'proxies' error expected from client init).")
    except Exception as e:
        print(f"Error during LLMInterface test: {e}")
        raise # Re-raise to make subtask fail if there's an issue
