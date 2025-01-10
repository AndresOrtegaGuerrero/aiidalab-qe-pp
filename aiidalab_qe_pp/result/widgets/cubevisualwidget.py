import ipywidgets as ipw
from weas_widget import WeasWidget
from aiidalab_qe_pp.result.widgets.cubevisualmodel import CubeVisualModel
import numpy as np


class CubeVisualWidget(ipw.VBox):
    """Widget to visualize the output data from PPWorkChain."""

    def __init__(self, model: CubeVisualModel, node, cube_data, plot_num, **kwargs):
        super().__init__(
            children=[ipw.HTML("Loading Cube data...")],
            **kwargs,
        )
        self._model = model
        self._model.node = node
        self._model.cube_data = cube_data
        self._model.plot_num = plot_num
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
        # WeasWidget Setting
        self.viewer = WeasWidget(guiConfig=self.guiConfig)
        self.viewer.from_ase(self._model.input_structure)
        isovalue = 2 * np.std(self._model.cube_data) + np.mean(self._model.cube_data)
        self.viewer.avr.iso.volumetric_data = {"values": self._model.cube_data}
        self.viewer.avr.iso.settings = {
            "positive": {"isovalue": isovalue},
            "negative": {"isovalue": -isovalue, "color": "yellow"},
        }
        self.viewer.avr.color_type = "JMOL"
        self.viewer.avr.model_style = 1

        # Display Button
        self.display_button = ipw.Button(description="Display", button_style="primary")
        # Download Cubefile Button
        self.download_button = ipw.Button(
            description="Download", button_style="primary"
        )
        self.buttons = ipw.HBox([self.display_button, self.download_button])
        self.download_button.on_click(self._model.download_cube)
        self.display_button.on_click(self._model.display(self.viewer))

        self.children = [self.viewer, self.download_button]
        self.rendered = True
