from aiidalab_qe.common.panel import ResultsModel
import traitlets as tl


class PpResultsModel(ResultsModel):
    title = "Post-processing"
    identifier = "pp"

    _this_process_label = "PPWorkChain"

    tab_titles = tl.List([])

    def get_pp_node(self):
        return self._get_child_outputs()

    def needs_charge_dens_tab(self):
        node = self.get_pp_node()
        return "charge_dens" in node

    def needs_spin_dens_tab(self):
        node = self.get_pp_node()
        return "spin_dens" in node

    def needs_potential_tab(self):
        node = self.get_pp_node()
        return "potential" in node

    def needs_wfn_tab(self):
        node = self.get_pp_node()
        return "wfn" in node

    def needs_ildos_tab(self):
        node = self.get_pp_node()
        return "ildos" in node

    def needs_stm_tab(self):
        node = self.get_pp_node()
        return "stm" in node

    def needs_ldos_tab(self):
        node = self.get_pp_node()
        return "ldos_grid" in node

    def needs_ildos_stm_tab(self):
        node = self.get_pp_node()
        return "ildos_stm" in node
