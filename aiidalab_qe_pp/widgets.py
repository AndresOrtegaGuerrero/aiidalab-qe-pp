import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets as tl


# Cube Visual Widget

"""Inspired and adapted from https://github.com/nanotech-empa/aiidalab-empa-surfaces/blob/master/surfaces_tools/widgets/pdos.py(author: yakutovicha)"""


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

    def length(self):  # This function we can delete it ... it is not used
        return len(self.items)


class OrbitalSelectionWidget(HorizontalItemWidget):
    def __init__(self):
        self.kpoint = ipw.BoundedIntText(
            description="Kpoint:",
            min=1,
            max=1000,
            step=1,
            value=0,
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        self.kbands = ipw.Text(
            description="Bands:",
            placeholder="e.g. 1..5 8 10",
            value="",
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        super().__init__(children=[self.kbands, self.kpoint])
        # Add observers to kbands and kpoint
        self.kpoint.observe(self._trigger_update, names="value")
        self.kbands.observe(self._trigger_update, names="value")

    def _trigger_update(self, change):
        # Notify parent widget to update orbitals
        if hasattr(self, "parent_widget"):
            self.parent_widget._update_orbitals()


class OrbitalListWidget(VerticalStackWidget, tl.HasTraits):
    orbitals = tl.List([])
    max_kpoint = tl.Int()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observe(self._update_orbitals, names="items")

    def add_item(self, _):
        item = self.item_class()
        # Observe changes in kpoint and kbands for each item
        item.kpoint.observe(self._on_kpoint_change, names="value")
        item.kbands.observe(self._on_kbands_change, names="value")
        item.kpoint.max = self.max_kpoint
        self.items += (item,)

    def reset(self):
        self.items = []
        self._update_orbitals()

    def _on_kpoint_change(self, change):
        """Triggered when kpoint value changes."""
        self._update_orbitals()

    def _on_kbands_change(self, change):
        """Triggered when kbands value changes."""
        self._update_orbitals()

    def _update_orbitals(self, *_):
        """Update the orbitals trait when items change."""
        self.orbitals = [(item.kbands.value, item.kpoint.value) for item in self.items]


# class PwCalcListWidget(ipw.VBox):
#     structure = tl.Instance(klass=orm.StructureData, allow_none=True)
#     _default_pwcalc_list_helper_text = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
#             Input structure is not set. Please set the structure first.
#             </div>"""

#     # , or select 'From scratch' to compute it. If you opt for <strong>'From scratch'</strong>, ensure you've
#     # set the desired properties like <strong>Electronic band structure</strong> or <strong>Projected density of states</strong> in <strong>Basic
#     # Settings</strong>, along with specifying the 'pw.x type to use' option. Ensure proper setup of the property in
#     # both Basic Settings and this tab.
#     description = ipw.HTML(
#         """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px">
#         Please choose the wavefunction source: either from a previous Bands or Nscf calculation linked
#         to your structure.
#         <h5>Be careful with the clean-up the work directory option in the Advanced Settings.</h5>
#         </div>""",
#         layout=ipw.Layout(max_width="100%"),
#     )
#     comp_description = ipw.HTML(
#         """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px">
#         <h5>For the next step, select the same computer used in the selected PwCalculation because the necessary files are stored there.</h5>
#         </div>""",
#         layout=ipw.Layout(max_width="100%"),
#     )
#     no_avail_cals = tl.Bool(False)

#     def __init__(
#         self,
#         structure: orm.StructureData,
#         **kwargs,
#     ):
#         self.select_helper = ipw.HTML(self._default_pwcalc_list_helper_text)
#         self.pwcalc_avail_helper = ipw.HTML()
#         self.pwcalc_avail_output = ipw.Output()
#         self.wc_type = ipw.ToggleButtons(
#             # options=[('PwCalculation', 'pw_calc'), ('From scratch', 'scratch')],
#             options=[("PwCalculation", "pw_calc")],
#             description="WorkChain to use",
#             disabled=False,
#             button_style="",  # 'success', 'info', 'warning', 'danger' or ''
#             tooltips=["Previous WorkChain", "Compute a new WorkChain from scratch"],
#             #     icons=['check'] * 3
#             style={"description_width": "initial"},
#         )
#         self.pwcalc_type = ipw.Dropdown(
#             options=[("Bands", "bands"), ("Nscf", "nscf")],
#             value="bands",
#             description="Select the pw.x type to use:",
#             disabled=False,
#             style={"description_width": "initial"},
#         )

#         self.pwcalc_avail = ipw.Dropdown(
#             options=[],  # List of available calculations
#             value=None,
#             description="PwCalculation available:",
#             disabled=False,
#             style={"description_width": "initial"},
#             layout={"width": "600px"},
#         )

#         self.bands_calc_list = []
#         self.nscf_calc_list = []

#         self.pwcalc_type.observe(self.update_pwcalc_avail, names="value")
#         self.wc_type.observe(self.display_pwcalc_output, names="value")

#         super().__init__(
#             children=[
#                 self.select_helper,
#                 self.description,
#                 self.wc_type,
#                 self.comp_description,
#                 self.pwcalc_type,
#                 self.pwcalc_avail_output,
#             ],
#             **kwargs,
#         )
#         self._reset()

#     def _reset(self):
#         if self.structure is None:
#             self.select_helper.value = self._default_pwcalc_list_helper_text
#             self.reset_pwcalc_avail()
#             return

#         self.select_helper.value = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: green;">
#             Structure set PK: {}.
#             </div>""".format(self.structure.pk)

#         # Get the available calculations
#         self.bands_calc_list = self.get_available_pwcalcs(self.structure, "bands")
#         self.nscf_calc_list = self.get_available_pwcalcs(self.structure, "nscf")

#         self.update_pwcalc_avail({"type": "change", "name": "value", "new": "bands"})

#     @tl.observe("structure")
#     def _structure_change(self, _):
#         self._reset()

#     def get_available_pwcalcs(self, structure, wc_type):
#         avail_list = []
#         if wc_type == "bands":
#             calc_list = (
#                 orm.QueryBuilder()
#                 .append(
#                     orm.StructureData, filters={"id": structure.pk}, tag="structure"
#                 )
#                 .append(
#                     BandsWorkChain,
#                     filters={
#                         "attributes.exit_status": 0,
#                     },
#                     with_incoming="structure",
#                     tag="bands_wc_qe",
#                 )
#                 .append(
#                     (PwBandsWorkChain, ProjwfcBandsWorkChain),
#                     filters={
#                         "attributes.exit_status": 0,
#                     },
#                     with_incoming="bands_wc_qe",
#                     tag="bands_wc",
#                 )
#                 .append(
#                     PwBaseWorkChain,
#                     filters={
#                         "attributes.exit_status": 0,
#                     },
#                     with_incoming="bands_wc",
#                     tag="base",
#                 )
#                 .append(
#                     PwCalculation,
#                     filters={
#                         "attributes.exit_status": 0,
#                     },
#                     project=["*"],
#                     with_incoming="base",
#                     tag="calc",
#                 )
#                 .append(
#                     orm.Dict,
#                     filters={
#                         "attributes.CONTROL.calculation": "bands",
#                     },
#                     with_outgoing="calc",
#                 )
#                 .all(flat=True)
#             )

#         elif wc_type == "nscf":
#             calc_list = (
#                 orm.QueryBuilder()
#                 .append(
#                     orm.StructureData, filters={"id": structure.pk}, tag="structure"
#                 )
#                 .append(
#                     PwBaseWorkChain,
#                     filters={
#                         "attributes.exit_status": 0,
#                     },
#                     with_incoming="structure",
#                     tag="base",
#                 )
#                 .append(
#                     PwCalculation,
#                     filters={
#                         "attributes.exit_status": 0,
#                     },
#                     project=["*"],
#                     with_incoming="base",
#                     tag="calc",
#                 )
#                 .append(
#                     orm.Dict,
#                     filters={
#                         "attributes.CONTROL.calculation": "nscf",
#                     },
#                     with_outgoing="calc",
#                 )
#                 .all(flat=True)
#             )

#         for calc in calc_list:
#             try:
#                 calc.outputs.remote_folder.listdir()
#                 description = "PK: {} LSDA = {} SOC = {} Computer = {}".format(
#                     calc.pk,
#                     calc.outputs.output_parameters["lsda"],
#                     calc.outputs.output_parameters["spin_orbit_calculation"],
#                     calc.computer.label,
#                 )

#                 avail_list.append((description, calc.pk))
#             except OSError:
#                 # If OSError occurs, skip this iteration
#                 continue
#             # Fix this in future
#             except SSHException:
#                 continue
#             # Skip calculations without necessary information
#             except NotExistent:
#                 continue

#         return avail_list

#     def update_pwcalc_avail(self, change):
#         if change["type"] == "change" and change["name"] == "value":
#             if change["new"] == "bands":
#                 self.pwcalc_avail.options = self.bands_calc_list
#                 if not self.bands_calc_list:
#                     self.pwcalc_avail_helper.value = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
#                     No Bands calculations available for this structure.
#                     </div>"""
#                     self.no_avail_cals = True
#                 else:
#                     self.no_avail_cals = False
#             elif change["new"] == "nscf":
#                 self.pwcalc_avail.options = self.nscf_calc_list
#                 if not self.nscf_calc_list:
#                     self.pwcalc_avail_helper.value = """<div style="line-height: 140%; padding-top: 0px; padding-bottom: 10px; color: red;">
#                     No Nscf calculations available for this structure.
#                     </div>"""
#                     self.no_avail_cals = True
#                 else:
#                     self.no_avail_cals = False
#             else:
#                 self.pwcalc_avail.options = []
#         if self.wc_type.value == "pw_calc":
#             with self.pwcalc_avail_output:
#                 clear_output()
#                 if change["new"]:
#                     display(self.pwcalc_avail_options())

#     def display_pwcalc_output(self, change):
#         if change["new"] == "pw_calc":
#             with self.pwcalc_avail_output:
#                 clear_output()
#                 if change["new"]:
#                     display(self.pwcalc_avail_options())
#         else:
#             with self.pwcalc_avail_output:
#                 clear_output()

#     def pwcalc_avail_options(self):
#         if self.pwcalc_type.value == "bands" and self.bands_calc_list:
#             return self.pwcalc_avail
#         elif self.pwcalc_type.value == "nscf" and self.nscf_calc_list:
#             return self.pwcalc_avail
#         elif self.pwcalc_type.value == "bands" and not self.bands_calc_list:
#             return self.pwcalc_avail_helper
#         elif self.pwcalc_type.value == "nscf" and not self.nscf_calc_list:
#             return self.pwcalc_avail_helper

#     def set_options_pwcalc_avail(self, pk):
#         calc = orm.load_node(pk)
#         description = "PK: {} LSDA: {} SOC {} Computer = {} ".format(
#             calc.pk,
#             calc.outputs.output_parameters["lsda"],
#             calc.outputs.output_parameters["spin_orbit_calculation"],
#             calc.computer.label,
#         )
#         self.pwcalc_avail.options = [(description, pk)]
#         self.pwcalc_avail.description = "PwCalculation used:"

#     def reset_pwcalc_avail(self):
#         self.pwcalc_avail.options = []
#         self.pwcalc_avail.description = "PwCalculation available:"


# class KpointInfoWidget(ipw.VBox):
#     def __init__(self, **kwargs):
#         self.kbands_info = ipw.HTML()
#         self.electron_info = ipw.HTML()
#         self.kpoints_table = ipw.Output()
#         self.sel_orbital = OrbitalListWidget(
#             item_class=OrbitalSelectionWidget, add_button_text="Add orbital"
#         )
#         super().__init__(
#             children=[
#                 self.kbands_info,
#                 self.electron_info,
#                 self.kpoints_table,
#                 self.sel_orbital,
#             ],
#             **kwargs,
#         )

#     def update_electrons(self, kpoint):
#         self.electron_info.value = f"<strong>Number of electrons:</strong> {kpoint}"

#     def update_kbands(self, kbands):
#         self.kbands_info.value = f"<strong>Number of Bands:</strong> {kbands}"

#     def update_kpoints_table(self, list_kpoints):
#         """Update table with the kpoints. Number - (kx,ky,kz).  list_kpoints"""
#         rounded_kpoints = np.round(list_kpoints, 4).tolist()
#         table_data = [
#             (index + 1, kpoint) for index, kpoint in enumerate(rounded_kpoints)
#         ]
#         table_html = "<table>"
#         table_html += "<tr><th style='text-align:center; width: 100px;'>Kpoint</th><th style='text-align:center;'>Crystal</th></tr>"
#         table_html += "<tr><th style='text-align:center; width: 100px;'>Index</th><th style='text-align:center;'>coord</th></tr>"
#         for row in table_data:
#             table_html += "<tr>"
#             for cell in row:
#                 table_html += "<td style='text-align:center;'>{}</td>".format(cell)
#             table_html += "</tr>"
#         table_html += "</table>"
#         self.kpoints_table.layout = {
#             "overflow": "auto",
#             "height": "200px",
#             "width": "300px",
#         }
#         with self.kpoints_table:
#             clear_output()
#             display(HTML(table_html))

#     def reset(self):
#         self.kbands_info.value = ""
#         self.electron_info.value = ""
#         self.clear_kpoints_table()
#         self.sel_orbital.reset()

#     def clear_kpoints_table(self):
#         with self.kpoints_table:
#             clear_output()
#         self.kpoints_table.layout = {
#             "overflow": "auto",
#             "height": "0px",
#             "width": "0px",
#         }

#     def update(self, calc):
#         self.update_electrons(calc.outputs.output_parameters["number_of_electrons"])
#         self.update_kbands(calc.outputs.output_parameters["number_of_bands"])
#         try:
#             kpoints = calc.inputs.kpoints.get_kpoints()
#             self.update_kpoints_table(kpoints)
#             self.sel_orbital.set_max_kpoint(len(kpoints))
#         except AttributeError:
#             self.clear_kpoints_table()


# class CubeVisualWidget(ipw.VBox):
#     """Widget to visualize the output data from PPWorkChain."""

#     def __init__(self, structure, cube_data, plot_num, **kwargs):
#         self.guiConfig = {
#             "enabled": True,
#             "components": {
#                 "atomsControl": True,
#                 "buttons": True,
#                 "cameraControls": True,
#             },
#             "buttons": {
#                 "fullscreen": True,
#                 "download": True,
#                 "measurement": True,
#             },
#         }
#         self.structure = structure
#         self.cube_data = cube_data
#         self.plot_num = plot_num
#         self.viewer = self._set_viewer()

#         # Display Button
#         self.display_button = ipw.Button(description="Display", button_style="primary")

#         # Download Cubefile Button
#         self.download_button = ipw.Button(
#             description="Download", button_style="primary"
#         )

#         self.buttons = ipw.HBox([self.display_button, self.download_button])

#         self.display_button.on_click(self._display)
#         self.download_button.on_click(self.download_cube)

#         super().__init__(children=[self.buttons, self.viewer], **kwargs)

#     def _set_viewer(self):
#         viewer = WeasWidget(guiConfig=self.guiConfig)
#         viewer.from_ase(self.structure.get_ase())
#         isovalue = 2 * np.std(self.cube_data) + np.mean(self.cube_data)
#         viewer.avr.iso.volumetric_data = {"values": self.cube_data}
#         viewer.avr.iso.settings = {"isovalue": isovalue, "mode": 0}
#         viewer.avr.color_type = "JMOL"
#         viewer.avr.model_style = 1
#         return viewer

#     def _display(self, _=None):
#         self.viewer._widget.send_js_task({"name": "tjs.onWindowResize", "kwargs": {}})
#         self.viewer._widget.send_js_task(
#             {
#                 "name": "tjs.updateCameraAndControls",
#                 "kwargs": {"direction": [0, -100, 0]},
#             }
#         )

#     def download_cube(self, _=None, filename="plot"):
#         # Create a temporary file, write to it, and initiate download
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as tmp:
#             # Write the cube data to a temporary file using pymatgen's VolumetricData
#             if self.structure.pbc != [True, True, True]:
#                 structure_temp = self.structure.clone()
#                 structure_temp.pbc = [True, True, True]
#                 structure = structure_temp.get_pymatgen()
#             else:
#                 structure = self.structure.get_pymatgen()

#             my_cube = VolumetricData(
#                 structure=structure, data={"total": self.cube_data}
#             )
#             my_cube.to_cube(tmp.name)

#             # Move the file pointer back to the start for reading
#             tmp.seek(0)
#             raw_bytes = tmp.read()

#         # Encode the file content to base64
#         base64_payload = base64.b64encode(raw_bytes).decode()

#         # if filename is not provided, use plot_num
#         if filename == "plot":
#             filename = f"plot_{self.plot_num}"

#         # JavaScript to trigger download
#         filename = f"{filename}.cube"
#         js_download = Javascript(
#             f"""
#             var link = document.createElement('a');
#             link.href = "data:application/octet-stream;base64,{base64_payload}";
#             link.download = "{filename}";
#             document.body.appendChild(link);
#             link.click();
#             document.body.removeChild(link);
#             """
#         )
#         display(js_download)

#         # Clean up by removing the temporary file
#         os.unlink(tmp.name)


# class WfnVisualWidget(CubeVisualWidget):
#     """Widget to visualize the wavefunction data with additional kpoints and bands selection."""

#     def __init__(
#         self,
#         structure,
#         cube_data_dict,
#         kpoint_band_data,
#         number_of_k_points,
#         lsda,
#         **kwargs,
#     ):
#         self.kpoint_band_data = (
#             kpoint_band_data  # This should be a list of dictionaries
#         )
#         self.cube_data_dict = (
#             cube_data_dict  # This should be a dictionary of cube_data objects
#         )
#         self.lsda = lsda
#         self.number_of_k_points = number_of_k_points

#         # Extract kpoints and bands from kpoint_band_data
#         kpoints = [entry["kpoint"] for entry in kpoint_band_data]
#         bands_dict = {entry["kpoint"]: entry["bands"] for entry in kpoint_band_data}

#         if lsda:
#             kpoints = kpoints[: len(kpoints) // 2]

#         # Initialize the Dropdowns
#         self.kpoints_dropdown = ipw.Dropdown(
#             options=kpoints,
#             description="Kpoint:",
#             style={"description_width": "initial"},
#             layout={"width": "150px"},
#         )
#         self.bands_dropdown = ipw.Dropdown(
#             description="Band:",
#             style={"description_width": "initial"},
#             layout={"width": "150px"},
#         )

#         # Set the bands options based on the initial kpoint selection
#         self._update_bands_options(self.kpoints_dropdown.value)

#         self.kpoints_dropdown.observe(self._on_kpoint_change, names="value")
#         self.bands_dropdown.observe(self._on_band_change, names="value")

#         self.spin = ipw.Dropdown(
#             options=[("Up", "up"), ("Down", "down")],
#             description="Spin:",
#             style={"description_width": "initial"},
#             layout={"width": "150px"},
#         )

#         self.spin.observe(self._on_spin_change, names="value")
#         # Add the new Dropdowns to the widget
#         self.controls = ipw.HBox(
#             [self.kpoints_dropdown, self.bands_dropdown, self.spin]
#         )

#         # Initialize the viewer with the first kpoint-band combination
#         initial_kpoint = kpoints[0]
#         initial_band = bands_dict[initial_kpoint][0]
#         initial_cube_data = cube_data_dict[
#             f"kp_{initial_kpoint}_kb_{initial_band}"
#         ].get_array("data")

#         super().__init__(structure, initial_cube_data, plot_num="wfn", **kwargs)
#         self.children = [self.controls, self.buttons, self.viewer]
#         if self.lsda:
#             self.spin.layout.display = "block"
#         else:
#             self.spin.layout.display = "none"

#     def _update_bands_options(self, kpoint):
#         """Update the bands dropdown options based on the selected kpoint."""
#         bands = next(
#             entry["bands"]
#             for entry in self.kpoint_band_data
#             if entry["kpoint"] == kpoint
#         )
#         self.bands_dropdown.options = bands

#     def _on_kpoint_change(self, change):
#         """Callback function to update bands options when kpoint changes."""
#         self._update_bands_options(change["new"])
#         self._update_viewer()

#     def _on_band_change(self, change):
#         """Callback function to update viewer when band changes."""
#         self._update_viewer()

#     def _on_spin_change(self, change):
#         """Callback function to update viewer when spin changes."""
#         self._update_viewer()

#     def _update_viewer(self):
#         """Update the viewer with the selected kpoint and band data."""
#         kpoint = self.kpoints_dropdown.value
#         band = self.bands_dropdown.value

#         if self.lsda and self.spin.value == "down":
#             kpoint += self.number_of_k_points

#         key = f"kp_{kpoint}_kb_{band}"
#         self.cube_data = self.cube_data_dict.get(key).get_array("data")
#         isovalue = 2 * np.std(self.cube_data) + np.mean(self.cube_data)
#         self.viewer.avr.iso.volumetric_data = {"values": self.cube_data}
#         self.viewer.avr.iso.settings = {"isovalue": isovalue, "mode": 0}

#     def download_cube(self, _=None):
#         """Download the cube file with the current kpoint and band in the filename."""
#         kpoint = self.kpoints_dropdown.value
#         band = self.bands_dropdown.value

#         if self.lsda and self.spin.value == "down":
#             kpoint += self.number_of_k_points

#         band = self.bands_dropdown.value
#         filename = f"plot_wfn_kp_{kpoint}_kb_{band}"
#         super().download_cube(_=None, filename=filename)


# class STMPlotWidget(ipw.VBox):
#     SETTINGS = {
#         "margin": {"l": 50, "r": 50, "b": 50, "t": 80},
#         "button_layer_1_height": 1.3,
#         "width": 800,
#         "height": 600,
#         "color_scales": ["Hot", "Cividis", "Greys", "Viridis"],
#         "default_color_scale": "Hot",
#     }

#     def __init__(self, node, mode, value, **kwargs):
#         self.x_cart = node["stm_data"].get_array("xcart")
#         self.y_cart = node["stm_data"].get_array("ycart")
#         self.f_stm = node["stm_data"].get_array("fstm")
#         self.mode = mode
#         self.value = value
#         self._process_data()
#         self.plot = self._create_plot()

#         self.zmax_text = ipw.BoundedFloatText(
#             value=np.max(self.z_grid),
#             min=np.min(self.z_grid),
#             max=np.max(self.z_grid),
#             step=(np.max(self.z_grid) - np.min(self.z_grid)) / 100,
#             description="Z Max:",
#             continuous_update=False,
#         )
#         self.zmax_text.observe(self._update_zmax, names="value")

#         super().__init__(
#             children=[
#                 self.plot,
#                 self.zmax_text,
#             ],
#             **kwargs,
#         )

#     def _process_data(self):
#         valid_indices = (
#             ~np.isnan(self.x_cart) & ~np.isnan(self.y_cart) & ~np.isnan(self.f_stm)
#         )
#         x_valid = self.x_cart[valid_indices]
#         y_valid = self.y_cart[valid_indices]
#         z_valid = self.f_stm[valid_indices]

#         epsilon = 1e-6
#         self.unique_x = np.unique(np.where(np.abs(x_valid) < epsilon, 0, x_valid))
#         self.unique_y = np.unique(np.where(np.abs(y_valid) < epsilon, 0, y_valid))

#         X, Y = np.meshgrid(self.unique_x, self.unique_y)
#         Z = griddata((x_valid, y_valid), z_valid, (X, Y), method="cubic")

#         self.x_grid = X
#         self.y_grid = Y
#         self.z_grid = Z

#     def _create_plot(self):
#         heatmap = go.Heatmap(
#             z=self.z_grid,
#             x=self.unique_x,
#             y=self.unique_y,
#             colorscale=self.SETTINGS["default_color_scale"],
#             colorbar=dict(
#                 title=f"{'Distance to the surface (Å)' if self.mode == 'current' else 'Electron density (a.u.)'}"
#             ),
#         )

#         fig = go.Figure(data=heatmap)
#         fig.update_layout(
#             title=dict(
#                 text=f"Constant {self.mode} plot, {self.value} {'Å' if self.mode == 'height' else 'pA'}",
#                 x=0.5,  # Center the title
#                 y=0.85,  # Adjust the vertical position of the title
#                 xanchor="center",
#                 yanchor="top",
#             ),
#             xaxis=dict(
#                 title="x (Å)",
#                 range=[np.min(self.unique_x), np.max(self.unique_x)],
#                 tickmode="auto",
#                 ticks="outside",
#                 showline=True,
#                 mirror=True,
#                 showgrid=False,
#             ),
#             yaxis=dict(
#                 title="y (Å)",
#                 range=[np.min(self.unique_y), np.max(self.unique_y)],
#                 tickmode="auto",
#                 ticks="outside",
#                 showline=True,
#                 mirror=True,
#                 showgrid=False,
#             ),
#             autosize=False,
#             width=self.SETTINGS["width"],
#             height=self.SETTINGS["height"],
#             margin=self.SETTINGS["margin"],
#         )

#         fig.update_layout(
#             updatemenus=[
#                 dict(
#                     buttons=[
#                         dict(
#                             args=["colorscale", colorscale],
#                             label=colorscale,
#                             method="restyle",
#                         )
#                         for colorscale in self.SETTINGS["color_scales"]
#                     ],
#                     direction="down",
#                     pad={"r": 10, "t": 10},
#                     showactive=True,
#                     x=0.1,
#                     xanchor="left",
#                     y=self.SETTINGS["button_layer_1_height"],
#                     yanchor="top",
#                 ),
#                 dict(
#                     buttons=[
#                         dict(
#                             args=["reversescale", False],
#                             label="False",
#                             method="restyle",
#                         ),
#                         dict(
#                             args=["reversescale", True], label="True", method="restyle"
#                         ),
#                     ],
#                     direction="down",
#                     pad={"r": 10, "t": 10},
#                     showactive=True,
#                     x=0.39,
#                     xanchor="left",
#                     y=self.SETTINGS["button_layer_1_height"],
#                     yanchor="top",
#                 ),
#             ]
#         )

#         fig.update_layout(
#             annotations=[
#                 dict(
#                     text="Colorscale",
#                     x=-0.03,
#                     xref="paper",
#                     y=self.SETTINGS["button_layer_1_height"] - 0.05,
#                     yref="paper",
#                     align="left",
#                     showarrow=False,
#                 ),
#                 dict(
#                     text="Reverse<br>Colorscale",
#                     x=0.26,
#                     xref="paper",
#                     y=self.SETTINGS["button_layer_1_height"] - 0.025,
#                     yref="paper",
#                     showarrow=False,
#                 ),
#             ]
#         )

#         return go.FigureWidget(fig)

#     def _update_zmax(self, change):
#         self.plot.data[0].update(zmax=change["new"])


# class STMNodesWidget(ipw.VBox):
#     def __init__(self, node, **kwargs):
#         self.node = node
#         self.list_calcs = list(self.node.keys())
#         self.dict_calcs = self.parse_strings_to_dicts(self.list_calcs)

#         self.calc_nodes = ipw.Dropdown(
#             options=self._get_calc_options(),  # List of available calculations
#             value=0,
#             description="Calculation:",
#             disabled=False,
#             style={"description_width": "initial"},
#             layout={"width": "600px"},
#         )

#         self.download_button = ipw.Button(
#             description="Download", button_style="primary"
#         )
#         self.plot = STMPlotWidget(
#             self.node[self.list_calcs[0]],
#             mode=self.dict_calcs[0]["mode"],
#             value=self.dict_calcs[0]["value"],
#         )

#         self.calc_nodes.observe(self._on_calc_change, names="value")

#         super().__init__(
#             children=[
#                 self.calc_nodes,
#                 self.plot,
#                 self.download_button,
#             ],
#             **kwargs,
#         )

#     def parse_strings_to_dicts(self, strings):
#         result = []
#         for s in strings:
#             parts = s.split("_")

#             # Extract and parse stm_bias value
#             if parts[2] == "neg":
#                 bias_sign = -1
#                 bias_index = 3
#             else:
#                 bias_sign = 1
#                 bias_index = 2

#             stm_bias_str = parts[bias_index] + "." + parts[bias_index + 1]
#             stm_bias = bias_sign * float(stm_bias_str)

#             # Extract mode and value
#             mode = parts[bias_index + 2]
#             value_str = parts[bias_index + 3] + "." + parts[bias_index + 4]
#             value = float(value_str)

#             # Create the dictionary
#             result.append({"stm_bias": stm_bias, "mode": mode, "value": value})

#         return result

#     def _get_calc_options(self):
#         return [
#             (
#                 f"STM Bias: {entry['stm_bias']} eV, Mode: {entry['mode']}, Value: {entry['value']} {'Å' if entry['mode'] == 'height' else 'pA'}",
#                 index,
#             )
#             for index, entry in enumerate(self.dict_calcs)
#         ]

#     def _on_calc_change(self, change):
#         self.plot = STMPlotWidget(
#             node=self.node[self.list_calcs[change["new"]]],
#             mode=self.dict_calcs[change["new"]]["mode"],
#             value=self.dict_calcs[change["new"]]["value"],
#         )
#         self.children = [self.calc_nodes, self.plot, self.download_button]
