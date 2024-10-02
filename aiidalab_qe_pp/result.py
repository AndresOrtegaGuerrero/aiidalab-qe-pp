from aiidalab_qe.common.panel import ResultPanel
import ipywidgets as ipw

from .widgets import CubeVisualWidget, WfnVisualWidget, STMNodesWidget

import re


def expand_kpoint_band_string(s):
    match = re.match(r"kp_(\d+)_kb_(\d+)_(\d+)", s)
    if match:
        kpoint = match.group(1)
        start_band = int(match.group(2))
        end_band = int(match.group(3))

        return [f"kp_{kpoint}_kb_{band}" for band in range(start_band, end_band + 1)]
    else:
        raise ValueError("String format is not correct")


def cube_data_dict(node):
    data_dict = {}

    for key in node.outputs.pp.wfn.keys():
        if hasattr(node.outputs.pp.wfn[key], "output_data_multiple"):
            labels = expand_kpoint_band_string(key)
            output_data_multiple = node.outputs.pp.wfn[key].output_data_multiple

            for i, output_key in enumerate(output_data_multiple.keys()):
                data_dict[labels[i]] = output_data_multiple[output_key]
        elif hasattr(node.outputs.pp.wfn[key], "output_data"):
            data_dict[key] = node.outputs.pp.wfn[key].output_data
    return data_dict


def process_orbitals(data):
    orbitals = data["orbitals"]
    kpoint_band_dict = {}

    for orbital in orbitals:
        kpoint = orbital["kpoint"]
        if "kband(2)" in orbital:
            bands = list(range(orbital["kband(1)"], orbital["kband(2)"] + 1))
        else:
            bands = [orbital["kband(1)"]]

        if kpoint not in kpoint_band_dict:
            kpoint_band_dict[kpoint] = set()

        kpoint_band_dict[kpoint].update(bands)

    # Convert the dictionary to the desired list format
    kpoint_band_data = [
        {"kpoint": kpoint, "bands": sorted(list(bands))}
        for kpoint, bands in kpoint_band_dict.items()
    ]

    return kpoint_band_data


class Result(ResultPanel):
    title = "PP Results"
    workchain_label = "pp"

    def __init__(self, node=None, **kwargs):
        super().__init__(node=node, identifier="pp", **kwargs)

        self.viewer_charge_dens = None
        self.viewer_spin_dens = None
        self.viewer_wfn = None
        self.viewer_ildos = None
        self.viewer_stm = None

        self.result_tabs = ipw.Tab()
        self.result_tabs.observe(self._on_tab_change, names="selected_index")
        self._update_view()

    def _update_view(self):
        children_result_widget = []
        tab_titles = []

        output_types = [
            ("charge_dens", "Charge Density", "viewer_charge_dens"),
            ("spin_dens", "Spin Density", "viewer_spin_dens"),
            ("wfn", "Orbitals", "viewer_wfn"),
            ("ildos", "ILDOS", "viewer_ildos"),
            ("stm", "STM", "viewer_stm"),
        ]

        for data_key, title, viewer_var in output_types:
            viewer = self.create_viewer(data_key)
            if viewer:
                setattr(self, viewer_var, viewer)
                # setattr(self, f"viewer_{data_key}", viewer)  # Optionally, you can also set specific attributes for each viewer
                tab_titles.append(title)
                children_result_widget.append(getattr(self, viewer_var))

        self.result_tabs.children = children_result_widget
        for index, title in enumerate(tab_titles):
            self.result_tabs.set_title(index, title)

        self.children = [self.result_tabs]

    def _on_tab_change(self, change):
        selected_index = change["new"]
        if selected_index is not None:
            for viewer_var in [
                "viewer_charge_dens",
                "viewer_spin_dens",
                "viewer_wfn",
                "viewer_ildos",
                "viewer_stm",
            ]:
                result_viewer = getattr(self, viewer_var, None)
                if result_viewer:
                    result_viewer.viewer._widget.send_js_task(
                        {"name": "tjs.onWindowResize", "kwargs": {}}
                    )
                    result_viewer.viewer._widget.send_js_task(
                        {
                            "name": "tjs.updateCameraAndControls",
                            "kwargs": {"direction": [0, -100, 0]},
                        }
                    )

    def create_viewer(self, data_key):
        """Creates a CubeVisualWidget or WfnVisualWidget viewer based on the data key."""
        try:
            data_output = getattr(self.node.outputs.pp, data_key)
            if data_key not in ["wfn", "stm"]:
                viewer = CubeVisualWidget(
                    structure=self.node.inputs.pp.structure,
                    cube_data=data_output.output_data.get_array("data"),
                    plot_num=data_key,
                )
                return viewer

            elif data_key == "stm":
                node = self.node.outputs.pp.stm
                viewer = STMNodesWidget(node=node)
                return viewer

            elif data_key == "wfn":
                data_dict = cube_data_dict(self.node)
                orbitals = process_orbitals(self.node.inputs.pp.parameters["wfn"])
                viewer = WfnVisualWidget(
                    structure=self.node.inputs.pp.structure,
                    cube_data_dict=data_dict,
                    kpoint_band_data=orbitals,
                    number_of_k_points=self.node.inputs.pp.parameters.get_dict()["wfn"][
                        "number_of_k_points"
                    ],
                    lsda=self.node.inputs.pp.parameters.get_dict()["wfn"]["lsda"],
                    # plot_num=data_key
                )
                return viewer

        except AttributeError:
            # print(f"AttributeError while creating viewer for key: {data_key}, Error: {e}")
            return None
