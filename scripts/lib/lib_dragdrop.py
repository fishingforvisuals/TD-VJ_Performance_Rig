def onDragStartGetItems(comp, info):
    dragItems = [comp]  # drag the comp itself
    # debug('\nonDragStartGetItems comp:', comp.path, '- info:\n', info)
    return dragItems
