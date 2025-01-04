import ipywidgets as ipw

from aiidalab_qe_pp.result.widgets.stmvisualmodel import STMVisualModel


class STMVisualWidget(ipw.VBox):
    """Widget to visualize the output data from PPWorkChain."""

    def __init__(self, model: STMVisualModel, node, **kwargs):
        super().__init__(
            children=[ipw.HTML("Loading STM data...")],
            **kwargs,
        )
        self._model = model
        self._model.node = node

    def render(self):
        if self.rendered:
            return

        self.calc_nodes = ipw.Dropdown(
            # options=self._get_calc_options(),  # List of available calculations
            # value=0,
            description="Calculation:",
            disabled=False,
            style={"description_width": "initial"},
            layout={"width": "600px"},
        )
        ipw.link((self.calc_nodes, "value"), (self._model, "calc_node"))
        ipw.dlink((self._model, "calc_node_options"), (self.calc_nodes, "options"))

        self.download_button = ipw.Button(
            description="Download", button_style="primary"
        )

        self.children = [self.calc_nodes, self.download_button]
        self._model.fetch_data()
        self.rendered = True
