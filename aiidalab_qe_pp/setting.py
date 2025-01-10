"""
This module contains the settings for the pp plugin in the AiiDAlab Quantum ESPRESSO (QE) plugin.
"""

import ipywidgets as ipw

from aiidalab_qe.common.panel import ConfigurationSettingsPanel
from .model import PpConfigurationSettingsModel
from .widgets import OrbitalListWidget, OrbitalSelectionWidget

# import traitlets as tl
# from aiidalab_qe.common.panel import Panel
# from aiida import orm
# from .widgets import PwCalcListWidget, KpointInfoWidget
# from IPython.display import clear_output, display


class PpConfigurationSettingPanel(
    ConfigurationSettingsPanel[PpConfigurationSettingsModel],
):
    title = "Pp Settings"
    identifier = "pp"

    def __init__(self, model: PpConfigurationSettingsModel, **kwargs):
        super().__init__(model, **kwargs)

        self._model.observe(
            self._on_input_structure_change,
            "input_structure",
        )

    def render(self):
        if self.rendered:
            return

        self.pwcalc_description = ipw.HTML(
            """
            <div style="line-height: 1.4; padding-bottom: 10px;">
                To run post-processing calculations, select a previous calculation (Band structure or Electronic projected density of states) where the chosen structure was used as input.
                The widget below lists all available calculations for the selected structure.
                Choose the type of calculation (Bands or NSCF) and then select the specific calculation you want to use.

                <h5>Note:</h5>
                <p>Be cautious with the "Delete work directory" option in Advanced Settings, as it will remove the associated files permanently.</p>
            </div>
            """,
            # layout=ipw.Layout(max_width="100%"),
        )

        self.comp_description = ipw.HTML(
            """
            <div style="line-height: 1.4; padding-bottom: 10px;">
                <h5>Note:</h5>
                <p>When selecting a PwCalculation, ensure you choose the same computer in Step 3.0 (Computational resources).
                The required files for post-processing calculations are stored on that computer.</p>
            </div>
            """,
            # layout=ipw.Layout(max_width="100%"),
        )

        # Structured selected HTML
        self.structure_selected = ipw.HTML()
        ipw.link(
            (self._model, "structure_selected"),
            (self.structure_selected, "value"),
        )
        self.calc_options_help = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
            <h5>Please select the different calculations options:</h5>
            </div>"""
        )

        # STM help
        self.calc_stm_help = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
            Write the list of parameters (Bias , Heights and Currents) to compute separated by a space. For example: 0.0 0.1 0.2
            </div>"""
        )

        # PwCalcList Widget

        # PwCalculation Type
        self.pwcalc_type = ipw.Dropdown(
            description="Select the pw.x type to use:",
            disabled=False,
            layout=ipw.Layout(width="fit-content"),
            style={"description_width": "initial"},
        )
        ipw.dlink(
            (self._model, "pwcalc_type_options"),
            (self.pwcalc_type, "options"),
        )
        ipw.link(
            (self._model, "pwcalc_type"),
            (self.pwcalc_type, "value"),
        )
        self.pwcalc_type.observe(
            self._model.update_pwcalc_avail_options,
            "value",
        )
        # PwCalculation Available
        self.pwcalc_avail = ipw.Dropdown(
            description="PwCalculation available:",
            style={"description_width": "initial"},
            layout=ipw.Layout(width="fit-content", display="block"),
        )
        ipw.dlink(
            (self._model, "pwcalc_avail_options"),
            (self.pwcalc_avail, "options"),
        )
        ipw.link(
            (self._model, "pwcalc_avail"),
            (self.pwcalc_avail, "value"),
        )
        ipw.link(
            (self._model, "pwcalc_avail_displayed"),
            (self.pwcalc_avail.layout, "display"),
        )
        self.pwcalc_avail.observe(
            self._model.on_pwcalc_avail_change,
            "value",
        )

        # No available calculations HTML
        self.no_avail_cals = ipw.HTML()
        ipw.link(
            (self._model, "no_avail_cals"),
            (self.no_avail_cals, "value"),
        )

        # Calculation options

        # Charge Density Calculation
        self.calc_charge_dens = ipw.Checkbox(
            description="Charge Density",
            indent=False,
            style={"description_width": "initial"},
        )
        ipw.link((self._model, "calc_charge_dens"), (self.calc_charge_dens, "value"))
        ipw.link(
            (self._model, "disable_calc_charge_dens"),
            (self.calc_charge_dens, "disabled"),
        )
        self.calc_charge_dens.observe(
            self._on_change_calc_charge_dens,
            "value",
        )

        # Spin Density Calculation
        self.calc_spin_dens = ipw.Checkbox(
            description="Spin Density",
            indent=False,
            style={"description_width": "initial"},
        )
        ipw.link((self._model, "calc_spin_dens"), (self.calc_spin_dens, "value"))
        ipw.link(
            (self._model, "disable_calc_spin_dens"), (self.calc_spin_dens, "disabled")
        )

        # Kohn Sham Orbitals Calculation
        self.calc_wfn = ipw.Checkbox(
            description="Kohn Sham Orbitals",
            indent=False,
            style={"description_width": "initial"},
        )
        ipw.link((self._model, "calc_wfn"), (self.calc_wfn, "value"))
        ipw.link((self._model, "disable_calc_wfn"), (self.calc_wfn, "disabled"))

        self.calc_wfn.observe(
            self._on_change_calc_wfn,
            "value",
        )

        # Integrated Local Density of States Calculation
        self.calc_ildos = ipw.Checkbox(
            description="Integrated Local Density of States",
            indent=False,
            style={"description_width": "initial"},
        )
        ipw.link((self._model, "calc_ildos"), (self.calc_ildos, "value"))
        ipw.link((self._model, "disable_calc_ildos"), (self.calc_ildos, "disabled"))
        self.calc_ildos.observe(
            self._on_change_calc_ildos,
            "value",
        )

        # STM Plots Calculation
        self.calc_stm = ipw.Checkbox(
            description="STM Plots",
            indent=False,
            style={"description_width": "initial"},
        )
        ipw.link((self._model, "calc_stm"), (self.calc_stm, "value"))
        ipw.link((self._model, "disable_calc_stm"), (self.calc_stm, "disabled"))
        self.calc_stm.observe(
            self._on_change_calc_stm,
            "value",
        )

        # Calc Charge Density Options
        self.charge_dens_options = ipw.Dropdown(
            description="Options:",
            disabled=False,
        )
        ipw.dlink(
            (self._model, "charge_dens_options"),
            (self.charge_dens_options, "options"),
        )
        ipw.link(
            (self._model, "charge_dens"),
            (self.charge_dens_options, "value"),
        )
        ipw.link(
            (self._model, "charge_dens_options_displayed"),
            (self.charge_dens_options.layout, "display"),
        )

        # Calc Kohn Sham Orbitals Options

        self.kbands_info = ipw.HTML()
        ipw.link(
            (self._model, "kbands_info"),
            (self.kbands_info, "value"),
        )
        self.kpoints_table = ipw.HTML()
        ipw.link(
            (self._model, "kpoints_table"),
            (self.kpoints_table, "value"),
        )
        self.kpoints_table_box = ipw.Box(
            children=[self.kpoints_table],
            layout=ipw.Layout(
                overflow="auto",
                height="300px",
                width="300px",
            ),
        )

        self.sel_orbital = OrbitalListWidget(
            item_class=OrbitalSelectionWidget, add_button_text="Add Orbital"
        )
        ipw.link(
            (self._model, "sel_orbital"),
            (self.sel_orbital, "orbitals"),
        )
        self.wfn_options_help = ipw.HTML(
            """<div style="line-height: 140%; padding-bottom: 5px">
            Click <span style="color: #2196f3;"> <b>Add orbital</b> </span> to select the orbitals (Bands) for plotting at a specific k-point.
            To add orbitals for additional k-points, use the <span style="color: #2196f3;"> <b>Add orbital</b> </span>  button again. The table displays the total number of k-points in your calculation.
            For LSDA calculations, both spin components are automatically computed.
            </div>"""
        )
        self.lsign = ipw.Checkbox(
            description="Plot |ψ|² sign(ψ) if k-point is Γ [0.0, 0.0, 0.0]",
            indent=True,
            style={"description_width": "initial"},
        )
        ipw.link((self._model, "lsign"), (self.lsign, "value"))
        self.wfn_options = ipw.VBox(
            [
                self.wfn_options_help,
                self.lsign,
                self.kbands_info,
                self.kpoints_table_box,
                self.sel_orbital,
            ]
        )

        ipw.link(
            (self._model, "wfn_options_displayed"),
            (self.wfn_options.layout, "display"),
        )

        # Calc ILDOS Options
        self.ildos_emin = ipw.FloatText(
            description="Emin (eV):",
            style={"description_width": "initial"},
            layout=ipw.Layout(width="fit-content"),
        )
        ipw.link((self._model, "ildos_emin"), (self.ildos_emin, "value"))
        self.ildos_emax = ipw.FloatText(
            description="Emax (eV):",
            style={"description_width": "initial"},
            layout=ipw.Layout(width="fit-content"),
        )
        ipw.link((self._model, "ildos_emax"), (self.ildos_emax, "value"))

        self.ildos_spin_component = ipw.Dropdown(
            description="Spin component:",
            style={"description_width": "initial"},
        )
        ipw.dlink(
            (self._model, "ildos_spin_component_options"),
            (self.ildos_spin_component, "options"),
        )
        ipw.link(
            (self._model, "ildos_spin_component"),
            (self.ildos_spin_component, "value"),
        )
        ipw.link(
            (self._model, "ildos_spin_component_options_displayed"),
            (self.ildos_spin_component.layout, "display"),
        )
        self.ildos_parameters_help = ipw.HTML(
            """<div style="line-height: 140%; padding-bottom: 5px">
            Select the energy range and spin component (LSDA) for the integrated local density of states calculation.
            </div>"""
        )

        self.ildos_parameters = ipw.VBox(
            [
                self.ildos_parameters_help,
                ipw.HBox(
                    [
                        self.ildos_emin,
                        self.ildos_emax,
                        self.ildos_spin_component,
                    ]
                ),
            ]
        )
        ipw.link(
            (self._model, "ildos_options_displayed"),
            (self.ildos_parameters.layout, "display"),
        )

        # Calc STM Options
        self.stm_sample_bias = ipw.Text(
            description="Sample bias List (eV):",
            disabled=False,
            style={"description_width": "initial"},
        )
        ipw.link((self._model, "stm_sample_bias"), (self.stm_sample_bias, "value"))
        self.stm_heights = ipw.Text(
            description="Heights List (Å): ",
            disabled=False,
            style={"description_width": "initial"},
        )
        ipw.link((self._model, "stm_heights"), (self.stm_heights, "value"))
        self.stm_currents = ipw.Text(
            description="Currents List (a.u): ",
            disabled=False,
            style={"description_width": "initial"},
            placeholder="arbitrary units",
        )
        ipw.link((self._model, "stm_currents"), (self.stm_currents, "value"))
        self.stm_parameters = ipw.VBox(
            [
                self.calc_stm_help,
                ipw.HBox(
                    [
                        self.stm_sample_bias,
                        self.stm_heights,
                        self.stm_currents,
                    ]
                ),
            ]
        )

        ipw.link(
            (self._model, "stm_options_displayed"),
            (self.stm_parameters.layout, "display"),
        )

        self.children = [
            self.structure_selected,
            self.pwcalc_description,
            self.comp_description,
            self.pwcalc_type,
            self.no_avail_cals,
            self.pwcalc_avail,
            self.calc_options_help,
            self.calc_charge_dens,
            self.charge_dens_options,
            self.calc_spin_dens,
            self.calc_wfn,
            self.wfn_options,
            self.calc_ildos,
            self.ildos_parameters,
            self.calc_stm,
            self.stm_parameters,
        ]
        self.rendered = True
        self._initial_view()

    def _initial_view(self):
        self._get_data()
        self._model.update_pwcalc_avail_options()

    def _on_input_structure_change(self, _):
        self.refresh(specific="structure")
        self._model.on_input_structure_change()

    def _get_data(self):
        self._model.fetch_data()

    def _update_pwcalc_avail_options(self, _):
        self._model.update_pwcalc_avail_options()

    def _on_pwcalc_avail_change(self, _):
        self._model.on_pwcalc_avail_change()

    def _on_change_calc_charge_dens(self, _):
        self._model.on_change_calc_charge_dens()

    def _on_change_calc_stm(self, _):
        self._model.on_change_calc_stm()

    def _on_change_calc_ildos(self, _):
        self._model.on_change_calc_ildos()

    def _on_change_calc_wfn(self, _):
        self._model.on_change_calc_wfn()
