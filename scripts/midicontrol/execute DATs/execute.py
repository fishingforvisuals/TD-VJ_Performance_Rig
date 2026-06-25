# base COMP with extension
base = parent(2)



def onStart():
	

	# reset selection
	const = base.op("knob_ui/selection")
	seq = const.seq.const
	for chan in seq:
		chan.par.value = 0
		
	
	


	# recreate knob labels
	# comp = op("knob1") 
	# update_range = [1,17]
	# scope = op("/engine/noise1")
	# run(f"op/'{base}').LabelKnob(args[0], args[1], args[2])", comp, update_range, scope, delayFrames=120)

	
	table = op("knob_settings")
	all_knobs = [knob.name for knob in parent().findChildren(tags=["knob"])]
	
	
	for knob in all_knobs:
		#recreate knob colors
		knob_color = [table[knob, "Knoblevelcolorr"], table[knob, "Knoblevelcolorg"], table[knob, "Knoblevelcolorb"]]
		base.ChangeKnobColor(knob, knob_color)
		
		# restore knob values
		stored_knob_value = float(table[knob, "Value0"])
		op(knob).par.Value0 = stored_knob_value
	
	


	return

def onCreate():
	return

def onExit():
	return

def onFrameStart(frame):
	return

def onFrameEnd(frame):
	return

def onPlayStateChange(state):
	return

def onDeviceChange():
	return

def onProjectPreSave():
	parameter_list = [param.val for param in op('knob_settings').row(0)[1:]]

	for param in parameter_list:
		for knob in parent().findChildren(tags=["knob"]):
			base.StoreSettings(param, knob)
	return

def onProjectPostSave():
	return

	