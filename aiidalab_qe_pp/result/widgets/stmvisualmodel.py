from aiidalab_qe.common.mvc import Model
import traitlets as tl
from aiida.common.extendeddicts import AttributeDict
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata
from IPython.display import display
import base64
import json

SETTINGS = {
    "margin": {"l": 50, "r": 50, "b": 50, "t": 80},
    "button_layer_1_height": 1.3,
    "width": 800,
    "height": 600,
    "color_scales": ["Hot", "Cividis", "Greys", "Viridis"],
    "default_color_scale": "Hot",
}


class STMVisualModel(Model):
    node = tl.Instance(AttributeDict, allow_none=True)
    calc_node = tl.Int(0)
    calc_node_options = tl.List(
        trait=tl.List(tl.Union([tl.Unicode(), tl.Int()])), default_value=[]
    )

    list_calcs = tl.List(trait=tl.Unicode(), default_value=[])
    dict_calcs = tl.List(trait=tl.Dict(), default_value=[])

    x_cart = tl.Instance(np.ndarray, allow_none=True)
    y_cart = tl.Instance(np.ndarray, allow_none=True)
    f_stm = tl.Instance(np.ndarray, allow_none=True)

    unique_x = tl.Instance(np.ndarray, allow_none=True)
    unique_y = tl.Instance(np.ndarray, allow_none=True)

    x_grid = tl.Instance(np.ndarray, allow_none=True)
    y_grid = tl.Instance(np.ndarray, allow_none=True)
    z_grid = tl.Instance(np.ndarray, allow_none=True)

    stm_bias = tl.Float(0.0)
    mode = tl.Unicode("height")
    value = tl.Float(0.0)

    zmax = tl.Float(0.0)
    zmax_min = tl.Float(0.0)
    zmax_max = tl.Float(0.0)
    zmax_step = tl.Float(0.0)

    # For images

    image_format_options = tl.List(
        trait=tl.Unicode(), default_value=["png", "jpeg", "svg", "pdf"]
    )
    image_format = tl.Unicode("png")

    def fetch_data(self):
        self.list_calcs = list(self.node.keys())
        self.dict_calcs = self.parse_strings_to_dicts(self.list_calcs)
        self.calc_node_options = self._get_calc_options()
        self._on_change_calc_node()

    def _on_change_calc_node(self):
        self.stm_bias = self.dict_calcs[self.calc_node]["stm_bias"]
        self.mode = self.dict_calcs[self.calc_node]["mode"]
        self.value = self.dict_calcs[self.calc_node]["value"]
        self.x_cart = self.node[self.list_calcs[self.calc_node]]["stm_data"].get_array(
            "xcart"
        )
        self.y_cart = self.node[self.list_calcs[self.calc_node]]["stm_data"].get_array(
            "ycart"
        )
        self.f_stm = self.node[self.list_calcs[self.calc_node]]["stm_data"].get_array(
            "fstm"
        )
        self._process_data()
        self.zmax = np.max(self.z_grid)
        self.zmax_min = np.min(self.z_grid)
        self.zmax_max = np.max(self.z_grid)
        self.zmax_step = (np.max(self.z_grid) - np.min(self.z_grid)) / 100

    def update_plot(self):
        self._on_change_calc_node()
        # Clear existing data
        self.plot.data = []
        # Add new heatmap trace
        new_data = self._update_data()  # This returns a list with a heatmap
        self.plot.add_traces(new_data)
        self.update_layout(self.plot)

    def update_plot_zmax(self):
        self.plot.data[0].update(zmax=self.zmax)

    def _get_calc_options(self):
        return [
            (
                f"STM Bias: {entry['stm_bias']} eV, Mode: {entry['mode']}, Value: {entry['value']} {'Å' if entry['mode'] == 'height' else '(au)'}",
                index,
            )
            for index, entry in enumerate(self.dict_calcs)
        ]

    def parse_strings_to_dicts(self, strings):
        result = []
        for s in strings:
            parts = s.split("_")

            # Extract and parse stm_bias value
            if parts[2] == "neg":
                bias_sign = -1
                bias_index = 3
            else:
                bias_sign = 1
                bias_index = 2

            stm_bias_str = parts[bias_index] + "." + parts[bias_index + 1]
            stm_bias = bias_sign * float(stm_bias_str)

            # Extract mode and value
            mode = parts[bias_index + 2]
            value_str = parts[bias_index + 3] + "." + parts[bias_index + 4]
            value = float(value_str)

            # Create the dictionary
            result.append({"stm_bias": stm_bias, "mode": mode, "value": value})

        return result

    def _process_data(self):
        valid_indices = (
            ~np.isnan(self.x_cart) & ~np.isnan(self.y_cart) & ~np.isnan(self.f_stm)
        )
        x_valid = self.x_cart[valid_indices]
        y_valid = self.y_cart[valid_indices]
        z_valid = self.f_stm[valid_indices]

        epsilon = 1e-6
        self.unique_x = np.unique(np.where(np.abs(x_valid) < epsilon, 0, x_valid))
        self.unique_y = np.unique(np.where(np.abs(y_valid) < epsilon, 0, y_valid))

        X, Y = np.meshgrid(self.unique_x, self.unique_y)
        Z = griddata((x_valid, y_valid), z_valid, (X, Y), method="cubic")

        self.x_grid = X
        self.y_grid = Y
        self.z_grid = Z

    def _update_data(self):
        heatmap = go.Heatmap(
            z=self.z_grid,
            x=self.unique_x,
            y=self.unique_y,
            colorscale=SETTINGS["default_color_scale"],
            colorbar=dict(
                title=f"{'Distance to the surface (Å)' if self.mode == 'current' else 'Electron density (a.u.)'}"
            ),
        )
        return [heatmap]

    def create_plot(self):
        fig = go.Figure(data=self._update_data())
        self.update_layout(fig)
        self.plot = go.FigureWidget(fig)

    def update_layout(self, fig):
        fig.update_layout(
            # Title settings
            title=dict(
                text=f"Constant {self.mode} plot, {self.value} {'Å' if self.mode == 'height' else '(au)'}",
                x=0.5,  # Center the title
                y=0.85,  # Adjust the vertical position of the title
                xanchor="center",
                yanchor="top",
            ),
            # X-axis settings
            xaxis=dict(
                title="x (Å)",
                range=[np.min(self.unique_x), np.max(self.unique_x)],
                tickmode="auto",
                ticks="outside",
                showline=True,
                mirror=True,
                showgrid=False,
            ),
            # Y-axis settings
            yaxis=dict(
                title="y (Å)",
                range=[np.min(self.unique_y), np.max(self.unique_y)],
                tickmode="auto",
                ticks="outside",
                showline=True,
                mirror=True,
                showgrid=False,
            ),
            # General layout settings
            autosize=False,
            width=SETTINGS["width"],
            height=SETTINGS["height"],
            margin=SETTINGS["margin"],
            # Update menus for interactivity
            updatemenus=[
                dict(
                    buttons=[
                        dict(
                            args=["colorscale", colorscale],
                            label=colorscale,
                            method="restyle",
                        )
                        for colorscale in SETTINGS["color_scales"]
                    ],
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=SETTINGS["button_layer_1_height"],
                    yanchor="top",
                ),
                dict(
                    buttons=[
                        dict(
                            args=["reversescale", False],
                            label="False",
                            method="restyle",
                        ),
                        dict(
                            args=["reversescale", True],
                            label="True",
                            method="restyle",
                        ),
                    ],
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.39,
                    xanchor="left",
                    y=SETTINGS["button_layer_1_height"],
                    yanchor="top",
                ),
            ],
            # Annotations for the layout
            annotations=[
                dict(
                    text="Colorscale",
                    x=-0.03,
                    xref="paper",
                    y=SETTINGS["button_layer_1_height"] - 0.05,
                    yref="paper",
                    align="left",
                    showarrow=False,
                ),
                dict(
                    text="Reverse<br>Colorscale",
                    x=0.26,
                    xref="paper",
                    y=SETTINGS["button_layer_1_height"] - 0.025,
                    yref="paper",
                    showarrow=False,
                ),
            ],
        )

    def download_image(self, _=None):
        """
        Downloads the current plot as an image in the format specified by self.image_format.
        """
        # Define the filename
        filename = f"stm_plot.{self.image_format}"

        # Generate the image in the specified format
        image_payload = self.plot.to_image(format=self.image_format)

        # Encode the image payload to base64
        import base64

        image_payload_base64 = base64.b64encode(image_payload).decode("utf-8")

        # Call the download helper method
        self._download_image(payload=image_payload_base64, filename=filename)

    @staticmethod
    def _download_image(payload, filename):
        from IPython.display import Javascript

        # Safely format the JavaScript code
        javas = Javascript(
            """
            var link = document.createElement('a');
            link.href = 'data:image/{format};base64,{payload}';
            link.download = "{filename}";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            """.format(
                payload=payload, filename=filename, format=filename.split(".")[-1]
            )
        )
        display(javas)

    def download_data(self, _=None):
        filename = "stm_calculation.json"
        my_dict = {
            "STM Bias (eV)": self.stm_bias,
            "Mode": self.mode,
            "Value": self.value,
            "fstm": self.f_stm.tolist(),
            "x_cart": self.x_cart.tolist(),
            "y_cart": self.y_cart.tolist(),
        }

        json_str = json.dumps(my_dict)
        b64_str = base64.b64encode(json_str.encode()).decode()
        self._download(payload=b64_str, filename=filename)

    @staticmethod
    def _download(payload, filename):
        from IPython.display import Javascript

        javas = Javascript(
            """
            var link = document.createElement('a');
            link.href = 'data:text/json;charset=utf-8;base64,{payload}'
            link.download = "{filename}"
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            """.format(payload=payload, filename=filename)
        )
        display(javas)
