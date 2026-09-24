# -*- coding: utf-8 -*-
"""``Preprocessor/TextChunkerPreprocessor.py`` - cutting the release notes.

The chunker hands the AI one piece at a time and shortens the input file by
what it consumed, so that the next call continues where the last one stopped.
"""
from __future__ import annotations

import unittest

from tests.support import RecordingAIProvider, TempDirTestCase, captured_stdout, config_values

import config
from Preprocessor.TextChunkerPreprocessor import TextChunkerPreprocessor

CHUNK_SIZE = 50


class ChunkerTestCase(TempDirTestCase):
    """A chunker working on small chunks inside the temporary folder."""

    def setUp(self):
        super().setUp()
        self.chunker = TextChunkerPreprocessor(RecordingAIProvider())
        self.overrides = config_values(
            config,
            CHUNK_SIZE=CHUNK_SIZE,
            CHUNK_DELIMITER="[[ =cut= ]]",
            TEMP_CHUNK_FILE=self.path("temp_chunk.txt"),
        )
        self.overrides.__enter__()
        self.addCleanup(self.overrides.__exit__, None, None, None)

    def chunk(self, text: str) -> str:
        source = self.write("release_notes.txt", text)
        with captured_stdout():
            return self.chunker._generate_chunk(source)


class ShortInputTests(ChunkerTestCase):
    """Release notes that fit into a single request."""

    def test_returns_everything(self):
        text = "one short release note"

        self.assertEqual(self.chunk(text), text)

    def test_says_that_it_is_done(self):
        self.chunk("one short release note")

        self.assertTrue(self.chunker.End())

    def test_consumes_the_whole_text(self):
        text = "one short release note"

        self.chunk(text)

        self.assertEqual(self.chunker.slice_position, len(text))


class DelimiterTests(ChunkerTestCase):
    """A delimiter written into the release notes wins over everything."""

    def test_cuts_directly_behind_the_delimiter(self):
        text = "first part\n[[ =cut= ]]\n" + "x" * 200

        chunk = self.chunk(text)

        self.assertEqual(chunk, "first part\n[[ =cut= ]]")
        self.assertFalse(self.chunker.End())

    def test_the_delimiter_comes_from_the_configuration(self):
        with config_values(config, CHUNK_DELIMITER="<<STOP>>"):
            chunk = self.chunk("first part\n<<STOP>>\n" + "x" * 200)

        self.assertTrue(chunk.endswith("<<STOP>>"))


class ParagraphTests(ChunkerTestCase):
    """Without a delimiter the cut goes to the next paragraph break."""

    def test_prefers_a_blank_line_after_the_chunk_size(self):
        head = "a" * (CHUNK_SIZE + 10)
        text = head + "\n\n\n" + "b" * 200

        chunk = self.chunk(text)

        self.assertTrue(chunk.startswith(head))
        self.assertTrue(chunk.endswith("\n\n\n"))
        self.assertNotIn("b", chunk)

    def test_falls_back_to_a_single_empty_line(self):
        head = "a" * (CHUNK_SIZE + 10)
        text = head + "\n\n" + "b" * 200

        chunk = self.chunk(text)

        self.assertTrue(chunk.startswith(head))
        self.assertNotIn("b", chunk)

    def test_cuts_behind_the_chunk_size_not_before_it(self):
        text = "a\n\n" + "b" * (CHUNK_SIZE + 10) + "\n\n" + "c" * 100

        chunk = self.chunk(text)

        # the empty line of the first line lies before CHUNK_SIZE and is
        # ignored, the AI gets whole paragraphs
        self.assertIn("b" * 10, chunk)

    def test_text_that_cannot_be_split_is_refused(self):
        with self.assertRaises(Exception):
            self.chunk("x" * 200)  # no paragraph break anywhere


class PreprocessFileTests(ChunkerTestCase):
    """The public entry point: write the chunk, shorten the input."""

    def test_saves_the_chunk_where_the_ai_preprocessor_looks_for_it(self):
        source = self.write("release_notes.txt",
                            "first part\n[[ =cut= ]]\n" + "x" * 200)

        with captured_stdout():
            self.chunker.preprocess_file(source)

        self.assertEqual(self.read("temp_chunk.txt"), "first part\n[[ =cut= ]]")

    def test_removes_the_consumed_part_from_the_input_file(self):
        rest = "x" * 200
        source = self.write("release_notes.txt", "first part\n[[ =cut= ]]" + rest)

        with captured_stdout():
            self.chunker.preprocess_file(source)

        self.assertEqual(self.read("release_notes.txt"), rest)

    def test_the_next_call_continues_behind_the_first_chunk(self):
        # every piece has to stay above 1.5 * CHUNK_SIZE, otherwise the rest
        # is short enough to be sent in one go
        source = self.write(
            "release_notes.txt",
            "a" * 60 + "[[ =cut= ]]" + "b" * 60 + "[[ =cut= ]]" + "c" * 60)

        with captured_stdout():
            first = self.chunker.preprocess_file(source)
            second = self.chunker.preprocess_file(source)
            third = self.chunker.preprocess_file(source)

        self.assertEqual(first, "a" * 60 + "[[ =cut= ]]")
        self.assertEqual(second, "b" * 60 + "[[ =cut= ]]")
        self.assertEqual(third, "c" * 60)
        self.assertTrue(self.chunker.End())
        self.assertEqual(self.read("release_notes.txt"), "")

    def test_a_missing_input_file_stops_the_run(self):
        with captured_stdout() as printed:
            with self.assertRaises(SystemExit) as exit_code:
                self.chunker.preprocess_file(self.path("not_there.txt"))

        self.assertEqual(exit_code.exception.code, 1)
        self.assertIn("not found", printed.getvalue())


class SliceInputTests(ChunkerTestCase):
    """Guard against consuming nothing and looping forever."""

    def test_refuses_to_slice_an_empty_piece(self):
        source = self.write("release_notes.txt", "content")
        self.chunker.slice_position = 0

        with self.assertRaises(Exception):
            self.chunker._slice_input(source)


if __name__ == "__main__":
    unittest.main()
