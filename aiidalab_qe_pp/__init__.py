from aiidalab_qe.common.panel import OutlinePanel
from aiidalab_qe.common.widgets import QEAppComputationalResourcesWidget


from .result import Result
from aiidalab_qe_pp.setting import Setting
from aiidalab_qe_pp.workchain import workchain_and_builder


__version__ = "0.0.1"


class PpOutline(OutlinePanel):
    title = "Data analysis and plotting (PP)"
    help = """"""


pp_code = QEAppComputationalResourcesWidget(
    description="pp.x",
    default_calc_job_plugin="quantumespresso.pp",
)

critic2_code = QEAppComputationalResourcesWidget(
    description="critic2",
    default_calc_job_plugin="critic2",
)

pp = {
    "outline": PpOutline,
    "code": {"pp": pp_code, "critic2": critic2_code},
    "setting": Setting,
    "workchain": workchain_and_builder,
    "result": Result,
}
