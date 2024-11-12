"""
Callback definitions for widget interactions.
"""

from ..core.constants import colors


class SliderCallbacks:
    """
    Class to manage slider callbacks with proper state management.
    """

    def __init__(self, render_window):
        """
        Initialize callback manager with render window reference.

        Args:
            render_window: VTK render window instance
        """
        self.render_window = render_window
        self._actors = {}
        self._value_texts = {}

    def register_actor(self, name, actor):
        """Register an actor for callback usage."""
        self._actors[name] = actor

    def register_value_text(self, name, text_actor):
        """Register a text actor for value updates."""
        self._value_texts[name] = text_actor

    def create_color_callback(self):
        """Create callback for color slider."""

        def color_callback(obj, event):
            slider_rep = obj.GetRepresentation()
            value = slider_rep.GetValue()
            if "cylinder" in self._actors:
                self._actors["cylinder"].GetProperty().SetColor(value, 0.0, 1.0 - value)
            if "color" in self._value_texts:
                self._value_texts["color"].SetInput(f"{value:.2f}")
                self._value_texts["color"].Modified()
            self.render_window.Render()

        return color_callback

    def create_resolution_callback(self, cylinder_source):
        """Create callback for resolution slider."""

        def resolution_callback(obj, event):
            slider_rep = obj.GetRepresentation()
            value = int(slider_rep.GetValue())
            cylinder_source.SetResolution(value)
            if "resolution" in self._value_texts:
                self._value_texts["resolution"].SetInput(str(value))
                self._value_texts["resolution"].Modified()
            self.render_window.Render()

        return resolution_callback

    def create_ratio_callback(self, cylinder_source):
        """Create callback for height/width ratio slider."""

        def ratio_callback(obj, event):
            slider_rep = obj.GetRepresentation()
            value = slider_rep.GetValue()
            cylinder_source.SetHeight(value)
            if "ratio" in self._value_texts:
                self._value_texts["ratio"].SetInput(f"{value:.2f}")
                self._value_texts["ratio"].Modified()
            self.render_window.Render()

        return ratio_callback
