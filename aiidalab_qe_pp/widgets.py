import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets as tl
import numpy as np
from aiida import orm


from aiida_quantumespresso.workflows.pw.bands import PwBandsWorkChain
from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
from aiida_quantumespresso.calculations.pw import PwCalculation
from IPython.display import HTML, clear_output, display

# Cube Visual Widget
from weas_widget import WeasWidget
from IPython.display import display, Javascript
import base64
import io
import tempfile
from pymatgen.io.common import VolumetricData
import os

'''Inspired and adapted from https://github.com/nanotech-empa/aiidalab-empa-surfaces/blob/master/surfaces_tools/widgets/pdos.py(author: yakutovicha)'''

class HorizontalItemWidget(ipw.HBox):
    stack_class = None

    def __init__(self, *args, **kwargs):
        # Delete button.
        self.delete_button = ipw.Button(
            description="x", button_style="danger", layout={"width": "30px"}
        )
        self.delete_button.on_click(self.delete_myself)

        children = kwargs.pop("children", [])
        children.append(self.delete_button)

        super().__init__(*args, children=children, **kwargs)

    def delete_myself(self, _):
        self.stack_class.delete_item(self)


class VerticalStackWidget(ipw.VBox):
    items = tl.Tuple()
    item_class = None

    def __init__(self, item_class, add_button_text="Add"):
        self.item_class = item_class

        self.add_item_button = ipw.Button(
            description=add_button_text, button_style="info"
        )
        self.add_item_button.on_click(self.add_item)

        self.items_output = ipw.VBox()
        tl.link((self, "items"), (self.items_output, "children"))

        # Outputs.
        self.add_item_message = awb.utils.StatusHTML()
        super().__init__(
            children=[
                self.items_output,
                self.add_item_button,
                self.add_item_message,
            ]
        )

    def add_item(self, _):
        self.items += (self.item_class(),)

    @tl.observe("items")
    def _observe_fragments(self, change):
        """Update the list of fragments."""
        if change["new"]:
            self.items_output.children = change["new"]
            for item in change["new"]:
                item.stack_class = self
        else:
            self.items_output.children = []

    def delete_item(self, item):
        try:
            index = self.items.index(item)
        except ValueError:
            return
        self.items = self.items[:index] + self.items[index + 1 :]
        del item

    def length(self): #This function we can delete it ... it is not used
        return len(self.items)

    


