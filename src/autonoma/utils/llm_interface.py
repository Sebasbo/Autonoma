import openai
import httpx
from typing import Optional, List, Dict, Any # Added List, Dict, Any for messages type


class LLMInterface:
    """
    Interface for interacting with a Language Model, specifically OpenAI's API.
    This class implements the LLMInterfaceProtocol implicitly.
    """
    def __init__(self, api_key: str, model_name: str = "gpt-4o", temperature: float = 0.7) -> None:
        """
        Initializes the LLMInterface.

        Args:
            api_key: The OpenAI API key.
            model_name: The name of the OpenAI model to use (e.g., "gpt-4o").
            temperature: The default sampling temperature for generation.
        """
        self.api_key: str = api_key
        self.model_name: str = model_name
        self.temperature: float = temperature

    def generate(self,
                 user_prompt: str,
                 system_prompt: Optional[str] = None,
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None) -> str:
        """
        Generates a response from the LLM.

        Args:
            user_prompt: The user's prompt.
            system_prompt: An optional system message to guide the LLM's behavior.
            temperature: Optional temperature for this specific call, overrides instance default.
            max_tokens: Optional maximum number of tokens for the response.

        Returns:
            The LLM's generated content as a string.
        """
        # Using synchronous httpx.Client with synchronous openai.Client
        http_client = httpx.Client()

        client = openai.Client(api_key=self.api_key, http_client=http_client)

        messages: List[Dict[str, str]] = []
        # Standard order: system prompt first, then user prompt.
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        completion_params: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "response_format": {"type": "json_object"},
        }
        if max_tokens is not None:
            completion_params["max_tokens"] = max_tokens

        response = client.chat.completions.create(**completion_params)

        content: Optional[str] = response.choices[0].message.content
        if content is None:
            # Handle cases where content might be None, e.g., due to safety filters or other issues.
            return "" # Or raise an error, depending on desired behavior.
        return content

if __name__ == "__main__":
    print("Testing LLMInterface with explicit httpx.Client...")
    try:
        import os
        api_key: str = os.getenv("OPENAI_API_KEY_DUMMY", "dummy_key_for_httpx_test")
        if api_key == "dummy_key_for_httpx_test":
            print("Using dummy API key for LLMInterface httpx test.")

        llm_interface: LLMInterface = LLMInterface(api_key=api_key)

        print(f"Attempting to call LLM with model: {llm_interface.model_name}")

        # Test Instantiation only (as actual calls will fail with dummy key)
        http_client_test: httpx.Client = httpx.Client()
        test_client: openai.Client = openai.Client(api_key=api_key, http_client=http_client_test)
        print(f"Successfully instantiated openai.Client with httpx.Client: {test_client}")

        # Example of how generate might be called (will fail with dummy key)
        print("Attempting a generate call (this will likely fail with dummy key or if network is unavailable)...")
        try:
            # Test with all parameters
            response_content: str = llm_interface.generate(
                user_prompt="Say 'Hello'",
                system_prompt="Be friendly.",
                temperature=0.5,
                max_tokens=10
            )
            print(f"LLMInterface generate response: {response_content}")
        except Exception as call_e:
            print(f"LLMInterface generate call failed as expected or unexpectedly: {call_e}")

        print("LLMInterface initialization and structure test passed (no 'proxies' error expected from client init).")
    except Exception as e:
        print(f"Error during LLMInterface test: {e}")
        raise
