# -*- coding: utf-8 -*-
"""``Preprocessor/PreprocessingPipeline.py`` - chunker and AI together.

``USE_PREPROCESS_CHUNKING`` decides whether the release notes are handed to
the AI in one go or cut into pieces first.
"""
from __future__ import annotations

import unittest

from tests.support import TempDirTestCase, config_values

import config
from Preprocessor.PreprocessingPipeline import PreprocessingPipeline


class FakeAIPreprocessor:
    """Records which file it was asked to preprocess."""

    def __init__(self, answers=None):
        self.files = []
        self.answers = list(answers or [])

    def preprocess_file(self, release_notes_file_path):
        self.files.append(release_notes_file_path)
        if self.answers:
            return self.answers.pop(0)
        return f"issues of {release_notes_file_path}"


class FakeChunker:
    """Ends after a fixed number of chunks."""

    def __init__(self, chunks=1):
        self.chunks = chunks
        self.calls = 0

    def preprocess_file(self, release_notes_file_path):
        self.calls += 1
        return f"chunk {self.calls}"

    def End(self):
        return self.calls >= self.chunks


class WithoutChunkingTests(TempDirTestCase):
    """``USE_PREPROCESS_CHUNKING = "n"`` - one request for everything."""

    def setUp(self):
        super().setUp()
        self.ai = FakeAIPreprocessor(["the structured issues"])
        self.chunker = FakeChunker()
        self.pipeline = PreprocessingPipeline(self.chunker, self.ai)
        self.notes = self.write("release_notes.txt", "notes")

    def test_hands_the_release_notes_to_the_ai_directly(self):
        with config_values(config, USE_PREPROCESS_CHUNKING="n",
                           TOOL_RELEASE_NOTES=self.notes):
            self.pipeline.Start()

        self.assertEqual(self.ai.files, [self.notes])

    def test_does_not_use_the_chunker(self):
        with config_values(config, USE_PREPROCESS_CHUNKING="n",
                           TOOL_RELEASE_NOTES=self.notes):
            self.pipeline.Start()

        self.assertEqual(self.chunker.calls, 0)

    def test_keeps_the_issues_the_ai_returned(self):
        with config_values(config, USE_PREPROCESS_CHUNKING="n",
                           TOOL_RELEASE_NOTES=self.notes):
            self.pipeline.Start()

        self.assertEqual(self.pipeline.getIssues(), "the structured issues")

    def test_the_setting_is_read_case_insensitively(self):
        with config_values(config, USE_PREPROCESS_CHUNKING="N",
                           TOOL_RELEASE_NOTES=self.notes):
            self.pipeline.Start()

        self.assertEqual(self.chunker.calls, 0)


class WithChunkingTests(TempDirTestCase):
    """``USE_PREPROCESS_CHUNKING = "y"`` - one request per chunk."""

    def setUp(self):
        super().setUp()
        self.notes = self.write("release_notes.txt", "a lot of notes")
        self.overrides = config_values(
            config,
            USE_PREPROCESS_CHUNKING="y",
            TOOL_RELEASE_NOTES=self.notes,
            TEMP_REL_NOTES=self.path("temp_rel_notes.txt"),
            TEMP_CHUNK_FILE=self.path("temp_chunk.txt"),
        )
        self.overrides.__enter__()
        self.addCleanup(self.overrides.__exit__, None, None, None)

    def test_works_on_a_copy_of_the_release_notes(self):
        # the chunker shortens what it reads - the original must survive
        pipeline = PreprocessingPipeline(FakeChunker(), FakeAIPreprocessor())

        pipeline.Start()

        self.assertEqual(self.read("release_notes.txt"), "a lot of notes")
        self.assertEqual(self.read("temp_rel_notes.txt"), "a lot of notes")

    def test_asks_the_ai_once_per_chunk(self):
        ai = FakeAIPreprocessor()
        pipeline = PreprocessingPipeline(FakeChunker(chunks=3), ai)

        pipeline.Start()

        self.assertEqual(len(ai.files), 3)
        self.assertEqual(set(ai.files), {self.path("temp_chunk.txt")})

    def test_collects_the_answers_of_all_chunks(self):
        ai = FakeAIPreprocessor(["first", "second"])
        pipeline = PreprocessingPipeline(FakeChunker(chunks=2), ai)

        pipeline.Start()

        self.assertIn("first", pipeline.getIssues())
        self.assertIn("second", pipeline.getIssues())

    def test_starts_from_an_empty_chunk_file(self):
        self.write("temp_chunk.txt", "chunk of an earlier run")
        pipeline = PreprocessingPipeline(FakeChunker(), FakeAIPreprocessor())

        pipeline.Start()

        self.assertEqual(self.read("temp_chunk.txt"), "")


if __name__ == "__main__":
    unittest.main()
