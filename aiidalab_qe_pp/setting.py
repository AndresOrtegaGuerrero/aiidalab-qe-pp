"""
This module contains the settings for the pp plugin in the AiiDAlab Quantum ESPRESSO (QE) plugin.
"""

import ipywidgets as ipw

from aiidalab_qe.common.panel import ConfigurationSettingsPanel
from .model import PpConfigurationSettingsModel


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

        self._default_pwcalc_list_helper_text = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
            Input structure is not set. Please set the structure first.
            </div>"""

        self.pwcalc_description = ipw.HTML(
            """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px">
            Please choose the wavefunction source: either from a previous Bands or Nscf calculation linked
            to your structure.
            <h5>Be careful with the clean-up the work directory option in the Advanced Settings.</h5>
            </div>""",
            layout=ipw.Layout(max_width="100%"),
        )

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
        # Calculation options
        self.calc_charge_dens = ipw.Checkbox(
            description="Charge Density", layout={"width": "initial"}
        )
        ipw.link((self._model, "calc_charge_dens"), (self.calc_charge_dens, "value"))

        self.calc_spin_dens = ipw.Checkbox(
            description="Spin Density", layout={"width": "initial"}
        )
        ipw.link((self._model, "calc_spin_dens"), (self.calc_spin_dens, "value"))
        self.calc_wfn = ipw.Checkbox(
            description="Kohn Sham Orbitals", layout={"width": "initial"}
        )
        ipw.link((self._model, "calc_wfn"), (self.calc_wfn, "value"))
        self.calc_ildos = ipw.Checkbox(
            description="Integrated Local Density of States",
            layout={"width": "initial"},
        )
        ipw.link((self._model, "calc_ildos"), (self.calc_ildos, "value"))
        self.calc_stm = ipw.Checkbox(
            description="STM Plots", layout={"width": "initial"}
        )
        ipw.link((self._model, "calc_stm"), (self.calc_stm, "value"))

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

        # Calc ILDOS Options
        self.ildos_emin = ipw.FloatText(
            description="Emin (eV):",
            disabled=False,
        )
        ipw.link((self._model, "ildos_emin"), (self.ildos_emin, "value"))
        self.ildos_emax = ipw.FloatText(
            description="Emax (eV):",
            disabled=False,
        )
        ipw.link((self._model, "ildos_emax"), (self.ildos_emax, "value"))

        self.ildos_spin_component = ipw.Dropdown(
            description="Spin component:",
            disabled=False,
            layout={"description_width": "initial"},
        )
        ipw.dlink(
            (self._model, "ildos_spin_component_options"),
            (self.ildos_spin_component, "options"),
        )
        ipw.link(
            (self._model, "ilods_spin_component"),
            (self.ildos_spin_component, "value"),
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
        self.stm_parameters = ipw.HBox(
            [self.stm_sample_bias, self.stm_heights, self.stm_currents]
        )

        self.children = [
            self.structure_selected,
            self.pwcalc_description,
            self.calc_options_help,
            self.calc_charge_dens,
            self.charge_dens_options,
            self.calc_spin_dens,
            self.calc_wfn,
            self.calc_ildos,
            self.ildos_emin,
            self.ildos_emax,
            self.ildos_spin_component,
            self.calc_stm,
            self.stm_parameters,
        ]

    def _on_input_structure_change(self, _):
        self.refresh(specific="structure")
        self._model.on_input_structure_change()


# class Setting(Panel):
#     title = "PP Settings"
#     identifier = "pp"

#     input_structure = tl.Instance(orm.StructureData, allow_none=True)

#     no_avail_cals = tl.Bool(False)

#     def __init__(self, **kwargs):
#         self.settings_title = ipw.HTML(
#             """<div style="padding-top: 0px; padding-bottom: 0px">
#             <h4>Settings</h4></div>"""
#         )
#         self.calc_options_help = ipw.HTML(
#             """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
#             <h5>Please select the different calculations options:</h5>
#             </div>"""
#         )
#         self.calc_stm_help = ipw.HTML(
#             """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
#             Write the list of parameters (Bias , Heights and Currents) to compute separated by a space. For example: 0.0 0.1 0.2
#             </div>"""
#         )
#         # PwCalcList Widget

