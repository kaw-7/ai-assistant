import asyncio
import sys
import threading
from typing_extensions import override
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)
from AIProvider.AIProvider import AIProvider
from AIProvider.AIContext import AIContext
import config


def run_async(coro):
    """Run a coroutine safely in any environment (terminal, Spyder, Jupyter).

    - Plain terminal: no loop is running -> asyncio.run() with a
      subprocess-capable policy on Windows.
    - Spyder/Jupyter: a loop is already running -> execute the coroutine
      in a dedicated thread with its own Proactor loop (required for
      subprocess support on Windows).
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No loop running (plain terminal)
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        return asyncio.run(coro)

    # Loop already running (Spyder/Jupyter) -> dedicated thread
    result, error = [None], [None]

    def worker():
        if sys.platform == "win32":
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result[0] = loop.run_until_complete(coro)
        except Exception as e:
            error[0] = e
        finally:
            loop.close()

    t = threading.Thread(target=worker)
    t.start()
    t.join()
    if error[0]:
        raise error[0]
    return result[0]


class ClaudeProvider(AIProvider, AIContext):
    """Uses the Claude Agent SDK, authenticated via your claude.ai
    subscription login (run `claude` once in a terminal to log in).
    No API key required."""

    def __init__(self):
        self.context = ""

    @override
    def generate_response(self, user_input: str) -> str:
        self.save_question(user_input)

        # for debug: save context
        with open(config.CONTEXT_FILE, "w", encoding="utf-8") as f:
            f.write(self.context)

        response_text = run_async(self._ask(user_input))
        self.save_response(response_text)
        return response_text

    async def _ask(self, prompt: str) -> str:
        parts = []
        options = ClaudeAgentOptions(
            allowed_tools=[],  # plain Q&A: no file/bash/web tools
            # model="claude-haiku-4-5-20251001",  # optional: cheaper/faster
        )
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, ResultMessage) and msg.is_error:
                raise RuntimeError(f"Claude error: {msg.result}")
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        parts.append(block.text)
        return "".join(parts)

    @override
    def save_question(self, question_to_ai: str):
        self.context +=   "============= User Question: =============\n"
        self.context += question_to_ai or ""
        self.context += "\n============= User Question end ==========\n"

    @override
    def save_response(self, ai_response: str):
        self.context +=   "============= AI Response: ===============\n"
        self.context += ai_response or ""
        self.context += "\n============= AI Response end ============\n"

    @override
    def retrieve_context(self) -> str:
        return self.context


if __name__ == "__main__":
    provider = ClaudeAgentProvider()
    print(provider.generate_response("Say hello in one short sentence."))