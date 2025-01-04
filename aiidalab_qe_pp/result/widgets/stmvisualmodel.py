from aiidalab_qe.common.mvc import Model
from aiida.orm.nodes.process.workflow.workchain import WorkChainNode
import traitlets as tl


SETTINGS = {
    "margin": {"l": 50, "r": 50, "b": 50, "t": 80},
    "button_layer_1_height": 1.3,
    "width": 800,
    "height": 600,
    "color_scales": ["Hot", "Cividis", "Greys", "Viridis"],
    "default_color_scale": "Hot",
}


class STMVisualModel(Model):
    node = tl.Instance(WorkChainNode, allow_none=True)
    calc_node = tl.Int(0)
    calc_node_options = tl.List(
        trait=tl.List(tl.Union([tl.Unicode(), tl.Int()])), default_value=[]
    )

    list_calcs = tl.List(trait=tl.Unicode(), default_value=[])
    dict_calcs = tl.List(trait=tl.Dict(), default_value=[])

    def fetch_data(self):
        self.list_calcs = list(self.node.keys())
        self.dict_calcs = self.parse_strings_to_dicts(self.list_calcs)
        self.calc_node_options = self._get_calc_options()

    def _get_calc_options(self):
        return [
            (
                f"STM Bias: {entry['stm_bias']} eV, Mode: {entry['mode']}, Value: {entry['value']} {'Å' if entry['mode'] == 'height' else 'pA'}",
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
