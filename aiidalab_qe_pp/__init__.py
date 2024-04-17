from aiidalab_qe.common.panel import OutlinePanel
from aiidalab_widgets_base import ComputationalResourcesWidget

#from .result import Result
from .setting import Setting
#from .workchain import workchain_and_builder

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
    "setting": Setting,
    "code": {"pp": pp_code},
    #"result": Result,
    #"workchain": workchain_and_builder,
}