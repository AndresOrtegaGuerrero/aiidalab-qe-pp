from aiidalab_qe.common.panel import ResultPanel
import ipywidgets as ipw
from weas_widget import WeasWidget

from .widgets import CubeVisualWdiget
class Result(ResultPanel):
    title = "PP Results"
    workchain_label = "pp"

    def __init__(self, node=None, **kwargs):
        super().__init__(node=node, identifier="pp", **kwargs)


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


    def _update_view(self):

        self.children = [self.result_tabs]
           
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
        """Creates a CubeVisualWdiget viewer if the data is available."""
        try:
            data_output = getattr(self.node.outputs.pp, data_key).output_data
            viewer = CubeVisualWdiget(structure=self.node.inputs.pp.structure, cube_data = data_output, plot_num=data_key)
            return viewer
        except AttributeError:
            return None