from aiidalab_qe.common.panel import PluginOutline

from aiidalab_qe_pp.code import PpResourceSettingsModel, PpResourceSettingsPanel


from aiidalab_qe_pp.workchain import workchain_and_builder
from aiidalab_qe_pp.model import PpConfigurationSettingsModel
from aiidalab_qe_pp.setting import PpConfigurationSettingPanel


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
    "workchain": workchain_and_builder,
}
