import ipywidgets as ipw

from aiidalab_qe_pp.result.widgets.wfnvisualmodel import WfnVisualModel
from weas_widget import WeasWidget


class WfnVisualWidget(ipw.VBox):
    def __init__(self, model: WfnVisualModel, node, **kwargs):
        super().__init__(
            children=[ipw.HTML("Loading wfn data...")],
            **kwargs,
        )
        self._model = model
        self._model.node = node
        self._model.fetch_data()
        self.rendered = False

    def render(self):
        if self.rendered:
            return

        self.guiConfig = {
            "enabled": True,
            "components": {
                "atomsControl": True,
                "buttons": True,
                "cameraControls": True,
            },
            "buttons": {
                "fullscreen": True,
                "download": True,
                "measurement": True,
            },
        }

        self.kpoints_dropdown = ipw.Dropdown(
            description="Kpoint:",
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        ipw.dlink(
            (self._model, "kpoints_dropdown_options"),
            (self.kpoints_dropdown, "options"),
        )
        ipw.link((self._model, "kpoint"), (self.kpoints_dropdown, "value"))
        self.kpoints_dropdown.observe(self._on_kpoints_change, "value")

        self.bands_dropdown = ipw.Dropdown(
            description="Band:",
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        ipw.dlink(
            (self._model, "bands_dropdown_options"), (self.bands_dropdown, "options")
        )
        ipw.link((self._model, "band"), (self.bands_dropdown, "value"))
        self.bands_dropdown.observe(self._on_band_change, "value")

        self.spin = ipw.Dropdown(
            description="Spin:",
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        ipw.dlink((self._model, "spin_options"), (self.spin, "options"))
        ipw.link((self._model, "spin"), (self.spin, "value"))
        ipw.link(
            (self._model, "spin_displayed"),
            (self.spin.layout, "display"),
        )
        self.spin.observe(self._on_spin_change, "value")

        self.controls = ipw.HBox(
            [self.kpoints_dropdown, self.bands_dropdown, self.spin]
        )

        self.download_button = ipw.Button(
            description="Download Cube", button_style="primary"
        )
        self.download_button.on_click(self._model.download_cube)

        self.plot = WeasWidget(guiConfig=self.guiConfig)
        self.plot.from_ase(self._model.input_structure)
        self.plot.avr.color_type = "JMOL"
        self.plot.avr.model_style = 1
        self._update_plot()
        self.children = [self.controls, self.plot, self.download_button]
        self.rendered = True

    def _update_plot(self):
        cube_data, isovalue = self._model.update_plot()
        self.plot.avr.iso.volumetric_data = {"values": cube_data}
        self.plot.avr.iso.settings = {
            "positive": {"isovalue": isovalue},
            "negative": {"isovalue": -isovalue, "color": "yellow"},
        }
        self.plot.avr.draw()

    def _on_kpoints_change(self, _):
        self._model.on_kpoints_change()
        self._update_plot()

    def _on_band_change(self, _):
        self._update_plot()

    def _on_spin_change(self, _):
        self._update_plot()
