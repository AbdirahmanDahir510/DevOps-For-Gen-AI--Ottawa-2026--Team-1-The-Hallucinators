import re
from typing import List, Dict

from ollama import chat


class OllamaLLMClient:

    def __init__(self, model: str = "llama3.2"):
        self.model = model

    def create_chat_completion(
        self,
        messages: List[Dict[str, str]]
    ) -> str:

        response = chat(
            model=self.model,
            messages=messages
        )

        return response.message.content


class SecureChatbot:

    def __init__(self, system_instruction: str):

        self.client = OllamaLLMClient(
            model="llama3.2"
        )

        self.system_instruction = system_instruction

        self.chat_history: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": self.system_instruction
            }
        ]

        # Basic prompt-injection detection
        self.blocked_patterns = [

            re.compile(
                r"ignore\s+(?:all\s+)?previous\s+instructions",
                re.IGNORECASE
            ),

            re.compile(
                r"system\s+prompt\s+bypass",
                re.IGNORECASE
            )
        ]

    def _sanitize_input(self, user_input: str) -> str:

        """
        Defensive Layer 1:
        Input validation / sanitization.
        """

        for pattern in self.blocked_patterns:

            if pattern.search(user_input):

                raise ValueError(
                    "Potential prompt injection attempt detected."
                )

        cleaned_input = user_input.strip()

        if not cleaned_input:

            raise ValueError(
                "Please enter a message."
            )

        if len(cleaned_input) > 2000:

            raise ValueError(
                "Message is too long. "
                "Please keep messages under 2000 characters."
            )

        return cleaned_input

    def send_message(self, user_input: str) -> str:

        try:

            sanitized_input = self._sanitize_input(
                user_input
            )

        except ValueError as e:

            return str(e)

        # Add user message
        self.chat_history.append(
            {
                "role": "user",
                "content": sanitized_input
            }
        )

        try:

            # Send conversation to local AI
            response = self.client.create_chat_completion(
                self.chat_history
            )

        except Exception as e:

            print("Ollama Error:", e)

            return (
                "Sorry, I couldn't connect to "
                "the local AI model."
            )

        # Save AI response
        self.chat_history.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        return response


def main():

    bot = SecureChatbot(

        system_instruction=(
            "You are a helpful assistant. "
            "Keep responses reasonably concise."
        )

    )

    print("================================")
    print("       Local AI Chatbot")
    print("================================")
    print("Powered by Ollama + Llama 3.2")
    print("Type 'quit' to exit.")
    print()

    while True:

        user_input = input("You: ")

        if user_input.lower() in [
            "quit",
            "exit"
        ]:

            print("Goodbye!")

            break

        response = bot.send_message(
            user_input
        )

        print()
        print("Bot:", response)
        print()


if __name__ == "__main__":
    main()