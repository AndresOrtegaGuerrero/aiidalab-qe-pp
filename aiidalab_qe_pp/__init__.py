from aiidalab_qe.common.panel import OutlinePanel
from aiidalab_widgets_base import ComputationalResourcesWidget


from .result import Result
from aiidalab_qe_pp.setting import Setting
from aiidalab_qe_pp.workchain import workchain_and_builder


__version__ = "0.0.1"


class PpOutline(OutlinePanel):
    title = "Data analysis and plotting (PP)"
    help = """"""


pp_code = ComputationalResourcesWidget(
    description="pp.x",
    default_calc_job_plugin="quantumespresso.pp",
)


pp = {
    "outline": PpOutline,
    "code": {"pp": pp_code},
    "setting": Setting,
    "workchain": workchain_and_builder,
    "result": Result,
}