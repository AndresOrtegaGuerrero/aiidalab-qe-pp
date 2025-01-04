"""PP Plugin results panel."""

from aiidalab_qe.common.panel import ResultsPanel
from aiidalab_qe_pp.result.model import PpResultsModel
import ipywidgets as ipw


class PpResultsPanel(ResultsPanel[PpResultsModel]):
    title = "Pp Results"
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
        # pp_node = self._model.get_pp_node()

        needs_charge_dens = self._model.needs_charge_dens_tab()

        if needs_charge_dens:
            tab_data.append(("charge_dens", "Charge Density", "viewer_charge_dens"))

        needs_spin_dens = self._model.needs_spin_dens_tab()
        if needs_spin_dens:
            print("spin_dens")
            tab_data.append(("spin_dens", "Spin Density", "viewer_spin_dens"))

        needs_wfn = self._model.needs_wfn_tab()
        if needs_wfn:
            tab_data.append(("wfn", "Orbitals", "viewer_wfn"))

        needs_ildos = self._model.needs_ildos_tab()
        if needs_ildos:
            tab_data.append(("ildos", "ILDOS", "viewer_ildos"))

        needs_stm = self._model.needs_stm_tab()
        if needs_stm:
            tab_data.append(("stm", "STM", "viewer_stm"))

        # Assign children and titles dynamically
        self.tabs.children = [content for _, content in tab_data]
        for index, (title, _) in enumerate(tab_data):
            self.tabs.set_title(index, title)

        self.children = [self.tabs]
        self.rendered = True
        self.tabs.selected_index = 0

    # def _on_tab_change(self, change):
    #     if (tab_index := change["new"]) is None:
    #         return
    #     self.tabs.children[tab_index].render()  # type: ignore
