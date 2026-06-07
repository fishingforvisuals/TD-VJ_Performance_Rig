# TD-VJ_Performance_Rig
This will become a VJ Mixer completely made in Touchdesigner. It should have functions like library management, previews, Midi parameter auto-mapping. Currently the basic setup is done but it has a lot of bugs.

## Basic Functionality
### UI
The UI Widget has the following areas:
- left section
    - Output Window
    - scene loader and corresponding parameters
- middle section
    - visuals library
- right section
    - Midi Fighter Widget

### Library
The library loads external tox files from /tox/visuals as visuals in that folder are .tiff-images that are used as thumbnails.
These visuals will be stacked in a scrollable list that previews the thumbnails.
The visuals can be dragged onto the scene loader widget to load them into the decks.

### Parameters
This section shows the custom parameter page from the visuals loaded in the deck. 
By dragging and dropping the parameters onto knobs of the Midi Fighter Widget they get assigned to that knob. This connection should be stored in the visual so that it gets automatically assigned when the visual is reloaded.

It would be nice to add functionalities for other data assignments e.g. CHOPs


## Problems to fix
- all visuals in the library are cooking the whole time
    - there are two options of how to fix this: enable cooking when loaded in the deck or even using engines in the deck loader
- external tox midi fighter twister doesn't work
- visuals are loaded from tox files when reloading them parameter
- tox visuals need a name in the lib preview


## next tasks
- [x] rework library management
- [ ] update drag and drop scripts
- [ ] update scene loader
- [ ] fix midi twister assignments
- [ ] fix storing the assignments with the visuals