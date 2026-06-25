# callbacks for when associated Panel is being dropped on
# base COMP with extension
base = parent(2)

def checkEngineRange(dragItemOwner):
	if dragItemOwner == "/sceneloader/engine1":
		engine_range = [1,8]
		return engine_range
	elif dragItemOwner == "/sceneloader/engine2":
		engine_range = [9,16]
		return engine_range

def checkKnobDeckMatch(comp, dragItemOwner):
	"""
	when the knob is inside the range of what the engines can be assigned to return true
	Args:
		comp: the panel component being hovered over
		dragItemOwner: from which operator does the visual come 
	"""
	# prepare knob digit
	parts = comp.path.split('/')
	# ['', 'midiMap', 'knobs', 'knob1', 'label', 'text']
	if len(parts) >= 4 and parts[1] == 'midiMap' and parts[2] == 'knobs':
		name = parts[3]
		if name.startswith('knob'):
			knob_digit = int(name.replace("knob", ""))
	
	
	if dragItemOwner == "/sceneloader/engine1":
		engine_range = [1,8]
		
		if knob_digit in range(engine_range[0], engine_range[1]):
			# print("Parameter accepted")
			return True
	elif dragItemOwner == "/sceneloader/engine2":
		engine_range = [9,16]
		if knob_digit in range(engine_range[0], engine_range[1]):
			# print("Parameter accepted")
			return True
	else:
		return False
	
		# 
	return None

def onHoverStartGetAccept(comp, info):
	"""
	Called when comp needs to know if dragItems are acceptable as a drop.

	Args:
		comp: the panel component being hovered over
		info: A dictionary containing all info about hover, including:
			dragItems: a list of objects being dragged over comp
			callbackPanel: the panel Component pointing to this callback DAT

	Returns:
		True if comp can receive dragItems
	"""
	#debug('\nonHoverStartGetAccept comp:', comp.path, '- info:\n', info)
	print("Hover over: ", comp, ", dragItems: ", info.get("dragItems")[0].owner)
	# print(comp.name.replace("/knob0", "").replace("/", ""))


	knob_match = checkKnobDeckMatch(comp, info.get("dragItems")[0].owner)
	

	return knob_match # accept what is being dragged

def onHoverEnd(comp, info):
	"""
	Called when dragItems leave comp's hover area.

	Args:
		comp: the panel component being hovered over
		info: A dictionary containing all info about hover, including:
			dragItems: a list of objects being dragged over comp
			callbackPanel: the panel Component pointing to this callback DAT
	"""
	#debug('\nonHoverEnd comp:', comp.path, '- info:\n', info)

def onDropGetResults(comp, info):
	"""
	Called when comp receives a drop of dragItems. This will only be called if
	onHoverStartGetAccept has returned True for these dragItems.

	Args:
		comp: the panel component being dropped on
		info: A dictionary containing all info about drop, including:
			dragItems: a list of objects being dropped on comp
			callbackPanel: the panel Component pointing to this callback DAT

	Returns:
		A dictionary of results with descriptive keys. Some possibilities:
			'droppedOn': the object receiving the drop
			'createdOPs': list of created ops in order of drag items
			'dropChoice': drop menu choice selected
			'modified': object modified by drop
	"""
	# debug('\nonDropGetResults comp:', comp.path, '- info:\n', info)
	droppedOn = comp.path
	dropped_item = info.get("dragItems")[0]
	target = op(dropped_item.owner)
	par_name = dropped_item.name

	# create bind Reference from the dropped parameter to the knob value
	target.pars(par_name)[0].mode = ParMode.BIND
	target.pars(par_name)[0].bindExpr = f"op('{droppedOn}').par.Value0"

	update_range = checkEngineRange(dropped_item.owner)
	scope = dropped_item.owner
	# update labels in specific range via main.py script
	run(f"op('{base}').LabelKnob(args[0], args[1], args[2])", comp, update_range, scope, delayFrames=1)
	

# callbacks for when associated Panel is being dragged

def onDragStartGetItems(comp, info):
	"""
	Called when information about dragged items is required.

	Args:
		comp: the panel clicked on to start drag
		info: A dictionary containing all info about drag
			callbackPanel: the panel Component pointing to this callback DAT

	Returns:
		A list of dragItems: [object1, object2, ...]
	"""
	dragItems = [comp] # drag the comp itself
	#debug('\nonDragStartGetItems comp:', comp.path, '- info:\n', info)
	return dragItems

def onDragEnd(comp, info):
	"""
	Called when a drag action ends.

	Args:
		comp: the panel clicked on to start drag
		info: A dictionary containing all info about drag, including:
			accepted: True if the drag was accepted, False if not
			dropResults: a dict of drop results. This is the return value of 
				onDropGetResults
			dragItems: the original dragItems for the drag
			callbackPanel: the panel Component pointing to this callback DAT
	"""
	#debug('\nonDragEnd comp:', comp.path, '- info:\n', info)
	
