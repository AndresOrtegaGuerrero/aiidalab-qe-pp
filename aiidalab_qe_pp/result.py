from aiidalab_qe.common.panel import ResultPanel
import ipywidgets as ipw

class Result(ResultPanel):
    title = "PP Results"
    workchain_label = "pp"

    def __init__(self, node=None, **kwargs):
        super().__init__(node=node, identifier="pp", **kwargs)

    def _update_view(self):

        tab_titles = []
        children_result_widget = ()

        try:
            charge_dens = self.node.outputs.pp.outputs.charge_dens
            tab_titles.append("Charge Density")
        except AttributeError:
            charge_dens = None

        try:
            spin_dens = self.node.outputs.pp.outputs.spin_dens
            tab_titles.append("Spin Density")
        except AttributeError:
            spin_dens = None

        try:
            wfn = self.node.outputs.pp.outputs.wfn
            tab_titles.append("Kohn-Sham Wavefunctions")
        except AttributeError:
            wfn = None

        try:
            ildos = self.node.outputs.pp.outputs.ildos
            tab_titles.append("Integrated Local Density of States")
        except AttributeError:
            ildos = None

        try:
            stm = self.node.outputs.pp.outputs.stm 
            tab_titles.append("Scanning Tunneling Microscopy")
        except AttributeError:
            stm = None

        self.result_tabs = ipw.Tab(children=children_result_widget)

        for title_index in range(len(tab_titles)):
            self.result_tabs.set_title(title_index, tab_titles[title_index])

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