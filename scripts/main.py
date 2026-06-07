import os


class LibraryEXT:
    def __init__(self, ownerCOMP):
        self.ownerCOMP = ownerCOMP
        debug(
            f"[LibraryEXT] Extension initialized on {ownerCOMP.path}"
        )  # this is already your container COMP
        self.oop = self.ownerCOMP  # just use it directly

        # -----------------------------------------------------------------
        # Thumbnail folder
        # -----------------------------------------------------------------
        self.thumb_dir = project.folder + "/tox/visuals"
        if not os.path.exists(self.thumb_dir):
            os.makedirs(self.thumb_dir)

        # -----------------------------------------------------------------
        # Bindings table
        # -----------------------------------------------------------------
        self.bindings_table_name = "visual_bindings"
        self.bindings_table = self.getOp(self.bindings_table_name)
        if not self.bindings_table:
            # create a new table DAT
            self.bindings_table = self.oop.create(tableDAT, self.bindings_table_name)
            # move to free space, e.g. X=300, Y=-200
            # self.bindings_table.nodeX = 300
            # self.bindings_table.nodeY = -200
        else:
            self.bindings_table.clear()

        # set header row
        self.bindings_table.appendRow(
            ["replicant_name", "param_name", "bind_type", "value", "SceneSlot"]
        )

    # -----------------------------------------------------------------
    # Helper to safely fetch child OPs
    # -----------------------------------------------------------------
    def getOp(self, name):
        op_ref = self.oop.op(name)  # use self.oop directly
        if not op_ref:
            debug(f"[LibraryEXT] OP '{name}' not found in {self.oop.path}")
        return op_ref

    # -----------------------------------------------------------------
    # Thumbnail methods
    # -----------------------------------------------------------------
    def SetupThumbnail(self, replicant):
        visual_container = replicant.op("visual")
        if not visual_container:
            debug(f"[Thumbnail] ERROR: No 'visual' container in {replicant.path}")
            return

        tox_path = visual_container.par.externaltox.eval()
        if not tox_path:
            debug(f"[Thumbnail] ERROR: No externaltox set on {visual_container.path}")
            return

        # derive thumbnail name
        tox_name = os.path.splitext(os.path.basename(tox_path))[0]
        thumb_path = os.path.join(self.thumb_dir, tox_name + ".tif").replace("\\", "/")

        if os.path.exists(thumb_path):
            if self.LoadThumbnail(replicant, thumb_path):
                debug(f"[Thumbnail] Loaded existing thumbnail: {tox_name}")
            else:
                debug(f"[Thumbnail] Failed to load existing thumbnail: {tox_name}")
            return

        # generate new thumbnail
        bg = visual_container.op("bg")
        if not bg:
            debug(f"[Thumbnail] ERROR: No bg TOP in {visual_container.path}")
            return

        sel = replicant.create("selectTOP", "sel_tmp")
        sel.par.top = bg.path

        mfo = replicant.create("moviefileoutTOP", "mfo_tmp")
        mfo.inputConnectors[0].connect(sel)
        mfo.par.file = thumb_path
        mfo.par.type = 1  # Single Image
        mfo.par.imagefiletype = 0  # TIF
        mfo.par.record = 1  # start recording

        # delayed stop and load
        def finish_record():
            mfo.par.record = 0
            success = self.LoadThumbnail(replicant, thumb_path)
            sel.destroy()
            mfo.destroy()
            if success:
                debug(f"[Thumbnail] Successfully created and loaded: {tox_name}")
            else:
                debug(f"[Thumbnail] FAILED to create/load thumbnail: {tox_name}")

        run(finish_record, delayFrames=10)

    def LoadThumbnail(self, replicant, thumb_path):
        if not os.path.exists(thumb_path):
            return False

        old = replicant.op("thumb_in")
        if old:
            old.destroy()

        thumb_top = replicant.create(moviefileinTOP, "thumb_in")
        thumb_top.par.file = thumb_path
        replicant.par.top = thumb_top
        return True

    # -----------------------------------------------------------------
    # Bindings methods
    # -----------------------------------------------------------------
    def StoreBindings(self, replicant):
        script_name = "LibraryEXT.StoreBindings"
        visual_op = replicant.op("visual")
        if not visual_op:
            debug(f"[{script_name}] ERROR: No 'visual' container in {replicant.path}")
            return

        # Read slot from the visual container (always the correct path)
        slot_val = getattr(visual_op.par, "Sceneslot", 1)
        debug(f"[{script_name}] Visual '{replicant.name}' slot = {slot_val}")

        # Iterate over parameters on the visual container
        for par in visual_op.pars():
            if par.page != "Custom":
                continue

            value = None
            bind_type = None

            if getattr(par, "binding", None):
                value = par.binding
                bind_type = "bind"
            elif getattr(par, "bindExpr", None):
                value = par.bindExpr
                bind_type = "bindExpr"
            elif getattr(par, "expr", None) and par.expr != "":
                value = par.expr
                bind_type = "expr"
            else:
                continue  # skip unbound

            debug(f"[{script_name}] Processing param '{par.name}' -> type: {bind_type}, value: {value}")

            # Check if this param already exists in the table
            existing_row = None
            for r in range(1, self.bindings_table.numRows):
                rep_name = self.bindings_table[r, 0].val
                par_name = self.bindings_table[r, 1].val
                row_slot = int(self.bindings_table[r, 4].val) if self.bindings_table.numCols > 4 else 1
                if rep_name == replicant.name and par_name == par.name and row_slot == slot_val:
                    existing_row = r
                    break

            if existing_row is not None:
                old_type = self.bindings_table[existing_row, 2].val
                old_val = self.bindings_table[existing_row, 3].val
                old_slot = int(self.bindings_table[existing_row, 4].val) if self.bindings_table.numCols > 4 else 1

                if old_type == bind_type and str(old_val) == str(value) and old_slot == slot_val:
                    debug(f"[{script_name}] Skip unchanged {replicant.name}.{par.name} (slot {slot_val})")
                    continue
                else:
                    self.bindings_table[existing_row, 2].val = bind_type
                    self.bindings_table[existing_row, 3].val = str(value)
                    if self.bindings_table.numCols <= 4:
                        self.bindings_table.appendCol("SceneSlot")
                    self.bindings_table[existing_row, 4].val = str(slot_val)
                    debug(f"[{script_name}] Updated {replicant.name}.{par.name} ({bind_type}) = {value}, slot {slot_val}")
            else:
                # new entry -> append row
                row = [replicant.name, par.name, bind_type, str(value), str(slot_val)]
                self.bindings_table.appendRow(row)
                debug(f"[{script_name}] Added {replicant.name}.{par.name} ({bind_type}) = {value}, slot {slot_val}")

        debug(f"[{script_name}] Finished storing bindings for '{replicant.name}'")

    def StoreAllReplicantBindings(self, replicator_op):
        replicator = self.getOp(replicator_op)
        if not replicator:
            debug(f"[Bindings] ERROR: replicator '{replicator_op}' not found")
            return

        parent_comp = replicator.parent()
        siblings = parent_comp.findChildren(depth=1, type=COMP)

        for rep in siblings:
            if rep == replicator:
                continue
            if rep.name.lower().startswith("visual"):
                self.StoreBindings(rep)

    def RestoreBindings(self, replicant):
        visual_container = replicant.op("visual")
        if not visual_container:
            debug(f"[Bindings] ERROR: No 'visual' container in {replicant.path}")
            return

        # determine which scene_selector slot this replicant belongs to
        parent_name = replicant.parent().name.lower()
        slot_index = 1
        if parent_name.startswith("scene_selector"):
            try:
                slot_index = int(parent_name.replace("scene_selector", ""))
            except ValueError:
                slot_index = 1  # fallback

        knob_offset = (slot_index - 1) * 8
        debug(f"[Bindings] Restoring for {replicant.name} in {parent_name}, knob offset {knob_offset}")

        for r in range(1, self.bindings_table.numRows):
            if self.bindings_table[r, 0].val != replicant.name:
                continue

            param_name = self.bindings_table[r, 1].val
            bind_type = self.bindings_table[r, 2].val
            value = self.bindings_table[r, 3].val

            # if param is a knob, shift it by the offset
            if param_name.lower().startswith("knob"):
                try:
                    knob_num = int(param_name[4:])  # extract knob number
                    param_name = f"Knob{knob_num + knob_offset}"
                    debug(f"[Bindings] Remapped knob {knob_num} -> {param_name}")
                except Exception:
                    pass

            par = getattr(visual_container.par, param_name, None)
            if not par:
                continue

            try:
                if bind_type == "bind":
                    par.bind = op(value)
                elif bind_type == "bindExpr":
                    par.bindExpr = value
                elif bind_type == "expr":
                    par.expr = value
                debug(f"[Bindings] Restored {replicant.name}.{param_name} ({bind_type})")
            except Exception as e:
                debug(
                    f"[Bindings] Failed to restore {replicant.name}.{param_name}: {e}"
                )

    def BindParameterToKnob(self, param: Par, knob_op_path: str):
        """
        Bind a parameter to a knob, store it in the visual_bindings table,
        and update Bindparameterref. Fixes slot-based binding issue.
        """
        knob_op = op(knob_op_path)
        if not knob_op or not hasattr(knob_op.par, "Value0"):
            debug(f"[KnobBind] Missing knob or Value0: {knob_op_path}")
            return

        visual_container = param.owner
        # Determine which scene slot this visual belongs to
        slot_val = getattr(visual_container.par, "Sceneslot", 1)
        knob_offset = (slot_val - 1) * 8  # if you use 8 knobs per slot

        # Apply knob offset if param is a knob
        knob_name = param.name
        if knob_name.lower().startswith("knob"):
            try:
                knob_num = int(knob_name[4:])
                knob_num += knob_offset
                knob_name = f"Knob{knob_num}"
            except Exception:
                pass

        # Bind the parameter
        param.bindExpr = f"op('{knob_op_path}').par.Value0"
        debug(f"[KnobBind] Bound {visual_container.path}.{param.name} -> {knob_op_path}.Value0")

        # Update Bindparameterref on the knob
        if hasattr(knob_op.par, "Bindparameterref"):
            current = knob_op.par.Bindparameterref.eval() if hasattr(knob_op.par.Bindparameterref, "eval") else knob_op.par.Bindparameterref.val
            current_names = [n.strip() for n in (current or "").split(",") if n.strip()]
            if param.name not in current_names:
                current_names.append(param.name)
            knob_op.par.Bindparameterref.val = ", ".join(current_names)
            debug(f"[KnobBind] Updated {knob_op_path}.Bindparameterref -> {knob_op.par.Bindparameterref.val}")

        # Update visual_bindings table
        table = self.bindings_table
        if not table:
            debug("[KnobBind] No bindings table available")
            return

        # --- Print BEFORE ---
        debug("[KnobBind] Table BEFORE update:")
        for r in range(table.numRows):
            debug(f"  Row {r}: {[table[r, c].val for c in range(table.numCols)]}")

        # Check if entry exists (consider slot now!)
        existing_row = None
        for r in range(1, table.numRows):
            row_parent = table[r, 0].val
            row_param = table[r, 1].val
            row_slot = int(table[r, 4].val) if table.numCols > 4 else 1
            if row_parent == visual_container.parent().name and row_param == param.name and row_slot == slot_val:
                existing_row = r
                break

        value = param.bindExpr
        bind_type = "bindExpr"

        if existing_row is not None:
            table[existing_row, 2].val = bind_type
            table[existing_row, 3].val = value
            table[existing_row, 4].val = str(slot_val)
            debug(f"[KnobBind] Updated table row {existing_row}: {param.name} -> {value} (slot {slot_val})")
        else:
            table.appendRow([visual_container.parent().name, param.name, bind_type, value, str(slot_val)])
            debug(f"[KnobBind] Added table entry: {param.name} -> {value} (slot {slot_val})")

        # --- Print AFTER ---
        debug("[KnobBind] Table AFTER update:")
        for r in range(table.numRows):
            debug(f"  Row {r}: {[table[r, c].val for c in range(table.numCols)]}")

        debug(f"[KnobBind] Finished BindParameterToKnob for {param.name}")
