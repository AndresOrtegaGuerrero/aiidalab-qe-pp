from aiidalab_qe.common.mvc import Model
import traitlets as tl
from aiida.common.extendeddicts import AttributeDict
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from IPython.display import display
import base64
import json

SETTINGS = {
    "margin": {"l": 50, "r": 50, "b": 50, "t": 80},
    "button_layer_1_height": 1.3,
    "width": 800,
    "height": 600,
    "color_scales": ["Hot", "Cividis", "Greys", "Viridis", "Electric"],
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
    zmax_max = tl.Float(30.0)
    zmax_step = tl.Float(0.1)

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
        if "stm_data" in self.dict_calcs[self.calc_node]:
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
        self.zmax = np.nanmax(self.z_grid)
        self.zmax_min = np.nanmin(self.z_grid)
        self.zmax_max = np.nanmax(self.z_grid)
        self.zmax_step = (np.nanmax(self.z_grid) - np.nanmin(self.z_grid)) / 100

    def update_plot(self):
        self._on_change_calc_node()
        # Clear existing data
        current_colorscale = self.plot.data[0].colorscale
        self.plot.data = []
        # Add new heatmap trace
        new_data = self._update_data()  # This returns a list with a heatmap
        self.plot.add_traces(new_data)
        self.update_layout(self.plot, color_scale=current_colorscale)

    def update_plot_zmax(self):
        self.plot.data[0].update(zmax=self.zmax)

    def _get_calc_options(self):
        return [
            (
                (f"STM Bias: {entry['stm_bias']} eV, " if "stm_bias" in entry else "")
                + f"Mode: {entry['mode']}, Value: {entry['value']} {'Å' if entry['mode'] == 'height' else '(au)'}",
                index,
            )
            for index, entry in enumerate(self.dict_calcs)
        ]

    def parse_strings_to_dicts(self, strings):
        def parse_float(parts):
            if len(parts) == 1:
                return float(parts[0])
            elif len(parts) == 2:
                return float(parts[0] + "." + parts[1])
            return None

        result = []

        for s in strings:
            # Determine mode and extract value
            mode = next((m for m in ["height", "current"] if m in s), None)
            if not mode:
                continue

            start_index = s.find(mode)
            end_index = start_index + len(mode)
            mode_value = s[end_index + 1 :].split("_")
            value_float = parse_float(mode_value)
            if value_float is None:
                continue

            # Determine bias if present
            bias_value_float = None
            if "stm_bias" in s:
                bias_value = s[
                    s.find("stm_bias") + len("stm_bias") + 1 : start_index - 1
                ]
                bias_sign = -1 if "neg_" in bias_value else 1
                bias_to_split = bias_value.replace("neg_", "").split("_")
                bias_value_float = parse_float(bias_to_split)
                if bias_value_float is not None:
                    bias_value_float *= bias_sign

            # Construct result dictionary
            entry = {"mode": mode, "value": value_float}
            if bias_value_float is not None:
                entry["stm_bias"] = bias_value_float

            result.append(entry)

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

        # **Check if NaNs exist**
        if np.isnan(Z).any():
            # Create mask of NaNs
            nan_mask = np.isnan(Z)

            # Use Gaussian smoothing (fills NaNs without changing shape)
            Z_filled = gaussian_filter(Z, sigma=1)

            # Replace NaN values only
            Z[nan_mask] = Z_filled[nan_mask]

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

    def update_layout(self, fig, color_scale=SETTINGS["default_color_scale"]):
        with fig.batch_update():
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
            fig.update_traces(colorscale=color_scale)

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
            "Mode": self.mode,
            "Value": self.value,
            "fstm": self.f_stm.tolist(),
            "x_cart": self.x_cart.tolist(),
            "y_cart": self.y_cart.tolist(),
        }

        if "stm_bias" in self.dict_calcs[self.calc_node]:
            my_dict["STM Bias (eV)"] = self.stm_bias

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
