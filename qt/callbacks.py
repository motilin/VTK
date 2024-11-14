def toggle_visibility(vtk_widget, actor):
    # Toggle the visibility of the given actor
    actor.SetVisibility(not actor.GetVisibility())
    vtk_widget.get_render_window().Render()
