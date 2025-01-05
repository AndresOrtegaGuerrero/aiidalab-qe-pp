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
        self._model.fetch_data()
        self.rendered = False

    def render(self):
        if self.rendered:
            return

        self.calc_nodes = ipw.Dropdown(
            description="Calculation:",
            disabled=False,
            style={"description_width": "initial"},
            layout={"width": "600px"},
        )
        ipw.dlink((self._model, "calc_node_options"), (self.calc_nodes, "options"))
        ipw.link(
            (self._model, "calc_node"),
            (self.calc_nodes, "value"),
        )
        self.calc_nodes.observe(self._update_plot, "value")

        self.download_button = ipw.Button(
            description="Download Raw Data", button_style="primary"
        )

        self.zmax = ipw.BoundedFloatText(
            description="Z Max:",
            continuous_update=False,
        )
        ipw.link((self._model, "zmax"), (self.zmax, "value"))
        ipw.link((self._model, "zmax_min"), (self.zmax, "min"))
        ipw.link(
            (self._model, "zmax_max"),
            (self.zmax, "max"),
        )
        ipw.link((self._model, "zmax_step"), (self.zmax, "step"))
        self.zmax.observe(self._update_plot_zmax, "value")

        self.children = [self.calc_nodes, self.zmax, self.download_button]
        self.rendered = True

        self._initial_plot()

    def _initial_plot(self):
        self._model.create_plot()
        self.plot = self._model.plot
        self.children = [self.calc_nodes, self.plot, self.zmax, self.download_button]

    def _update_plot(self, _):
        self._model.update_plot()

    def _update_plot_zmax(self, _):
        self._model.update_plot_zmax()
