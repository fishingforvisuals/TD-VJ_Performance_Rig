"""
Engine COMP Callbacks

me - this DAT
"""

def onInitialize(engineComp: engineCOMP, callCount: int) -> int:
	"""
	Called when the Engine COMP is initialized.
	
	Args:
		engineComp: The connected Engine COMP
		callCount: Increments with each attempt, starting at 1
		
	Returns:
		int: If > 0, will be called again after the returned number of frames
	"""
	return 0

def onReady(engineComp: engineCOMP):
	"""
	Called when the Engine COMP is ready.
	"""
	return

def onStart(engineComp: engineCOMP):
	"""
	Called when the Engine COMP starts.
	"""
	return

def whileRunning(engineComp: engineCOMP):
	"""
	Called every frame while the Engine COMP is running.
	"""
	return

def onDone(engineComp: engineCOMP):
	"""
	Called when the Engine COMP is done.
	"""
	return

def onError(engineComp: engineCOMP):
	"""
	Called when the Engine COMP encounters an error.
	"""
	return
