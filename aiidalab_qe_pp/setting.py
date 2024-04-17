"""
This module contains the settings for the pp plugin in the AiiDAlab Quantum ESPRESSO (QE) plugin.
"""

import ipywidgets as ipw
import traitlets as tl
from aiidalab_qe.common.panel import Panel
from aiida_quantumespresso.workflows.pdos import PdosWorkChain
from aiida import orm
from .widgets import OrbitalListWidget, OrbitalSelectionWidget, PwCalcListWidget, KpointInfoWidget
from IPython.display import clear_output, display


class Setting(Panel):
    title = "PP Settings"
    identifier = "pp"

    input_structure = tl.Instance(orm.StructureData, allow_none=True)

    def __init__(self, **kwargs):

        self.settings_title = ipw.HTML(
            """<div style="padding-top: 0px; padding-bottom: 0px">
            <h4>Settings</h4></div>"""
        )
        self.calc_options_help= ipw.HTML(
            """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 5px">
            Please select the different calculations options:
            </div>"""
        )
        #PwCalcList Widget

        self.pwcalc_list = PwCalcListWidget(structure=self.input_structure)

        #Calculation options
        self.calc_charge_dens = ipw.Checkbox(description="Charge Density", value=False, layout={'width': 'initial'})
        self.calc_spin_dens = ipw.Checkbox(description="Spin Density", value=False, layout={'width': 'initial'})
        self.calc_wfn = ipw.Checkbox(description="Kohn Sham Orbitals", value=False, layout={'width': 'initial'})
        self.calc_ildos = ipw.Checkbox(description="Integrated Local Density of States", value=False, layout={'width': 'initial'})
        self.calc_stm = ipw.Checkbox(description="STM Plots", value=False)

        #Calc Charge Density Options
        self.charge_dens_options = ipw.Dropdown(options=[('Total charge', 1), ('Spin up', 2), ('Spin down', 3)],
                                                 value=1, description='Options:', disabled=False)
        #Output Charge Density Output
        self.charge_dens_output = ipw.Output()

        #Calc Kohn Sham Orbitals Options
        self.kpoints_info = KpointInfoWidget()
        self.sel_orbital = OrbitalListWidget(item_class=OrbitalSelectionWidget, add_button_text="Add Orbital")
     
        #Calc ILDOS Options
        self.ildos_emin = ipw.FloatText(value=0.0, description='Emin (eV):', disabled=False, layout={'width': 'initial'})
        self.ildos_emax = ipw.FloatText(value=0.0, description='Emax (eV):', disabled=False, layout={'width': 'initial'})
        self.ildos_options = ipw.HBox([self.ildos_emin, self.ildos_emax])

        #Output Kohn Sham Orbitals
        self.wfn_output = ipw.Output()
        self.kpoints_info_output = ipw.Output()

        #Output ILDOS Output
        self.ildos_output = ipw.Output()

        #Calc STM Options
        self.stm_sample_bias = ipw.FloatText(value=0.0, description='Sample bias (Ry):', disabled=False, style={'description_width': 'initial'})   

        #Output STM Output
        self.stm_output = ipw.Output()
        
        # Set up observers for each widget
        self.calc_charge_dens.observe(self._display_widget_options(self.charge_dens_output, self.charge_dens_options), names='value')
        self.calc_wfn.observe(self._display_widget_options(self.wfn_output, self.sel_orbital), names='value')
        self.calc_wfn.observe(self._display_widget_options(self.kpoints_info_output, self.kpoints_info), names='value')
        self.calc_ildos.observe(self._display_widget_options(self.ildos_output, self.ildos_options), names='value')
        self.calc_stm.observe(self._display_widget_options(self.stm_output, self.stm_sample_bias), names='value')
        
        self.pwcalc_list.pwcalc_avail.observe(self._update_calc_options, names='value')
        self.pwcalc_list.pwcalc_type.observe(self._update_calc_type_options, names='value')
        self.pwcalc_list.wc_type.observe(self._update_wc_options, names='value')

        self.children = [
            self.settings_title,
            self.pwcalc_list,
            self.calc_options_help,
            self.calc_charge_dens,
            self.charge_dens_output,
            self.calc_spin_dens,
            self.calc_wfn,
            self.kpoints_info_output,
            self.wfn_output,
            self.calc_ildos,
            self.ildos_output,
            self.calc_stm,
            self.stm_output,
        ]
        super().__init__(**kwargs)

    # Display the output widget associated with each calculation option
    def _display_widget_options(self, output_widget, display_widget):
        def _display(change):
            with output_widget:
                clear_output()
                if change['new']:
                    display(display_widget)
        return _display

    @tl.observe('input_structure')
    def _structure_change(self, change):
        self.pwcalc_list.structure = change['new']

    def set_charge_dens_options(self, lsda):
        if not lsda:
            self.charge_dens_options.options = [('Total charge', 1)]
        else:
            self.charge_dens_options.options = [('Total charge', 1), ('Spin up', 2), ('Spin down', 3)]


    def _reset_calc_options(self):
        self.calc_charge_dens.value = False
        self.calc_spin_dens.value = False
        self.calc_wfn.value = False
        self.calc_ildos.value = False
        self.calc_stm.value = False
        self.calc_spin_dens.disabled = False
        self.calc_stm.disabled = False
        self.set_charge_dens_options(False)
        self.kpoints_info.reset()

    def _update_wc_options(self, change):
        if change['new'] == 'scratch':
            self._reset_calc_options()
        else:
            self._update_calc_options({'new': self.pwcalc_list.pwcalc_avail.value})

    def _update_calc_type_options(self, change):
        if self.pwcalc_list.pwcalc_avail.options:
            self._update_calc_options({'new': self.pwcalc_list.pwcalc_avail.value})


    def _update_calc_options(self, change):

        if self.pwcalc_list.pwcalc_avail.options:
            pw_calc = orm.load_node(change['new'])
            self.calc_spin_dens.disabled = not pw_calc.outputs.output_parameters['lsda']
            self.calc_stm.disabled = pw_calc.outputs.output_parameters['spin_orbit_calculation']
            self.set_charge_dens_options(pw_calc.outputs.output_parameters['lsda'])
            self.kpoints_info.update(pw_calc)
        
        else:
            self._reset_calc_options()




        
