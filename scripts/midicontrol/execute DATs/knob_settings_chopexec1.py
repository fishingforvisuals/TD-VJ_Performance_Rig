# base COMP with extension
base = parent(2)

def onOffToOn(channel: Channel, sampleIndex: int, val: float, 
				prev: float):
	"""
	Called when a channel changes from 0 to non-zero.

	Args:
		channel: The Channel object which has changed
		sampleIndex: The index of the changed sample
		val: The numeric value of the changed sample
		prev: The previous sample value
	"""
	last_name = me.fetch('last_channel_name', None)

	src = op('select1')
	const = op('selection')
	modkeys = op("modkeys")


	def updateSettings(label, focusChannel):
		"""
		insert label and select the knob_colors and parameters to view
		"""

		t_label = op('masterHeader')
		t_params = op('knob_parameter')

		# create label
		t_label.par.Headerlabel = label

		# update current parameter settings to view
		knob_path = f"{base.path}/knobs/{focusChannel}"
		t_params.par.op = knob_path
		
		# define selection of color parameters in focus_knobcolor CHOP
		focus_color = op("focus_knobcolor")
		focus_color.par.ops = f"{base.path}/knobs/{focusChannel}"


	######### prepare selection infrastructure #########
	if not const:
		const = op('..').create(constantCHOP, 'selection')
		run("op('selection').viewer = 1", delayFrames=1)

	seq = const.seq.const
	count = len(src.chans())

	# recreate selection CHOPs channel names when the chops amount of channels is not the same as the source
	if const or len(seq) != count:
		seq.numBlocks = count
		for i, ch in enumerate(src.chans()):
			seq[i].par.name = ch.name


	######## create selection ########
	# select single knob and evaluate all the others to reset any
	if modkeys["shift"] == 0 and modkeys["ctrl"] == 0: 
		for i, ch in enumerate(src.chans()):
			seq[i].par.value = ch.eval()
		
		updateSettings(channel.name, channel.name)
		
		me.store("last_channel_name", channel.name) 	# store channel.name to last_channel_name variable


	# select a range of knobs by clicking on 2 different knobs, keep the first selected knob as last_channel_knob
	if modkeys["shift"] == 1:
		last_knob_digits = int(last_name.replace("knob", ""))
		current_knob_digits = int(channel.name.replace("knob", ""))

		range_list = [last_knob_digits, current_knob_digits]
		range_list = sorted(range_list)

		# reset all values in selection CHOP
		for i, ch in enumerate(src.chans()):
			seq[i].par.value = 0

		# select range
		for i in range(range_list[0], range_list[1] + 1):
			seq[i-1].par.value = 1
		
		label_string = f"knob{range_list[0]}-{range_list[1]}"
		updateSettings(label_string, last_name)

	# with ctrl key pressed select or deselect knobs 
	if modkeys['ctrl'].eval() == 1:
		label_string = "knob "
		for block in const.seq.const:
			if block.par.name.eval() == channel.name:
				current = block.par.value.eval()
				block.par.value = 0 if current else 1
			if block.par.value.eval() == 1:
				label_string += f"{block.par.name.eval().replace('knob', '')}, "
				updateSettings(label_string, last_name)
		
		return

def whileOn(channel: Channel, sampleIndex: int, val: float, 
			prev: float):
	"""
	Called every frame while a channel is non-zero.
	
	Args:
		channel: The Channel object which has changed
		sampleIndex: The index of the changed sample
		val: The numeric value of the changed sample
		prev: The previous sample value
	"""
	return

def onOnToOff(channel: Channel, sampleIndex: int, val: float, 
			  prev: float):
	"""
	Called when a channel changes from non-zero to 0.
	
	Args:
		channel: The Channel object which has changed
		sampleIndex: The index of the changed sample
		val: The numeric value of the changed sample
		prev: The previous sample value
	"""
	return

def whileOff(channel: Channel, sampleIndex: int, val: float, 
			 prev: float):
	"""
	Called every frame while a channel is 0.
	
	Args:
		channel: The Channel object which has changed
		sampleIndex: The index of the changed sample
		val: The numeric value of the changed sample
		prev: The previous sample value
	"""
	return

def onValueChange(channel: Channel, sampleIndex: int, val: float, 
				  prev: float):
	"""
	Called when a channel value changes.
	
	Args:
		channel: The Channel object which has changed
		sampleIndex: The index of the changed sample
		val: The numeric value of the changed sample
		prev: The previous sample value
	"""
	return