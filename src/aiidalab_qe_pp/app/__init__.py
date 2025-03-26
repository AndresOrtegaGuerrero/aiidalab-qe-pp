from aiidalab_qe.common.panel import PluginOutline

from aiidalab_qe_pp.app.code import PpResourceSettingsModel, PpResourceSettingsPanel


from aiidalab_qe_pp.app.workchain import workchain_and_builder
from aiidalab_qe_pp.app.model import PpConfigurationSettingsModel
from aiidalab_qe_pp.app.setting import PpConfigurationSettingPanel

from aiidalab_qe_pp.app.result.model import PpResultsModel
from aiidalab_qe_pp.app.result.result import PpResultsPanel


class PpPluginOutline(PluginOutline):
    title = "Post-processing (PP)"


pp = {
    "outline": PpPluginOutline,
    "configuration": {
        "panel": PpConfigurationSettingPanel,
        "model": PpConfigurationSettingsModel,
    },
    "resources": {
        "panel": PpResourceSettingsPanel,
        "model": PpResourceSettingsModel,
    },
    "result": {
        "panel": PpResultsPanel,
        "model": PpResultsModel,
    },
    "workchain": workchain_and_builder,
}
