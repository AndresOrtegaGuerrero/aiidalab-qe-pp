from aiidalab_qe.common.panel import ConfigurationSettingsModel

from aiidalab_qe.common.mixins import HasInputStructure
import traitlets as tl


class PpConfigurationSettingsModel(ConfigurationSettingsModel, HasInputStructure):
    dependencies = [
        "input_structure",
    ]

    structure_selected = tl.Unicode("""<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
            Input structure is not set. Please set the structure first.
            </div>""")
    calc_charge_dens = tl.Bool(False)
    calc_spin_dens = tl.Bool(False)
    calc_wfn = tl.Bool(False)
    calc_ildos = tl.Bool(False)
    calc_stm = tl.Bool(False)

    charge_dens_options = tl.List(
        trait=tl.List(tl.Union([tl.Unicode(), tl.Int()])),
        default_value=[
            ("Total charge", 0),
            ("Spin up", 1),
            ("Spin down", 2),
        ],
    )

    charge_dens = tl.Float(1)

    ildos_emin = tl.Float(0)
    ildos_emax = tl.Float(0)

    ildos_spin_component_options = tl.List(
        trait=tl.List(tl.Union([tl.Unicode(), tl.Int()])),
        default_value=[("Up + Down", 0), ("Up", 1), ("Down", 2)],
    )
    ilods_spin_component = tl.Float(0)

    stm_sample_bias = tl.Unicode("0.0")
    stm_heights = tl.Unicode("2.0")
    stm_currents = tl.Unicode("0.00005")

    def on_input_structure_change(self, _=None):
        if self.input_structure:
            self.structure_selected = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: green;">
            Structure set PK: {}.
            </div>""".format(self.input_structure.pk)