#         self.pwcalc_list = PwCalcListWidget(structure=self.input_structure)
#         ipw.dlink(
#             (self.pwcalc_list, "no_avail_cals"),
#             (self, "no_avail_cals"),
#         )
#         # Calculation options
#         self.calc_charge_dens = ipw.Checkbox(
#             description="Charge Density", value=False, layout={"width": "initial"}
#         )
#         self.calc_spin_dens = ipw.Checkbox(
#             description="Spin Density", value=False, layout={"width": "initial"}
#         )
#         self.calc_wfn = ipw.Checkbox(
#             description="Kohn Sham Orbitals", value=False, layout={"width": "initial"}
#         )
#         self.calc_ildos = ipw.Checkbox(
#             description="Integrated Local Density of States",
#             value=False,
#             layout={"width": "initial"},
#         )
#         self.calc_stm = ipw.Checkbox(description="STM Plots", value=False)

#         # Calc Charge Density Options
#         self.charge_dens_options = ipw.Dropdown(
#             options=[("Total charge", 0), ("Spin up", 1), ("Spin down", 2)],
#             value=1,
#             description="Options:",
#             disabled=False,
#         )
#         # Output Charge Density Output
#         self.charge_dens_output = ipw.Output()

#         # Calc Kohn Sham Orbitals Options
#         self.kpoints_info = KpointInfoWidget()
#         # self.sel_orbital = OrbitalListWidget(item_class=OrbitalSelectionWidget, add_button_text="Add Orbital")

#         # Calc ILDOS Options
#         self.ildos_emin = ipw.FloatText(
#             value=0.0,
#             description="Emin (eV):",
#             disabled=False,
#             layout={"width": "initial"},
#         )
#         self.ildos_emax = ipw.FloatText(
#             value=0.0,
#             description="Emax (eV):",
#             disabled=False,
#             layout={"width": "initial"},
#         )
#         self.ildos_spin_component = ipw.Dropdown(
#             options=[("Up + Down", 0), ("Up", 1), ("Down", 2)],
#             value=0,
#             description="Spin component:",
#             disabled=False,
#             layout={"width": "initial"},
#         )
#         self.ildos_spin_com_output = ipw.Output()
#         self.ildos_options = ipw.HBox(
#             [self.ildos_emin, self.ildos_emax, self.ildos_spin_com_output]
#         )

#         # Output Kohn Sham Orbitals
#         self.wfn_output = ipw.Output()
#         self.kpoints_info_output = ipw.Output()

#         # Output ILDOS Output
#         self.ildos_output = ipw.Output()

#         # Calc STM Options
#         self.stm_sample_bias = ipw.Text(
#             value="0.0",
#             description="Sample bias List (eV):",
#             disabled=False,
#             style={"description_width": "initial"},
#         )
#         self.stm_heights = ipw.Text(
#             value="2.0",
#             description="Heights List (Å): ",
#             disabled=False,
#             style={"description_width": "initial"},
#         )
#         self.stm_currents = ipw.Text(
#             value="0.00005",
#             description="Currents List (a.u): ",
#             disabled=False,
#             style={"description_width": "initial"},
#             placeholder="arbitrary units",
#         )
#         self.stm_parameters = ipw.HBox(
#             [self.stm_sample_bias, self.stm_heights, self.stm_currents]
#         )
#         self.stm_options = ipw.VBox([self.calc_stm_help, self.stm_parameters])
#         # Output STM Output
#         self.stm_output = ipw.Output()

