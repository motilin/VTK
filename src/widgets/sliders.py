"""
Custom slider widgets and related functionality.
"""

from vtkmodules.vtkRenderingCore import vtkTextActor
from vtkmodules.vtkInteractionWidgets import (
    vtkSliderRepresentation2D,
    vtkSliderWidget,
)
from ..core.constants import (
    SLIDER_START_X,
    SLIDER_WIDTH,
    SLIDER_HEIGHT,
    WINDOW_HEIGHT,
    colors,
)


class SliderManager:
    """
    Manages creation and organization of slider widgets.
    """

    def __init__(self, renderer, interactor):
        self.renderer = renderer
        self.interactor = interactor
        self.sliders = {}
        self.value_texts = {}

    def create_slider(self, name, index, min_val, max_val, init_val, callback, title):
        """
        Create a new slider with associated text actors.
        """
        height = WINDOW_HEIGHT - SLIDER_HEIGHT * index

        # Create slider representation
        slider_rep = vtkSliderRepresentation2D()
        slider_rep.SetMinimumValue(min_val)
        slider_rep.SetMaximumValue(max_val)
        slider_rep.SetValue(init_val)
        slider_rep.GetPoint1Coordinate().SetCoordinateSystemToDisplay()
        slider_rep.GetPoint1Coordinate().SetValue(SLIDER_START_X, height)
        slider_rep.GetPoint2Coordinate().SetCoordinateSystemToDisplay()
        slider_rep.GetPoint2Coordinate().SetValue(SLIDER_START_X + SLIDER_WIDTH, height)
        self._configure_slider_appearance(slider_rep)

        # Create slider widget
        slider_widget = vtkSliderWidget()
        slider_widget.SetInteractor(self.interactor)
        slider_widget.SetRepresentation(slider_rep)
        slider_widget.AddObserver("InteractionEvent", callback)
        slider_widget.EnabledOn()

        # Create text actors
        title_text = self._create_text_actor(
            title, SLIDER_START_X + SLIDER_WIDTH + 10, height - 10
        )
        value_text = self._create_text_actor(
            f"{init_val:.2f}", SLIDER_START_X - 50, height - 10
        )

        # Store references
        self.sliders[name] = slider_widget
        self.value_texts[name] = value_text

        # Add actors to renderer
        self.renderer.AddActor(title_text)
        self.renderer.AddActor(value_text)

        return slider_widget, value_text

    def _configure_slider_appearance(self, slider_rep):
        """Configure the appearance of a slider representation."""
        slider_rep.SetSliderLength(0.0001)
        slider_rep.SetSliderWidth(0.02)
        slider_rep.SetEndCapLength(0.01)
        slider_rep.SetEndCapWidth(0.03)
        slider_rep.SetTubeWidth(0.005)
        slider_rep.GetTubeProperty().SetColor(colors.GetColor3d("Gray"))
        slider_rep.ShowSliderLabelOff()

    def _create_text_actor(self, text, x, y):
        """Create a text actor with specified position and text."""
        text_actor = vtkTextActor()
        text_actor.SetInput(text)
        text_actor.GetTextProperty().SetFontSize(16)
        text_actor.GetTextProperty().SetColor(colors.GetColor3d("White"))
        text_actor.SetPosition(x, y)
        return text_actor
