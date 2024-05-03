from aiidalab_qe.common.panel import ResultPanel
import ipywidgets as ipw
from weas_widget import WeasWidget
class Result(ResultPanel):
    title = "PP Results"
    workchain_label = "pp"

    def __init__(self, node=None, **kwargs):
        super().__init__(node=node, identifier="pp", **kwargs)

        self.guiConfig = {
            "enabled": True,
            "components": {"atomsControl": True, "buttons": True},
            "buttons": {
                "fullscreen": True,
                "download": True,
                "measurement": True,
            },
        }

        self.display_button = ipw.Button(description="Display", button_style="primary")
        self.result_tabs = ipw.Tab()
        children_result_widget = []
        tab_titles = []

        # List of potential data outputs and their corresponding tab titles
        output_types = [
            ("charge_dens", "Charge Density"),
            ("spin_dens", "Spin Density"),
            ("wfn", "Kohn-Sham Wavefunctions"),
            ("ildos", "Integrated Local Density of States"),
            ("stm", "Scanning Tunneling Microscopy"),
        ]
        
        for data_key, title in output_types:
            viewer = self.create_viewer(data_key)
            if viewer:
                children_result_widget.append(viewer)
                tab_titles.append(title)

        self.result_tabs.children = children_result_widget
        for index, title in enumerate(tab_titles):
            self.result_tabs.set_title(index, title)
        self.display_button.on_click(self.update_children_result_widget)


    def _update_view(self):

        self.children = [self.display_button, self.result_tabs]


    def update_children_result_widget(self, _):
        for i in self.result_tabs.children:
            i._widget.send_js_task({"name": "tjs.onWindowResize", "kwargs": {}})
            i._widget.send_js_task(
                {
                    "name": "tjs.updateCameraAndControls",
                    "kwargs": {"direction": [0, -100, 0]},
                }
            )
            
    def fetch_node_outputs(self):
        output_types = {
            'charge_dens': "Charge Density",
            'spin_dens': "Spin Density",
            'wfn': "Kohn-Sham Wavefunctions",
            'ildos': "Integrated Local Density of States",
            'stm': "Scanning Tunneling Microscopy"
        }

        tab_titles = []
        outputs = {}

        for output_key, title in output_types.items():
            output_value = getattr(self.node.outputs.pp, output_key, None)
            if output_value is not None:
                tab_titles.append(title)
            outputs[output_key] = output_value

        return tab_titles, outputs

    def create_viewer(self, data_key):
        """Creates a WeasWidget viewer if the data is available."""
        try:
            data_output = getattr(self.node.outputs.pp, data_key).output_data
            viewer = WeasWidget(guiConfig=self.guiConfig)
            viewer.from_ase(self.node.inputs.pp.structure.get_ase())
            data = data_output.get_array("data")
            viewer.avr.iso.volumetric_data = {"values": data}
            viewer.avr.iso.settings = [{"isovalue": 0.001, "mode": 0}]

            return viewer
        except AttributeError:
            return None