"""Real LibreLane API checks; explicitly skipped outside the pinned environment."""
import importlib.util
import unittest

AVAILABLE = importlib.util.find_spec("librelane") is not None


@unittest.skipUnless(AVAILABLE, "Requires the pinned LibreLane environment; not an EDA pass")
class LivePluginTests(unittest.TestCase):
    def test_flow_registration(self):
        import librelane_plugin_phoenix
        from librelane.__version__ import __version__
        self.assertEqual(__version__, "3.0.14")
        from librelane.flows import Flow
        self.assertIs(Flow.factory.get("Phoenix.Classic"), librelane_plugin_phoenix.PhoenixClassic)

    def test_exactly_one_synthesis_replacement(self):
        from librelane_plugin_phoenix import PhoenixClassic, PhoenixSynthesis
        from librelane.steps.pyosys import Synthesis
        self.assertEqual(PhoenixClassic.Steps.count(PhoenixSynthesis), 1)
        self.assertNotIn(Synthesis, PhoenixClassic.Steps)
