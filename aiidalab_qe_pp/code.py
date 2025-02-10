from aiidalab_qe.common.code.model import CodeModel
from aiidalab_qe.common.panel import (
    PluginResourceSettingsModel,
    PluginResourceSettingsPanel,
)


class PpResourceSettingsModel(PluginResourceSettingsModel):
    """Resource settings for the pp calculations."""

    title = "Post-processing"
    identifier = "pp"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_models(
            {
                "pp": CodeModel(
                    name="pp.x",
                    description="pp.x",
                    default_calc_job_plugin="quantumespresso.pp",
                ),
                "critic2": CodeModel(
                    name="critic2",
                    description="critic2",
                    default_calc_job_plugin="critic2",
                ),
                "python": CodeModel(
                    name="python",
                    description="Python code for isosurface calculation",
                    default_calc_job_plugin="pythonjob.pythonjob",
                ),
            }
        )


class PpResourceSettingsPanel(PluginResourceSettingsPanel[PpResourceSettingsModel]):
    """Panel for the resource settings for the vibroscopy calculations."""

    title = "Post-processing"