class OrbitalSelectionWidget(HorizontalItemWidget):
    def __init__(self):
        self.kpoint = ipw.BoundedIntText(
            description="Kpoint:",
            min = 1,
            max = 1000,
            step =1,
            value=0,
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        self.kbands = ipw.Text(
            description="Bands:",
            value="",
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        super().__init__(children=[self.kbands, self.kpoint])


class OrbitalListWidget(VerticalStackWidget):
    def add_item(self, _):
        self.items += (self.item_class(),)
        
    def reset(self,):
        self.items = []
    #Set the max value of the self.kpoint widget in the OrbitalSelectionWidget
    def set_max_kpoint(self, max_kpoint):
        for item in self.items:
            item.kpoint.max = max_kpoint

    @property
    def orbitals(self):
        return [(item.kbands.value, item.kpoint.value) for item in self.items]


class PwCalcListWidget(ipw.VBox):
    
    structure = tl.Instance(klass=orm.StructureData, allow_none=True)
    _default_pwcalc_list_helper_text = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
            Input structure is not set. Please set the structure first.
            </div>"""

    description = ipw.HTML(
        """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px">
        Please choose the wavefunction source: either from a previous Bands or Nscf calculation linked 
        to your structure, or select 'From scratch' to compute it. If you opt for <strong>'From scratch'</strong>, ensure you've
        set the desired properties like <strong>Electronic band structure</strong> or <strong>Projected density of states</strong> in <strong>Basic
        Settings</strong>, along with specifying the 'pw.x type to use' option. Ensure proper setup of the property in
        both Basic Settings and this tab.
        <h5>Be careful with the clean-up the work directory option in the Advanced Settings.</h5>
        </div>""",
        layout=ipw.Layout(max_width="100%"),
    )
    no_avail_cals = tl.Bool(False)
    def __init__(
        self,
        structure: orm.StructureData,
        **kwargs,
    ):
        self.select_helper = ipw.HTML(self._default_pwcalc_list_helper_text)
        self.pwcalc_avail_helper = ipw.HTML()
        self.pwcalc_avail_output = ipw.Output()
        self.wc_type = ipw.ToggleButtons(
            options=[('PwCalculation', 'pw_calc'), ('From scratch', 'scratch')],
            description='WorkChain to use',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltips=['Previous WorkChain', 'Compute a new WorkChain from scratch'],
        #     icons=['check'] * 3
            style={'description_width': 'initial'},
        )
        self.pwcalc_type = ipw.Dropdown(
            options=[("Bands", "bands"), ("Nscf", "nscf")],
            value="bands",
            description="Select the pw.x type to use:",
            disabled=False,
            style={"description_width": "initial"},
        )

        self.pwcalc_avail = ipw.Dropdown(
            options=[], # List of available calculations
            value=None,
            description="PwCalculation available:",
            disabled=False,
            style={"description_width": "initial"},
            layout={'width': '500px'}
        )

        self.bands_calc_list = []
        self.nscf_calc_list = []
        
        self.pwcalc_type.observe(self.update_pwcalc_avail, names='value')
        self.wc_type.observe(self.display_pwcalc_output, names='value')

        super().__init__(
            children=[
                self.select_helper,
                self.description,
                self.wc_type,
                self.pwcalc_type,
                self.pwcalc_avail_output,
                ]
            , **kwargs
        )
        self._reset()

    
    def _reset(self):
        if self.structure is None:
            self.select_helper.value = self._default_pwcalc_list_helper_text
            self.reset_pwcalc_avail()
            return

        self.select_helper.value = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: green;">
            Structure set PK: {}.
            </div>""".format(self.structure.pk)

        # Get the available calculations
        self.bands_calc_list = self.get_available_pwcalcs(self.structure, 'bands')
        self.nscf_calc_list = self.get_available_pwcalcs(self.structure, 'nscf')

        self.update_pwcalc_avail({'type': 'change', 'name': 'value', 'new': 'bands'})

    @tl.observe("structure")
    def _structure_change(self, _):
        self._reset()
        
    def get_available_pwcalcs(self,structure, wc_type):
        avail_list = []
        if wc_type == 'bands':
        
            calc_list = orm.QueryBuilder().append(
                orm.StructureData,
                filters={'id': structure.pk},
                tag='structure'
            ).append(
                PwBandsWorkChain,
                filters={
                        "attributes.exit_status": 0,
                    },
                    with_incoming="structure",
                    tag="bands_wc",
            ).append(
                PwBaseWorkChain,
                filters={
                    "attributes.exit_status": 0,
                },
                with_incoming="bands_wc",
                tag="base"
            ).append(
                PwCalculation,
                filters={
                    "attributes.exit_status": 0,
                },
                project = ["*"],
                with_incoming="base",
                tag="calc",
            ).append(
                orm.Dict,
                filters={
                    "attributes.CONTROL.calculation": "bands",
                },
                with_outgoing="calc",
            ).all(flat=True)

        elif wc_type == 'nscf':
            calc_list = orm.QueryBuilder().append(
                orm.StructureData,
                filters={'id': structure.pk},
                tag='structure'
            ).append(
                PwBaseWorkChain,
                filters={
                    "attributes.exit_status": 0,
                },
                with_incoming="structure",
                tag="base"
            ).append(
                PwCalculation,
                filters={
                    "attributes.exit_status": 0,
                },
                project = ["*"],
                with_incoming="base",
                tag="calc",
            ).append(
                orm.Dict,
                filters={
                    "attributes.CONTROL.calculation": "nscf",
                },
                with_outgoing="calc",
            ).all(flat=True)

        for calc in calc_list:
            try:
                remote_dir = calc.outputs.remote_folder.listdir()
                description = "PK: {} LSDA = {} SOC={}".format(calc.pk, calc.outputs.output_parameters['lsda'], calc.outputs.output_parameters['spin_orbit_calculation'])
                
                avail_list.append((description, calc.pk))
            except OSError:
            # If OSError occurs, skip this iteration
                continue
        
        return avail_list

    def update_pwcalc_avail(self,change):
        if change['type'] == 'change' and change['name'] == 'value':
            if change['new'] == 'bands':
                self.pwcalc_avail.options = self.bands_calc_list
                if not self.bands_calc_list:
                    self.pwcalc_avail_helper.value = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
                    No Bands calculations available for this structure.
                    </div>"""
                    self.no_avail_cals = True
                else:
                    self.no_avail_cals = False
            elif change['new'] == 'nscf':
                self.pwcalc_avail.options = self.nscf_calc_list
                if not self.nscf_calc_list:
                    self.pwcalc_avail_helper.value = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
                    No Nscf calculations available for this structure.
                    </div>"""
                    self.no_avail_cals = True
                else:
                    self.no_avail_cals = False
            else:
                self.pwcalc_avail.options = []
        if self.wc_type.value == 'pw_calc':
            with self.pwcalc_avail_output:
                clear_output()
                if change['new']:
                    display(self.pwcalc_avail_options())
        
    def display_pwcalc_output(self,change):
        if change['new'] == 'pw_calc':
            with self.pwcalc_avail_output:
                clear_output()
                if change['new']:
                    display(self.pwcalc_avail_options())
        else:
            with self.pwcalc_avail_output:
                clear_output()
    
    def pwcalc_avail_options(self):
        if self.pwcalc_type.value == 'bands' and self.bands_calc_list:
            return self.pwcalc_avail
        elif self.pwcalc_type.value == 'nscf' and self.nscf_calc_list:
            return self.pwcalc_avail
        elif self.pwcalc_type.value == 'bands' and not self.bands_calc_list:
            return self.pwcalc_avail_helper
        elif self.pwcalc_type.value == 'nscf' and not self.nscf_calc_list:
            return self.pwcalc_avail_helper
    
    def set_options_pwcalc_avail(self, pk):
        calc = orm.load_node(pk)
        description = "PK: {} LSDA = {} SOC={}".format(calc.pk, calc.outputs.output_parameters['lsda'], calc.outputs.output_parameters['spin_orbit_calculation'])
        self.pwcalc_avail.options = [(description, pk)]
        self.pwcalc_avail.description = "PwCalculation used:"

    def reset_pwcalc_avail(self):
        self.pwcalc_avail.options = []
        self.pwcalc_avail.description = "PwCalculation available:"
        

    

class KpointInfoWidget(ipw.VBox):
    def __init__(self, **kwargs):
        
        self.kbands_info = ipw.HTML()
        self.electron_info = ipw.HTML()
        self.kpoints_table = ipw.Output()
        self.sel_orbital = OrbitalListWidget(item_class=OrbitalSelectionWidget, add_button_text="Add Orbital")
        super().__init__(
            children=[
                self.kbands_info,
                self.electron_info,
                self.kpoints_table,
                self.sel_orbital,
            ],
            **kwargs
        )

    def update_electrons(self, kpoint):
        self.electron_info.value = f"<strong>Number of electrons:</strong> {kpoint}"

    def update_kbands(self, kbands):
        self.kbands_info.value = f"<strong>Number of Bands:</strong> {kbands}"

    def update_kpoints_table(self, list_kpoints):
        """Update table with the kpoints. Number - (kx,ky,kz).  list_kpoints"""
        rounded_kpoints = np.round(list_kpoints, 4).tolist()
        table_data = [(index + 1, kpoint) for index, kpoint in enumerate(rounded_kpoints)]
        table_html = "<table>"
        table_html += "<tr><th style='text-align:center; width: 100px;'>Kpoint</th><th style='text-align:center;'>Crystal</th></tr>"
        table_html += "<tr><th style='text-align:center; width: 100px;'>Index</th><th style='text-align:center;'>coord</th></tr>"
        for row in table_data:
            table_html += "<tr>"
            for cell in row:
                table_html += "<td style='text-align:center;'>{}</td>".format(cell)
            table_html += "</tr>"
        table_html += "</table>"
        self.kpoints_table.layout = {
            "overflow": "auto",
            "height": "200px",
            "width": "300px",
        }
        with self.kpoints_table:
            clear_output()
            display(HTML(table_html))

    def reset(self):
        self.kbands_info.value = ""
        self.electron_info.value = ""
        self.clear_kpoints_table()
        self.sel_orbital.reset()
    
    def clear_kpoints_table(self):
        with self.kpoints_table:
            clear_output()
        self.kpoints_table.layout = {
            "overflow": "auto",
            "height": "0px",
            "width": "0px",
        }
    def update(self, calc):
        self.update_electrons(calc.outputs.output_parameters['number_of_electrons'])
        self.update_kbands(calc.outputs.output_parameters['number_of_bands'])
        try:
            kpoints = calc.inputs.kpoints.get_kpoints()
            self.update_kpoints_table(kpoints)
            self.sel_orbital.set_max_kpoint(len(kpoints))
        except AttributeError:
            self.clear_kpoints_table()
        


    

class CubeVisualWdiget(ipw.VBox):
    """Widget to visualize the output data from PPWorkChain."""


    def __init__(self, structure, cube_data , plot_num , **kwargs):

        self.guiConfig = {
            "enabled": True,
            "components": {"atomsControl": True, "buttons": True},
            "buttons": {
                "fullscreen": True,
                "download": True,
                "measurement": True,
            },
        }
        self.structure = structure
        self.cube_data = cube_data.get_array("data")
        self.plot_num = plot_num
        self.viewer = self._set_viewer()

        # Display Button
        self.display_button = ipw.Button(description="Display", button_style="primary")

        # Download Cubefile Button

        self.download_button = ipw.Button(description="Download", button_style="primary")

        self.buttons = ipw.HBox([self.display_button, self.download_button])

        self.display_button.on_click(self._display)
        self.download_button.on_click(self.download_cube)
        super().__init__(children=[self.buttons,self.viewer], **kwargs)



    def _set_viewer(self):
        viewer = WeasWidget(guiConfig=self.guiConfig)
        viewer.from_ase(self.structure.get_ase())
        viewer.avr.iso.volumetric_data = {"values": self.cube_data}
        viewer.avr.iso.settings = [{"isovalue": 0.001, "mode": 0}]
        return viewer

    def _display(self, _=None):
        self.viewer._widget.send_js_task({"name": "tjs.onWindowResize", "kwargs": {}})
        self.viewer._widget.send_js_task(
            {
                "name": "tjs.updateCameraAndControls",
                "kwargs": {"direction": [0, -100, 0]},
            }
        )
        
    def download_cube(self, _=None):
        # Create a temporary file, write to it, and initiate download
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as tmp:
            # Write the cube data to a temporary file using pymatgen's VolumetricData
            my_cube = VolumetricData(structure=self.structure.get_pymatgen(), data={"total": self.cube_data})
            my_cube.to_cube(tmp.name)

            # Move the file pointer back to the start for reading
            tmp.seek(0)
            raw_bytes = tmp.read()

        # Encode the file content to base64
        base64_payload = base64.b64encode(raw_bytes).decode()

        # JavaScript to trigger download
        filename = f"plot_{self.plot_num}.cube"
        js_download = Javascript(
            f"""
            var link = document.createElement('a');
            link.href = "data:application/octet-stream;base64,{base64_payload}";
            link.download = "{filename}";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            """
        )
        display(js_download)

        # Clean up by removing the temporary file
        os.unlink(tmp.name)

