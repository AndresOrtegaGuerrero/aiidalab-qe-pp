from aiidalab_qe.common.panel import PluginOutline

from aiidalab_qe_pp.code import PpResourceSettingsModel, PpResourceSettingsPanel


from aiidalab_qe_pp.workchain import workchain_and_builder
from aiidalab_qe_pp.model import PpConfigurationSettingsModel
from aiidalab_qe_pp.setting import PpConfigurationSettingPanel

from aiidalab_qe_pp.result.model import PpResultsModel
from aiidalab_qe_pp.result.result import PpResultsPanel


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
    "results": {
        "panel": PpResultsPanel,
        "model": PpResultsModel,
    },
    "workchain": workchain_and_builder,
}
