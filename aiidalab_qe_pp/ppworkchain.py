from aiida.plugins import WorkflowFactory
from aiida.engine import ToContext, WorkChain, if_
from aiida_quantumespresso.utils.mapping import prepare_process_inputs
from aiida import orm
from aiida.common import AttributeDict



PpCalculation = plugins.CalculationFactory("quantumespresso.pp")

class PPWorkChain(WorkChain):
    "WorkChain to compute vibrational property of a crystal."
    label = "pp"

    @classmethod
    def define(cls, spec):