#         # Set up observers for each widget
#         self.calc_charge_dens.observe(
#             self._display_widget_options(
#                 self.charge_dens_output, self.charge_dens_options
#             ),
#             names="value",
#         )
#         # self.calc_wfn.observe(self._display_widget_options(self.wfn_output, self.sel_orbital), names='value')
#         self.calc_wfn.observe(
#             self._display_widget_options(self.kpoints_info_output, self.kpoints_info),
#             names="value",
#         )
#         self.calc_ildos.observe(
#             self._display_widget_options(self.ildos_output, self.ildos_options),
#             names="value",
#         )
#         self.calc_stm.observe(
#             self._display_widget_options(self.stm_output, self.stm_options),
#             names="value",
#         )

#         self.pwcalc_list.pwcalc_avail.observe(self._update_calc_options, names="value")
#         self.pwcalc_list.pwcalc_type.observe(
#             self._update_calc_type_options, names="value"
#         )
#         self.pwcalc_list.wc_type.observe(self._update_wc_options, names="value")

#         self.children = [
#             self.settings_title,
#             self.pwcalc_list,
#             self.calc_options_help,
#             self.calc_charge_dens,
#             self.charge_dens_output,
#             self.calc_spin_dens,
#             self.calc_wfn,
#             self.kpoints_info_output,
#             self.wfn_output,
#             self.calc_ildos,
#             self.ildos_output,
#             self.calc_stm,
#             self.stm_output,
#         ]
#         super().__init__(**kwargs)

#     # Display the output widget associated with each calculation option
#     def _display_widget_options(self, output_widget, display_widget):
#         def _display(change):
#             with output_widget:
#                 clear_output()
#                 if change["new"]:
#                     display(display_widget)

#         return _display

#     @tl.observe("input_structure")
#     def _structure_change(self, change):
#         self.pwcalc_list.structure = change["new"]

#     def set_charge_dens_options(self, lsda):
#         if not lsda:
#             self.charge_dens_options.options = [("Total charge", 0)]
#         else:
#             self.charge_dens_options.options = [
#                 ("Total charge", 0),
#                 ("Spin up", 1),
#                 ("Spin down", 2),
#             ]

#     @tl.observe("no_avail_cals")
#     def _no_avail_cals_change(self, change):
#         if change["new"]:
#             self._reset_calc_values()
#             self.calc_charge_dens.disabled = True
#             self.calc_spin_dens.disabled = True
#             self.calc_wfn.disabled = True
#             self.calc_ildos.disabled = True
#             self.calc_stm.disabled = True
#         else:
#             self.calc_charge_dens.disabled = False
#             self.calc_wfn.disabled = False
#             self.calc_ildos.disabled = False
#             self._update_calc_options({"new": self.pwcalc_list.pwcalc_avail.value})

#     def _reset_calc_values(self):
#         self.calc_charge_dens.value = False
#         self.calc_spin_dens.value = False
#         self.calc_wfn.value = False
#         self.calc_ildos.value = False
#         self.calc_stm.value = False

#     def _reset_calc_options(self):
#         self._reset_calc_values()
#         self.calc_spin_dens.disabled = False
#         self.calc_stm.disabled = False
#         self.set_charge_dens_options(False)
#         self.kpoints_info.reset()

#     def _update_wc_options(self, change):
#         if change["new"] == "scratch":
#             self._reset_calc_options()
#         else:
#             self._update_calc_options({"new": self.pwcalc_list.pwcalc_avail.value})

#     def _update_calc_type_options(self, change):
#         if self.pwcalc_list.pwcalc_avail.options:
#             self._update_calc_options({"new": self.pwcalc_list.pwcalc_avail.value})

