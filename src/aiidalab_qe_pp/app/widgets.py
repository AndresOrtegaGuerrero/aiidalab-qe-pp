import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets as tl


# Cube Visual Widget

"""Inspired and adapted from https://github.com/nanotech-empa/aiidalab-empa-surfaces/blob/master/surfaces_tools/widgets/pdos.py(author: yakutovicha)"""


class HorizontalItemWidget(ipw.HBox):
    stack_class = None

    def __init__(self, *args, **kwargs):
        # Delete button.
        self.delete_button = ipw.Button(
            description="x", button_style="danger", layout={"width": "30px"}
        )
        self.delete_button.on_click(self.delete_myself)

        children = kwargs.pop("children", [])
        children.append(self.delete_button)

        super().__init__(*args, children=children, **kwargs)

    def delete_myself(self, _):
        self.stack_class.delete_item(self)


class VerticalStackWidget(ipw.VBox):
    items = tl.Tuple()
    item_class = None

    def __init__(self, item_class, add_button_text="Add"):
        self.item_class = item_class

        self.add_item_button = ipw.Button(
            description=add_button_text, button_style="info"
        )
        self.add_item_button.on_click(self.add_item)

        self.items_output = ipw.VBox()
        tl.link((self, "items"), (self.items_output, "children"))

        # Outputs.
        self.add_item_message = awb.utils.StatusHTML()
        super().__init__(
            children=[
                self.items_output,
                self.add_item_button,
                self.add_item_message,
            ]
        )

    def add_item(self, _):
        self.items += (self.item_class(),)

    @tl.observe("items")
    def _observe_fragments(self, change):
        """Update the list of fragments."""
        if change["new"]:
            self.items_output.children = change["new"]
            for item in change["new"]:
                item.stack_class = self
        else:
            self.items_output.children = []

    def delete_item(self, item):
        try:
            index = self.items.index(item)
        except ValueError:
            return
        self.items = self.items[:index] + self.items[index + 1 :]
        del item

    def length(self):  # This function we can delete it ... it is not used
        return len(self.items)


class OrbitalSelectionWidget(HorizontalItemWidget):
    def __init__(self):
        self.kpoint = ipw.BoundedIntText(
            description="Kpoint:",
            min=1,
            max=1000,
            step=1,
            value=0,
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        self.kbands = ipw.Text(
            description="Bands:",
            placeholder="e.g. 1..5 8 10",
            value="",
            style={"description_width": "initial"},
            layout={"width": "150px"},
        )
        super().__init__(children=[self.kbands, self.kpoint])
        # Add observers to kbands and kpoint
        self.kpoint.observe(self._trigger_update, names="value")
        self.kbands.observe(self._trigger_update, names="value")

    def _trigger_update(self, change):
        # Notify parent widget to update orbitals
        if hasattr(self, "parent_widget"):
            self.parent_widget._update_orbitals()


class OrbitalListWidget(VerticalStackWidget, tl.HasTraits):
    orbitals = tl.List([])
    max_kpoint = tl.Int()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observe(self._update_orbitals, names="items")

    def add_item(self, _):
        item = self.item_class()
        # Observe changes in kpoint and kbands for each item
        item.kpoint.observe(self._on_kpoint_change, names="value")
        item.kbands.observe(self._on_kbands_change, names="value")
        item.kpoint.max = self.max_kpoint
        self.items += (item,)

    def reset(self):
        self.items = []
        self._update_orbitals()

    def _on_kpoint_change(self, change):
        """Triggered when kpoint value changes."""
        self._update_orbitals()

    def _on_kbands_change(self, change):
        """Triggered when kbands value changes."""
        self._update_orbitals()

    def _update_orbitals(self, *_):
        """Update the orbitals trait when items change."""
        self.orbitals = [(item.kbands.value, item.kpoint.value) for item in self.items]
