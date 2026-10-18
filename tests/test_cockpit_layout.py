"""Layout regression tests for the holographic web cockpit (index.html / style.css / app.js).

Pins the cockpit layout rules (project guidelines G-001..G-003):
  1. The TELEMETRY / Tactical Flight Log panel is anchored at the lower-right corner
     and carries a HIDE/SHOW button.
  2. The Chrono tick/time settings deck sits at the right upper corner, as the last
     block of the top status bar.
  3. The Commerce/Arsenal/Fleet terminal runs vertically (up to down) on the left
     side: a vertical tab rail with the active tab's content beside it.
The left-side radar and reactor move to the center column (radar first, reactor below).
"""

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent / "voidfarer" / "static"
INDEX_HTML = STATIC_DIR / "index.html"
STYLE_CSS = STATIC_DIR / "style.css"
APP_JS = STATIC_DIR / "app.js"

VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

TAB_BUTTON_IDS = (
    "tabBtnMarket",
    "tabBtnArsenal",
    "tabBtnFleet",
    "tabBtnContracts",
    "tabBtnMastery",
    "tabBtnStory",
    "tabBtnFactions",
)

TAB_CONTENT_IDS = (
    "tabContentMarket",
    "tabContentArsenal",
    "tabContentFleet",
    "tabContentContracts",
    "tabContentMastery",
    "tabContentStory",
    "tabContentFactions",
)


class _DomNode:
    """Minimal element tree node built from html.parser events."""

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self.parent = None

    def find_by_id(self, element_id):
        if self.attrs.get("id") == element_id:
            return self
        for child in self.children:
            found = child.find_by_id(element_id)
            if found is not None:
                return found
        return None

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def has_class(self, name):
        return name in (self.attrs.get("class") or "").split()


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _DomNode("document", {})
        self.stack = [self.root]

    def _append(self, tag, attrs, closing):
        node = _DomNode(tag, attrs)
        node.parent = self.stack[-1]
        self.stack[-1].children.append(node)
        if not closing and tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_starttag(self, tag, attrs):
        self._append(tag, attrs, closing=False)

    def handle_startendtag(self, tag, attrs):
        self._append(tag, attrs, closing=True)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return


class TestCockpitLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parser = _TreeBuilder()
        parser.feed(INDEX_HTML.read_text(encoding="utf-8"))
        parser.close()
        cls.dom = parser.root
        cls.css = STYLE_CSS.read_text(encoding="utf-8")
        cls.js = APP_JS.read_text(encoding="utf-8")

    def _rule_body(self, selector):
        match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", self.css)
        self.assertIsNotNone(match, f"missing CSS rule for {selector}")
        return match.group(1)

    def _ancestor_ids(self, node):
        return [ancestor.attrs.get("id") for ancestor in node.ancestors()]

    def _document_order(self):
        order = []

        def walk(node):
            node_id = node.attrs.get("id")
            if node_id:
                order.append(node_id)
            for child in node.children:
                walk(child)

        walk(self.dom)
        return order

    # --- Rule 1: telemetry log at the lower-right corner, with a hide button ---

    def test_telemetry_log_sits_in_the_lower_right_deck(self):
        log_panel = self.dom.find_by_id("logPanel")
        self.assertIsNotNone(log_panel, "telemetry log panel (#logPanel) missing from index.html")
        self.assertTrue(log_panel.has_class("log-panel"))
        self.assertIn("panelRight", self._ancestor_ids(log_panel),
                      "telemetry log must live in the lower-right deck (#panelRight)")
        self.assertIsNotNone(log_panel.find_by_id("flightLogStream"),
                             "flight log stream must be inside the log panel")

    def test_lower_right_deck_contains_only_the_telemetry_log(self):
        right_deck = self.dom.find_by_id("panelRight")
        self.assertIsNotNone(right_deck)
        child_ids = [child.attrs.get("id") for child in right_deck.children]
        self.assertEqual(child_ids, ["logPanel"],
                         "the lower-right deck must hold only the telemetry log")

    def test_lower_right_deck_anchors_its_content_to_the_bottom(self):
        deck_rule = self._rule_body(".panel-right")
        self.assertIn("flex-end", deck_rule,
                      "the right deck must pin its content to the bottom corner")

    def test_telemetry_log_carries_a_hide_button(self):
        log_panel = self.dom.find_by_id("logPanel")
        self.assertIsNotNone(log_panel)
        toggle = log_panel.find_by_id("btnToggleLog")
        self.assertIsNotNone(toggle, "telemetry log must carry a HIDE/SHOW button")

    def test_log_collapse_style_and_toggle_wiring_exist(self):
        self.assertRegex(self.css, r"\.log-panel\.log-collapsed[^{]*\{[^}]*display:\s*none")
        self.assertIn("btnToggleLog", self.js, "app.js must bind the log HIDE/SHOW button")
        self.assertIn("log-collapsed", self.js, "app.js must toggle the collapsed log class")

    # --- Rule 2: chrono deck pinned to the right upper corner ---

    def test_chrono_deck_is_the_last_block_of_the_top_bar(self):
        topbar = self.dom.find_by_id("hudTopBar")
        self.assertIsNotNone(topbar)
        self.assertTrue(topbar.children, "top bar must have content")
        last_child = topbar.children[-1]
        self.assertEqual(last_child.attrs.get("id"), "hudTimeDeck",
                         "the chrono/tick deck must sit at the far right of the top bar")
        self.assertTrue(last_child.has_class("hud-time-deck"))

    def test_chrono_deck_is_pushed_to_the_right_edge(self):
        deck_rule = self._rule_body(".hud-time-deck")
        self.assertIn("margin-left", deck_rule)
        self.assertIn("auto", deck_rule,
                      "the chrono deck must be pushed to the right edge of the top bar")

    # --- Rule 3: vertical Commerce/Arsenal/Fleet terminal on the left ---

    def test_terminal_lives_in_the_left_deck(self):
        left_deck = self.dom.find_by_id("panelLeft")
        self.assertIsNotNone(left_deck, "left terminal deck (#panelLeft) missing from index.html")
        self.assertTrue(left_deck.has_class("panel-left"))

        for tab_id in TAB_BUTTON_IDS:
            button = self.dom.find_by_id(tab_id)
            self.assertIsNotNone(button, f"missing tab button #{tab_id}")
            self.assertIn("panelLeft", self._ancestor_ids(button),
                          f"#{tab_id} must sit in the left terminal deck")

        for content_id in TAB_CONTENT_IDS:
            content = self.dom.find_by_id(content_id)
            self.assertIsNotNone(content, f"missing tab content #{content_id}")
            self.assertIn("panelLeft", self._ancestor_ids(content),
                          f"#{content_id} must sit in the left terminal deck")

    def test_terminal_uses_a_vertical_rail_beside_the_content(self):
        deck_rule = self._rule_body(".panel-left")
        self.assertIn("grid", deck_rule, "the left deck must lay the rail out beside the content")

        rail_rule = self._rule_body(".panel-left .deck-tabs-header")
        self.assertIn("column", rail_rule, "the tab rail must run vertically (up to down)")

    # --- Center column: radar above reactor ---

    def test_center_column_stacks_radar_above_reactor(self):
        order = self._document_order()
        self.assertIn("panelNav", order, "radar sub-panel (#panelNav) missing")
        self.assertIn("panelReactor", order, "reactor sub-panel (#panelReactor) missing")

        radar = self.dom.find_by_id("panelNav")
        reactor = self.dom.find_by_id("panelReactor")
        self.assertIn("panelCenter", self._ancestor_ids(radar),
                      "the radar must live in the center column")
        self.assertIn("panelCenter", self._ancestor_ids(reactor),
                      "the reactor must live in the center column")
        self.assertLess(order.index("panelNav"), order.index("panelReactor"),
                        "the radar must sit above the reactor")

    def test_context_alerts_live_in_the_center_column(self):
        for alert_id in ("combatCard", "anomalyCard"):
            alert = self.dom.find_by_id(alert_id)
            self.assertIsNotNone(alert, f"missing alert card #{alert_id}")
            self.assertIn("panelCenter", self._ancestor_ids(alert),
                          f"#{alert_id} must live in the center column")


if __name__ == "__main__":
    unittest.main()
