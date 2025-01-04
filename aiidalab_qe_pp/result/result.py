"""PP Plugin results panel."""

from aiidalab_qe.common.panel import ResultsPanel
from aiidalab_qe_pp.result.model import PpResultsModel
import ipywidgets as ipw

from aiidalab_qe_pp.result.widgets.cubevisualmodel import CubeVisualModel
from aiidalab_qe_pp.result.widgets.cubevisualwidget import CubeVisualWidget


class PpResultsPanel(ResultsPanel[PpResultsModel]):
    title = "Post-processing"
    identifier = "pp"
    workchain_labels = ["pp"]

    def render(self):
        if self.rendered:
            return

        self.tabs = ipw.Tab(
            layout=ipw.Layout(min_height="250px"),
            selected_index=None,
        )
        self.tabs.observe(
            self._on_tab_change,
            "selected_index",
        )

        tab_data = []
        pp_node = self._model.get_pp_node()

        needs_charge_dens = self._model.needs_charge_dens_tab()

        if needs_charge_dens:
            node = self._model.fetch_child_process_node()
            cube_data = pp_node.charge_dens.output_data.get_array("data")
            plot_num = "charge_dens"
            cube_visual_model = CubeVisualModel()
            cube_visual_widget = CubeVisualWidget(
                cube_visual_model, node, cube_data, plot_num
            )
            tab_data.append(("Charge density", cube_visual_widget))

        needs_spin_dens = self._model.needs_spin_dens_tab()
        if needs_spin_dens:
            node = self._model.fetch_child_process_node()
            cube_data = pp_node.spin_dens.output_data.get_array("data")
            plot_num = "spin_dens"
            cube_visual_model = CubeVisualModel()
            cube_visual_widget = CubeVisualWidget(
                cube_visual_model, node, cube_data, plot_num
            )

            tab_data.append(("Spin density", cube_visual_widget))

        needs_wfn = self._model.needs_wfn_tab()
        if needs_wfn:
            tab_data.append(("wfn", "Orbitals"))

        needs_ildos = self._model.needs_ildos_tab()
        if needs_ildos:
            node = self._model.fetch_child_process_node()
            cube_data = pp_node.ildos.output_data.get_array("data")
            plot_num = "ildos"
            cube_visual_model = CubeVisualModel()
            cube_visual_widget = CubeVisualWidget(
                cube_visual_model, node, cube_data, plot_num
            )
            tab_data.append(("ILDOS", cube_visual_widget))

        needs_stm = self._model.needs_stm_tab()
        if needs_stm:
            tab_data.append(("stm", "STM"))

        # Assign children and titles dynamically
        self.tabs.children = [content for _, content in tab_data]
        for index, (title, _) in enumerate(tab_data):
            self.tabs.set_title(index, title)

        self.children = [self.tabs]
        self.rendered = True
        self.tabs.selected_index = 0

    def _on_tab_change(self, change):
        if (tab_index := change["new"]) is None:
            return
        self.tabs.children[tab_index].render()  # type: ignore
