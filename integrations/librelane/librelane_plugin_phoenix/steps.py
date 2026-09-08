"""Pass-through plugin. It does not claim incremental synthesis or physical ECO."""
from pathlib import Path as LocalPath

from librelane.common import Path
from librelane.config import Variable
from librelane.flows import Flow
from librelane.flows.classic import Classic
from librelane.state import DesignFormat
from librelane.steps import Step
from librelane.steps.pyosys import Synthesis

from .contract import audited_command

IDENTITY = DesignFormat(
    "phoenix_synthesis_identity", "identity.json", "Phoenix synthesis runtime identity"
)
IDENTITY.register()


@Step.factory.register()
class PhoenixSynthesis(Synthesis):
    id = "Phoenix.Synthesis"
    name = "Audited Yosys synthesis"
    long_name = "Audited pass-through synthesis with the selected Yosys package"
    outputs = [*Synthesis.outputs, IDENTITY]
    config_vars = [
        *Synthesis.config_vars,
        Variable("PHOENIX_TOOLCHAIN_FILE", Path, "Explicit generated toolchain identity JSON"),
    ]

    def get_command(self, state_in):
        return audited_command(
            super().get_command(state_in),
            str(LocalPath(__file__).with_name("audit.py")),
            str(self.config["PHOENIX_TOOLCHAIN_FILE"]),
            str(LocalPath(self.step_dir) / "synthesis.identity.json"),
        )

    def run(self, state_in, **kwargs):
        views, metrics = super().run(state_in, **kwargs)
        report = LocalPath(self.step_dir) / "synthesis.identity.json"
        if not report.is_file():
            raise RuntimeError("Synthesis returned without an in-process identity audit")
        views[IDENTITY] = Path(str(report))
        metrics["phoenix__native_incremental_enabled"] = 0
        return views, metrics


@Flow.factory.register("Phoenix.Classic")
class PhoenixClassic(Classic):
    name = "Phoenix.Classic"
    Steps = [PhoenixSynthesis if step is Synthesis else step for step in Classic.Steps]
