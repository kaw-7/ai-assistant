# -*- coding: utf-8 -*-
"""``PolarionAssistant/Core`` - the parts that need no server.

``PolarionWorker.__init__`` connects to Polarion, so the tests call the
methods that do not touch ``self`` unbound, on fake work items.  A fake item
only has to offer what the code really uses: ``description.content``,
``title`` and ``save()``.
"""
from __future__ import annotations

import re
import unittest

from tests.support import captured_stdout

import PolarionAssistant.ValidReport.periodic_review_config as PRConf
from PolarionAssistant.Core.ItemUtil import ItemUtil
from PolarionAssistant.Core.PolarionWorker import PolarionWorker


class FakeText:
    def __init__(self, content):
        self.content = content


class FakeItem:
    """The bits of a Polarion work item the builders touch."""

    def __init__(self, title="", content=None, item_type=None):
        self.title = title
        self.description = FakeText(content) if content is not None else None
        self.type = item_type
        self.saved = 0

    def save(self):
        self.saved += 1


class FakeType:
    def __init__(self, type_id):
        self.id = type_id


class ModifyItemsTests(unittest.TestCase):
    """Replacing the tool name placeholder of a copied template."""

    @staticmethod
    def _modify(items, placeholder, substitute):
        # the method never touches self - call it unbound to skip the
        # connection made by PolarionWorker.__init__
        with captured_stdout():
            PolarionWorker._ModifyItems(None, items, placeholder, substitute)

    def test_replaces_the_placeholder_in_every_item(self):
        items = [FakeItem(content="Validation of [toolname] passed"),
                 FakeItem(content="[toolname] was tested")]

        self._modify(items, "[toolname]", "Axivion 7.4")

        self.assertEqual(items[0].description.content,
                         "Validation of Axivion 7.4 passed")
        self.assertEqual(items[1].description.content, "Axivion 7.4 was tested")

    def test_saves_every_item_it_touched(self):
        items = [FakeItem(content="[toolname]")]

        self._modify(items, "[toolname]", "Axivion 7.4")

        self.assertEqual(items[0].saved, 1)

    def test_replaces_all_occurrences_inside_one_item(self):
        items = [FakeItem(content="[toolname] and [toolname]")]

        self._modify(items, "[toolname]", "X")

        self.assertEqual(items[0].description.content, "X and X")

    def test_an_item_without_a_description_is_skipped(self):
        empty = FakeItem(content=None)
        blank = FakeItem(content="text")
        blank.description.content = None

        self._modify([empty, blank], "[toolname]", "X")

        self.assertEqual(empty.saved, 0)
        self.assertEqual(blank.saved, 0)

    def test_an_item_without_the_placeholder_is_left_unchanged(self):
        items = [FakeItem(content="nothing to replace")]

        self._modify(items, "[toolname]", "X")

        self.assertEqual(items[0].description.content, "nothing to replace")

    def test_a_compiled_pattern_replaces_every_match(self):
        items = [FakeItem(content="<b>[toolname]</b> and <i>[Tool Name]</i>")]

        self._modify(items, re.compile(r"\[tool ?name\]", re.IGNORECASE), "X")

        self.assertEqual(items[0].description.content, "<b>X</b> and <i>X</i>")

    def test_a_pattern_substitute_is_taken_literally(self):
        # a backslash in the tool name must not be read as a group reference
        items = [FakeItem(content="[toolname]")]

        self._modify(items, re.compile(r"\[toolname\]"), r"C:\tools\1")

        self.assertEqual(items[0].description.content, r"C:\tools\1")

    def test_the_periodic_review_placeholder_matches_the_template_span(self):
        items = [FakeItem(content='Tool: <span style="color: #FF0000;">[toolname]</span>.'),
                 FakeItem(content='<span style="color:#f00;">[Tool Name]</span>'),
                 FakeItem(content='<span style="color: #FF0000;">other</span>')]

        self._modify(items, PRConf.PLACEHOLDER, "Axivion 7.4")

        self.assertEqual(items[0].description.content, "Tool: Axivion 7.4.")
        self.assertEqual(items[1].description.content, "Axivion 7.4")
        self.assertEqual(items[2].description.content,
                         '<span style="color: #FF0000;">other</span>')


class FakeDocument:
    def __init__(self, items, raising=False):
        self._items = items
        self._raising = raising

    def getWorkitems(self):
        if self._raising:
            raise RuntimeError("the server said no")
        return self._items


class FindHeadingItemByNameTests(unittest.TestCase):
    """Looking the target heading of the import up in a document."""

    def test_finds_the_item_carrying_the_heading(self):
        wanted = FakeItem(title="Known Issues")
        document = FakeDocument([FakeItem(title="Introduction"), wanted])

        self.assertIs(ItemUtil.find_heading_item_by_name(document,
                                                         "Known Issues"),
                      wanted)

    def test_returns_nothing_when_the_heading_is_missing(self):
        document = FakeDocument([FakeItem(title="Introduction")])

        with captured_stdout() as printed:
            found = ItemUtil.find_heading_item_by_name(document, "Known Issues")

        self.assertIsNone(found)
        self.assertIn("Known Issues", printed.getvalue())

    def test_the_search_is_exact(self):
        document = FakeDocument([FakeItem(title="Known Issues of the tool")])

        with captured_stdout():
            found = ItemUtil.find_heading_item_by_name(document, "Known Issues")

        self.assertIsNone(found)

    def test_a_failing_server_call_is_reported_instead_of_raising(self):
        document = FakeDocument([], raising=True)

        with captured_stdout() as printed:
            found = ItemUtil.find_heading_item_by_name(document, "Known Issues")

        self.assertIsNone(found)
        self.assertIn("the server said no", printed.getvalue())


if __name__ == "__main__":
    unittest.main()