#     def _update_calc_options(self, change):
#         if self.pwcalc_list.pwcalc_avail.options:
#             pw_calc = orm.load_node(change["new"])
#             self.calc_spin_dens.disabled = not pw_calc.outputs.output_parameters["lsda"]
#             if pw_calc.outputs.output_parameters["lsda"]:
#                 self._display_widget_options(
#                     self.ildos_spin_com_output, self.ildos_spin_component
#                 )({"new": True})
#             else:
#                 self.ildos_spin_com_output.value = 0
#                 self.ildos_spin_com_output.clear_output()

#             if not pw_calc.outputs.output_parameters[
#                 "spin_orbit_calculation"
#             ] and self.input_structure.pbc != (True, True, True):
#                 self.calc_stm.disabled = False
#             else:
#                 self.calc_stm.disabled = True
#             self.set_charge_dens_options(pw_calc.outputs.output_parameters["lsda"])
#             self.kpoints_info.update(
#                 pw_calc
#             )  # Add a trailet so it triggers the change in the constructor

#         else:
#             self._reset_calc_options()

#     def get_value(self, attribute):
#         """Safely get the value of an attribute if it exists, else return the attribute itself."""
#         if hasattr(attribute, "value"):
#             return attribute.value
#         if hasattr(attribute, "orbitals"):
#             return attribute.orbitals
#         return attribute

#     def get_panel_value(self):
#         pw_calc = orm.load_node(self.pwcalc_list.pwcalc_avail.value)
#         lsda = pw_calc.outputs.output_parameters["lsda"]
#         return {
#             "calc_charge_dens": self.get_value(self.calc_charge_dens),
#             "calc_spin_dens": self.get_value(self.calc_spin_dens),
#             "calc_wfn": self.get_value(self.calc_wfn),
#             "calc_ildos": self.get_value(self.calc_ildos),
#             "calc_stm": self.get_value(self.calc_stm),
#             "charge_dens_options": self.get_value(self.charge_dens_options),
#             "sel_orbital": self.kpoints_info.sel_orbital.orbitals,
#             "ildos_emin": self.get_value(self.ildos_emin),
#             "ildos_emax": self.get_value(self.ildos_emax),
#             "ildos_spin_component": self.get_value(self.ildos_spin_component),
#             "stm_sample_bias": self.get_value(self.stm_sample_bias),
#             "stm_heights": self.get_value(self.stm_heights),
#             "stm_currents": self.get_value(self.stm_currents),
#             "pwcalc_avail": self.get_value(self.pwcalc_list.pwcalc_avail),
#             "pwcalc_type": self.get_value(self.pwcalc_list.pwcalc_type),
#             "structure_pk": self.input_structure.pk,
#             "lsda": lsda,
#         }

#     def reset(self):
#         self._reset_calc_options()
#         self.pwcalc_list._reset()

#     def set_panel_value(self, input_dict):
#         #     """ Load a dictionary of the input parameters for the plugin. """
#         self.pwcalc_list.pwcalc_type.value = input_dict.get("pwcalc_type", "bands")
#         self.pwcalc_list.set_options_pwcalc_avail(input_dict.get("pwcalc_avail", None))
#         self.calc_charge_dens.value = input_dict.get("calc_charge_dens", False)
#         self.calc_spin_dens.value = input_dict.get("calc_spin_dens", False)
#         self.calc_wfn.value = input_dict.get("calc_wfn", False)
#         self.calc_ildos.value = input_dict.get("calc_ildos", False)
#         self.calc_stm.value = input_dict.get("calc_stm", False)
#         self.charge_dens_options.value = input_dict.get("charge_dens_options", 0)
#         self.ildos_emax.value = input_dict.get("ildos_emax", 0.0)
#         self.ildos_emin.value = input_dict.get("ildos_emin", 0.0)
#         self.ildos_spin_component.value = input_dict.get("ildos_spin_component", 0)
#         # self.stm_sample_bias.value = input_dict.get("stm_sample_bias", '0.0')
#         self.stm_heights.value = input_dict.get("stm_heights", "2.0")
#         self.stm_currents.value = input_dict.get("stm_currents", "0.1")
