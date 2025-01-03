import traitlets as tl
from aiida import orm
from aiidalab_qe.common.panel import ConfigurationSettingsModel
from aiidalab_qe.common.mixins import HasInputStructure
from aiida_quantumespresso.workflows.pw.bands import PwBandsWorkChain
from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
from aiida_quantumespresso.calculations.pw import PwCalculation
from paramiko.ssh_exception import SSHException
from aiidalab_qe.plugins.bands.bands_workchain import BandsWorkChain
from aiida_wannier90_workflows.workflows import ProjwfcBandsWorkChain
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from aiida.common.exceptions import NotExistent


class PpConfigurationSettingsModel(ConfigurationSettingsModel, HasInputStructure):
    title = "Pp Settings"
    dependencies = [
        "input_structure",
    ]

    structure_selected = tl.Unicode("""<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
            Input structure is not set. Please set the structure first.
            </div>""")

    no_avail_cals = tl.Unicode("")

    pwcalc_type_options = tl.List(
        trait=tl.List(tl.Unicode()),
        default_value=[("Bands", "bands"), ("Nscf", "nscf")],
    )
    pwcalc_type = tl.Unicode("bands")

    pwcalc_avail_options = tl.List(
        trait=tl.List(tl.Union([tl.Unicode(), tl.Int()])), default_value=[]
    )
    pwcalc_avail = tl.Int(None, allow_none=True)

    calc_charge_dens = tl.Bool(False)
    calc_spin_dens = tl.Bool(False)
    calc_wfn = tl.Bool(False)
    calc_ildos = tl.Bool(False)
    calc_stm = tl.Bool(False)

    disable_calc_charge_dens = tl.Bool(False)
    disable_calc_spin_dens = tl.Bool(False)
    disable_calc_wfn = tl.Bool(False)
    disable_calc_ildos = tl.Bool(False)
    disable_calc_stm = tl.Bool(False)

    charge_dens = tl.Float(0)
    charge_dens_options = tl.List(
        trait=tl.List(tl.Union([tl.Unicode(), tl.Int()])),
        default_value=[
            ("Total charge", 0),
            ("Spin up", 1),
            ("Spin down", 2),
        ],
    )
    charge_dens_options_displayed = tl.Unicode("none")
    stm_options_displayed = tl.Unicode("none")
    ildos_options_displayed = tl.Unicode("none")
    ildos_spin_component_options_displayed = tl.Unicode("none")
    pwcalc_avail_displayed = tl.Unicode("block")

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

    bands_calc_lis = []
    nscf_calc_list = []

    current_calc_lsda = tl.Bool(False)
    current_calc_soc = tl.Bool(False)

    def fetch_data(self):
        self.bands_calc_list = self.get_available_pwcalcs(self.input_structure, "bands")
        self.nscf_calc_list = self.get_available_pwcalcs(self.input_structure, "nscf")

    def update_pwcalc_avail_options(self, _=None):
        """Update the available PW calculations based on the selected calculation type."""
        calc_list = (
            self.bands_calc_list if self.pwcalc_type == "bands" else self.nscf_calc_list
        )
        if calc_list:
            # Set available calculations and select the first one as default
            self.no_avail_cals = ""
            self.pwcalc_avail_options = calc_list
            self.pwcalc_avail = calc_list[0][1]
            self.on_pwcalc_avail_change()
            self.pwcalc_avail_displayed = "block"
        else:
            # Disable calculations and clear options if no calculations are available
            self.no_avail_cals = f"""<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
            No {self.pwcalc_type} calculations available for the selected structure. Please change the pw.x calculation type. If there are no calculations available please selected a different structure.
            </div>"""

            self.disable_all_calcs()
            self.pwcalc_avail_options = []
            self.pwcalc_avail = None
            self.pwcalc_avail_displayed = "none"

    def on_input_structure_change(self, _=None):
        if self.input_structure:
            self.structure_selected = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: green;">
            Structure selected PK: {}.
            </div>""".format(self.input_structure.pk)

            if self.input_structure.pbc == (True, True, True):
                self.calc_stm = False
                self.disable_calc_stm = True

    def on_pwcalc_avail_change(self, _=None):
        if not self.pwcalc_avail:
            return
        calc = orm.load_node(self.pwcalc_avail)
        self.current_calc_lsda = calc.outputs.output_parameters["lsda"]
        self.current_calc_soc = calc.outputs.output_parameters["spin_orbit_calculation"]
        self.enable_all_calcs()
        if self.current_calc_lsda:
            self.calc_spin_dens = False
            self.disable_calc_spin_dens = False
            self.charge_dens_options = [
                ("Total charge", 0),
                ("Spin up", 1),
                ("Spin down", 2),
            ]

        else:
            self.calc_spin_dens = False
            self.disable_calc_spin_dens = True
            self.charge_dens_options = [("Total charge", 0)]

        if self.current_calc_soc:
            self.calc_stm = False
            self.disable_calc_stm = True
        else:
            self.calc_stm = False
            if self.input_structure.pbc != (True, True, True):
                self.disable_calc_stm = False
            else:
                self.disable_calc_stm = True

    def _get_default(self, trait):
        return self._defaults.get(trait, self.traits()[trait].default_value)

    def on_change_calc_charge_dens(self, _=None):
        if self.calc_charge_dens:
            self.charge_dens_options_displayed = "block"
        else:
            self.charge_dens_options_displayed = "none"

    def on_change_calc_stm(self, _=None):
        if self.calc_stm:
            self.stm_options_displayed = "block"
        else:
            self.stm_options_displayed = "none"

    def on_change_calc_ildos(self, _=None):
        if self.calc_ildos:
            self.ildos_options_displayed = "block"
            if self.current_calc_lsda:
                self.ildos_spin_component_options_displayed = "block"
            else:
                self.ildos_spin_component_options_displayed = "none"
        else:
            self.ildos_options_displayed = "none"

    def disable_all_calcs(self):
        self.disable_calc_charge_dens = True
        self.disable_calc_spin_dens = True
        self.disable_calc_wfn = True
        self.disable_calc_ildos = True
        self.disable_calc_stm = True

    def enable_all_calcs(self):
        self.disable_calc_charge_dens = False
        self.disable_calc_spin_dens = False
        self.disable_calc_wfn = False
        self.disable_calc_ildos = False
        self.disable_calc_stm = False

    def get_available_pwcalcs(self, structure, wc_type):
        avail_list = []
        if wc_type == "bands":
            calc_list = (
                orm.QueryBuilder()
                .append(
                    (orm.StructureData, HubbardStructureData),
                    filters={"id": structure.pk},
                    tag="structure",
                )
                .append(
                    BandsWorkChain,
                    filters={
                        "attributes.exit_status": 0,
                    },
                    with_incoming="structure",
                    tag="bands_wc_qe",
                )
                .append(
                    (PwBandsWorkChain, ProjwfcBandsWorkChain),
                    filters={
                        "attributes.exit_status": 0,
                    },
                    with_incoming="bands_wc_qe",
                    tag="bands_wc",
                )
                .append(
                    PwBaseWorkChain,
                    filters={
                        "attributes.exit_status": 0,
                    },
                    with_incoming="bands_wc",
                    tag="base",
                )
                .append(
                    PwCalculation,
                    filters={
                        "attributes.exit_status": 0,
                    },
                    project=["*"],
                    with_incoming="base",
                    tag="calc",
                )
                .append(
                    orm.Dict,
                    filters={
                        "attributes.CONTROL.calculation": "bands",
                    },
                    with_outgoing="calc",
                )
                .all(flat=True)
            )

        elif wc_type == "nscf":
            calc_list = (
                orm.QueryBuilder()
                .append(
                    (orm.StructureData, HubbardStructureData),
                    filters={"id": structure.pk},
                    tag="structure",
                )
                .append(
                    PwBaseWorkChain,
                    filters={
                        "attributes.exit_status": 0,
                    },
                    with_incoming="structure",
                    tag="base",
                )
                .append(
                    PwCalculation,
                    filters={
                        "attributes.exit_status": 0,
                    },
                    project=["*"],
                    with_incoming="base",
                    tag="calc",
                )
                .append(
                    orm.Dict,
                    filters={
                        "attributes.CONTROL.calculation": "nscf",
                    },
                    with_outgoing="calc",
                )
                .all(flat=True)
            )

        for calc in calc_list:
            try:
                calc.outputs.remote_folder.listdir()
                description = "PK: {} LSDA: {} SOC: {} Computer: {}".format(
                    calc.pk,
                    calc.outputs.output_parameters["lsda"],
                    calc.outputs.output_parameters["spin_orbit_calculation"],
                    calc.computer.label,
                )

                avail_list.append((description, calc.pk))
            except OSError:
                # If OSError occurs, skip this iteration
                continue
            # Fix this in future
            except SSHException:
                continue
            # Skip calculations without necessary information
            except NotExistent:
                continue

        return avail_list
