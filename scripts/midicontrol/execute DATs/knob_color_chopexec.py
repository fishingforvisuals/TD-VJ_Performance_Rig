base = parent(2)

def onValueChange(channel, sampleIndex, val, prev):
	'''
	when color is selected in parameter viewer update the color for the whole selection
	'''
	knob_list = base.GetSelectedKnobs()
	focus_color_op = base.op("knob_ui/focus_knobcolor")
	focus_color_rgb = [color.eval() for color in focus_color_op.chans()]
	
	for knob in knob_list:
		base.ChangeKnobColor(knob, focus_color_rgb)

	return
	