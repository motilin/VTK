import vtk


def create_axes(length=5, line_width=0.5, font_size=24, cone_radius=0.2):
    """
    Creates coordinate axes with larger labels and smaller arrow heads
    Parameters:
    -----------
    length : float
        Size of the axes
    line_width : float
        Width of the axis lines
    font_size : int
        Size of the X,Y,Z labels
    cone_radius : float
        Size of the arrow heads relative to default
    Returns:
    --------
    vtk.vtkAxesActor
        The customized axes actor
    """
    axes = vtk.vtkAxesActor()
    # Set the axes length
    axes.SetTotalLength(length, length, length)
    # Set line width
    axes.GetXAxisShaftProperty().SetLineWidth(line_width)
    axes.GetYAxisShaftProperty().SetLineWidth(line_width)
    axes.GetZAxisShaftProperty().SetLineWidth(line_width)
    # Customize labels
    axes.SetXAxisLabelText("x")
    axes.SetYAxisLabelText("y")
    axes.SetZAxisLabelText("z")

    # Create custom text properties for each axis caption
    for caption_actor in [
        axes.GetXAxisCaptionActor2D(),
        axes.GetYAxisCaptionActor2D(),
        axes.GetZAxisCaptionActor2D(),
    ]:
        # Enable caption scaling
        caption_actor.SetCaption("")  # Clear default caption
        caption_actor.BorderOff()
        caption_actor.LeaderOff()

        # Get the text property
        text_property = caption_actor.GetCaptionTextProperty()

        # Set text properties
        text_property.SetFontFamily(vtk.VTK_FONT_FILE)
        text_property.SetFontSize(font_size)
        text_property.SetBold(True)
        text_property.SetShadow(False)

        # Set the position and height of the caption
        caption_actor.SetAttachmentPoint(
            length, 0, 0
        )  # This will be different for each axis
        caption_actor.SetPosition(
            length + 0.2 * length, 0
        )  # Adjust position relative to axis end

        # Enable non-scaled text
        caption_actor.GetTextActor().SetTextScaleModeToNone()

    # Adjust individual axis caption positions
    axes.GetYAxisCaptionActor2D().SetAttachmentPoint(0, length, 0)
    axes.GetYAxisCaptionActor2D().SetAttachmentPoint(0, length + 0.2 * length, 0)

    axes.GetZAxisCaptionActor2D().SetAttachmentPoint(0, 0, length)
    axes.GetZAxisCaptionActor2D().SetAttachmentPoint(0, 0, length + 0.2 * length)

    # Customize arrow heads
    axes.SetConeRadius(cone_radius)
    axes.SetConeResolution(16)  # Smooth cone
    axes.SetShaftTypeToCylinder()
    axes.SetCylinderRadius(cone_radius * 0.05)  # Decrease cylinder radius
    axes.SetNormalizedShaftLength(0.85, 0.85, 0.85)  # Adjust shaft length
    axes.SetNormalizedTipLength(0.15, 0.15, 0.15)  # Adjust tip length

    return axes
