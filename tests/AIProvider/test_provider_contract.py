# -*- coding: utf-8 -*-
"""``AIProvider/`` - the contract every AI back end has to fulfil.

The concrete providers talk to a paid service and most of them need an API
key in the environment, so the tests stay on the contract itself and on the
shape of the providers: every caller in this project invokes
``generate_response(user_input=...)`` and swapping the provider in ``main.py``
has to stay a one line change.
"""
from __future__ import annotations

import importlib
import inspect
import unittest

from tests.support import RecordingAIProvider

from AIProvider.AIContext import AIContext
from AIProvider.AIProvider import AIProvider

#: modules of AIProvider/ that hold one provider each
PROVIDER_MODULES = (
    "AIProvider.ClaudeProvider",
    "AIProvider.GeminiProvider",
    "AIProvider.AzureOpenAIProvider",
    "AIProvider.OpenAIProvider",
    "AIProvider.PerplexityProvider",
)


class AIProviderContractTests(unittest.TestCase):

    def test_a_provider_has_to_answer_prompts(self):
        class Incomplete(AIProvider):
            pass

        with self.assertRaises(TypeError):
            Incomplete()

    def test_an_implementation_can_be_used(self):
        provider = RecordingAIProvider(["the answer"])

        self.assertEqual(provider.generate_response(user_input="a prompt"),
                         "the answer")
        self.assertEqual(provider.prompts, ["a prompt"])


class AIContextContractTests(unittest.TestCase):

    def test_a_context_has_to_save_and_retrieve(self):
        class Incomplete(AIContext):
            def save_question(self, prompt):
                pass

        with self.assertRaises(TypeError):
            Incomplete()

    def test_an_implementation_can_be_used(self):
        class Memory(AIContext):
            def __init__(self):
                self.lines = []

            def save_question(self, prompt):
                self.lines.append(f"Q: {prompt}")

            def save_response(self, prompt):
                self.lines.append(f"A: {prompt}")

            def retrieve_context(self):
                return "\n".join(self.lines)

        memory = Memory()
        memory.save_question("why?")
        memory.save_response("because")

        self.assertEqual(memory.retrieve_context(), "Q: why?\nA: because")


class ProviderModuleTests(unittest.TestCase):
    """The providers shipped with the project.

    A provider whose SDK is not installed is skipped instead of failing the
    run - not every machine needs every back end.
    """

    def _provider_classes(self, module_name):
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # missing SDK, missing key, ...
            self.skipTest(f"{module_name} cannot be imported here: {exc}")
        return [obj for _, obj in inspect.getmembers(module, inspect.isclass)
                if issubclass(obj, AIProvider) and obj is not AIProvider
                and obj.__module__ == module_name]

    def test_every_module_holds_one_provider(self):
        for module_name in PROVIDER_MODULES:
            with self.subTest(module=module_name):
                self.assertEqual(len(self._provider_classes(module_name)), 1)

    def test_every_provider_is_asked_with_user_input(self):
        # main.py, the preprocessors and the risk agent all call
        # generate_response(user_input=...) - a provider naming the
        # parameter differently raises a TypeError at the first request
        for module_name in PROVIDER_MODULES:
            with self.subTest(module=module_name):
                for provider in self._provider_classes(module_name):
                    parameters = inspect.signature(
                        provider.generate_response).parameters
                    self.assertIn("user_input", parameters)


if __name__ == "__main__":
    unittest.main()
