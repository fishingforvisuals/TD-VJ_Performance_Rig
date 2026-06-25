import colorsys

class MidiControllerEXT:
    def __init__(self, ownerCOMP):
        self.ownerCOMP = ownerCOMP
        oop = self.ownerCOMP.op
        self.oop = oop

        # recurring references
        self.Target_table = self.oop("knobs/knob_settings")  # last knob_settings table DAT
        self.Knob_selection = self.oop("knob_ui/selection")  # constant CHOP with states of currently selected knobs
        self.Knobs = self.oop("knobs")

    def GetColIndex(self, table, col_name):
        """Return the index of col_name in the first row of the table"""
        # TODO: needs to be checked, where used?

        header_row = table.rows()[0]  # first row
        for i, cell in enumerate(header_row):
            if cell.val == col_name:
                return i
        return None  # not found
    
    def TestFunction(self):
        print(self.Target_table)
    
    def StoreSettings(self, param, knob):
        """
        Store the settings of each knob and take all the listed parameters from the Target_table (which is the knob_settings table). With the arguments this is a per parameter approach which gives you the ability to decide how many parameters should be stored with this function.
        Args:
            param: is the parameter name that will be stored
            knob: defines from which operator to pull the parameter value from
        """
        self.Target_table[knob.name, param] = knob.par[param]



    def StoreCurrentValues(self, param_name):
        """
        Store current value of `param_name` from each knob listed in self.source_table (opfind1)
        into the corresponding row in self.Target_table without deleting rows.
        """
        # TODO: needs to be checked, where used?
        print("store data")
        if not self.Target_table or not self.source_table:
            print("[MyExt] source_table or Target_table not found")
            return

        # find column index in Target_table
        col_index = self.GetColIndex(self.Target_table, param_name)
        if col_index is None:
            print(f"[MyExt] Column '{param_name}' not found in Target_table")
            return

        # find column index in source_table for knob names
        name_col_index = self.GetColIndex(self.source_table, "name")
        if name_col_index is None:
            print("[MyExt] Column 'name' not found in source_table")
            return

        # loop over knobs listed in source_table
        for i, row in enumerate(self.source_table.rows()[1:]):  # skip header
            knob_name = row[name_col_index].val
            knob = self.oop(knob_name)
            if not knob:
                print(f"[MyExt] Knob '{knob_name}' not found, skipping")
                continue

            # access parameter safely with exact case
            par = getattr(knob.par, param_name, None)
            if par is not None:  # check the object, not its value
                self.Target_table[i + 1, col_index] = par.eval()
            else:
                print(f"[MyExt] Knob '{knob_name}' has no parameter '{param_name}'")

    def StoreData(self, op_path, par_name, val):
        """
        Set the parameter on a dynamically referenced operator.
        op_path: "knob1" (not op('knob1'))
        par_name: parameter name string
        val: value to set
        """
        # TODO: needs to be checked, where used?

        try:
            knob = self.oop(op_path)  # resolve operator
            if knob:
                knob.par[par_name] = val
            else:
                debug(f"OP not found: {op_path}")
        except Exception as e:
            debug(f"Error setting {op_path}.{par_name}: {e}")

    def ApplyAssignments(self):
        """
        Loop over rows in Target_table and set parameters.
        Works with replicants: uses stable identifiers to match the operator.
        Assumes table format:
            stack | # | ... | param columns ...
        """
        # TODO: needs to be checked, where used?
        print("applying assignments")
        table = self.Target_table
        num_rows = table.numRows
        num_cols = table.numCols

        # find column indices
        stack_col = 0  # assuming first col is 'stack'
        id_col = 1  # assuming second col is '#'
        # other columns are parameters
        param_cols = [c for c in range(num_cols) if c not in (stack_col, id_col)]

        for r in range(1, num_rows):  # skip header
            stack_val = table[r, stack_col].val
            knob_id = table[r, id_col].val

            # find the replicant by some stable identifier
            # example: name = knob_id or combine stack+id
            op_path = knob_id  # adjust if needed
            knob = self.oop(op_path)
            if not knob:
                debug(f"Replicant {op_path} not found, skipping row {r}")
                continue

            # apply stored parameter values
            for c in param_cols:
                par_name = table[0, c].val  # header row = parameter name
                val = table[r, c].val
                try:
                    self.StoreData(op_path, par_name, val)
                except Exception as e:
                    debug(f"Error applying {op_path}.{par_name} = {val}: {e}")

    def ResetKnobs(self, reset_val=""):
        """
        Reset all knob-related values in Target_table, except the 'stack' and '#' columns.
        Keeps header row intact. Default reset value = 0.
        Works by indexing through the table like op('tableDAT')[row, col].
        """
        # TODO: needs to be checked, where used?
        table = self.Target_table
        num_rows = table.numRows
        num_cols = table.numCols

        # find indices of columns to skip by checking header row (row 0)
        skip_cols = []
        for c in range(num_cols):
            header_val = table[0, c].val
            if header_val in ["stack", "#"]:
                skip_cols.append(c)

        # iterate over data rows (skip header row)
        for r in range(1, num_rows):
            for c in range(num_cols):
                if c not in skip_cols:
                    try:
                        table[r, c] = reset_val
                    except Exception as e:
                        debug(f"Error resetting cell {r},{c}: {e}")

    # ------------------------------------- |
    #           HELPER-FUNCTIONS            |
    # ------------------------------------- |

    def StoreHelper(self, param_names=None):
        """
        Store current values of parameters listed in param_names into Target_table.
        """
        # TODO: needs to be checked, where used?
        if param_names is None:
            param_names = [
                "Knoblevelcolorr",
                "Knoblevelcolorg",
                "Knoblevelcolorb",
                "Mfthue",
                "Bindparameterref",
                "Value0",
                "Rgbbrightness",
            ]

        for param in param_names:
            self.StoreCurrentValues(param_name=param)

    def RecreateReplicants(self, replicator_op="replicator1"):
        """
        Recreate all replicants for the given replicator COMP.
        Args:
            - replicator_op: path to a replicator op
        """
        # TODO: pulsing the replicator like that is not doing much -> disable this function?
        replicator = op(replicator_op)
        if replicator:
            replicator.par.recreateall.pulse()
        else:
            debug(f"Replicator '{replicator_op}' not found!")

    def DelayHelper(self, func, delay_frames=10):
        """
        Run any function after a delay of delay_frames.
        """
        # TODO: needs to be checked, where used?
        run(func, delayFrames=delay_frames)

    def StoreRecreateApply(
        self, param_names=None, replicator_op="replicator1", apply_delay=10
    ):
        # TODO: needs to be checked, where used?
        """
        Convenience method to store -> recreate -> apply assignments.
        """
        self.StoreHelper(param_names)
        self.RecreateReplicants(replicator_op)

        # delayed application
        self.DelayHelper(self.ApplyAssignments, apply_delay)

    def GetSelectedKnobs(self):
        """
        check what knobs are currently selected
        Returns:
            List of currently selected knobs
        """

        seq = self.Knob_selection.seq.const
        selected_knobs = [knob.par.name for knob in seq if knob.par.value == 1]
        return selected_knobs



    def rgb_to_hue(self,r, g, b):
        """Convert RGB (0-1) to MIDI hue 0-127"""
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        # print (h, s, v)
        return float(h)
    
    def ChangeKnobColor(self, knobName, color):
        """
        updates the knobs ui and midi controller color. Converts values accordingly
        Args:
            knobName: knob of which the color will be changed
        """
    
        ####### update color in ui #######            
        knob_op = self.Knobs.op(knobName)


        r, g, b = color[0], color[1], color[2]

        knob_op.par.Knobcolorr = r
        knob_op.par.Knobcolorg = g
        knob_op.par.Knobcolorb  = b

        ####### send color values to midi controller #######    
        # convert from rgb to hsv
        midi_hue = self.rgb_to_hue(r, g, b)
        # Midi Fighter Twister has a different hue mapping compared to TD
        # reversing the values solves the issue
        midiout = knob_op.op("constant1")
        midiout_remap = ((1 - midi_hue) -1/3) %1
        midiout.par.value0 = midiout_remap
            
    def LabelKnob(self, comp, update_range, scope):
        """
        Trigger: on starting td and dragging new parameters onto the midi controller
        function: create Label from bound parameters

        Args:
            comp: is the td COMP that updates the labels
            range: list of min and max of which knobs get updated, adds possibility to use two decks of visuals for example
            scope: op that filters bindReferences to update from
        """
        # TODO: insert the whole operator and access its path via op.path        
        knob_base_path = comp.path[:-len(str(comp.digits))] # remove knob digit


        # update every knob in range
        for knob in range(update_range[0], update_range[1]):
            knob_comp =  knob_base_path + str(knob)
            
            p = op(knob_comp).par.Value0
            bound_par = p.bindReferences

            # filter bound_par with scope
            filtered_bound_par_names = [ref.name for ref in bound_par if scope.path in ref.owner.path]
            
            # create label from list
            label = ", ".join(filtered_bound_par_names)
            
            # apply label
            op(knob_comp).par.Widgetlabel = label