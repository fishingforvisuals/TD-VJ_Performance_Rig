import re

def debug_table(table, msg="Table contents"):
    if table:
        debug(f"[select1_callback] {msg}:")
        for r in range(table.numRows):
            debug(f"  Row {r}: {[table[r, c].val for c in range(table.numCols)]}")

def _get_par(op_obj, par_name):
    """Fetch a parameter robustly by name."""
    try:
        return getattr(op_obj.par, par_name)
    except Exception:
        pass
    for p in op_obj.pars():
        if p.name.lower() == par_name.lower():
            return p
    debug(f"[select1_callback] Parameter '{par_name}' not found on {op_obj.path}")
    return None

def _clear_slot_knobs(replicant_op):
    debug(f"[select1_callback] _clear_slot_knobs called for {replicant_op.path}")
    parent_name = replicant_op.parent().name.lower()
    slot_index = 1
    if parent_name.startswith("scene_selector"):
        try:
            slot_index = int(parent_name.replace("scene_selector", ""))
        except ValueError:
            debug(f"[select1_callback] Failed to parse slot index from {parent_name}, defaulting to 1")

    knob_prefix = "knob"
    start_knob = (slot_index - 1) * 8 + 1
    end_knob = slot_index * 8

    # Show knob values before clearing
    debug(f"[select1_callback] Clearing knobs for slot {slot_index} ({replicant_op.path}) - BEFORE")
    for knob_num in range(start_knob, end_knob + 1):
        knob_op = op(f"/midiFighterTwisterV2/{knob_prefix}{knob_num}")
        if knob_op and hasattr(knob_op.par, "Bindparameterref"):
            debug(f"  {knob_op.path}.Bindparameterref = '{knob_op.par.Bindparameterref.val}'")
        elif knob_op:
            debug(f"  {knob_op.path} has no Bindparameterref")
        else:
            debug(f"  Knob {knob_num} not found")

    # Clear Bindparameterref
    for knob_num in range(start_knob, end_knob + 1):
        knob_op = op(f"/midiFighterTwisterV2/{knob_prefix}{knob_num}")
        if knob_op and hasattr(knob_op.par, "Bindparameterref"):
            knob_op.par.Bindparameterref.val = ""
            debug(f"[select1_callback] Cleared {knob_op.path}.Bindparameterref")

    # Restore bindings
    debug(f"[select1_callback] Restoring bindings for {replicant_op.path}")
    parent().RestoreBindings(replicant_op)

    debug(f"[select1_callback] Knob values AFTER restore for slot {slot_index}")
    for knob_num in range(start_knob, end_knob + 1):
        knob_op = op(f"/midiFighterTwisterV2/{knob_prefix}{knob_num}")
        if knob_op and hasattr(knob_op.par, "Bindparameterref"):
            debug(f"  {knob_op.path}.Bindparameterref = '{knob_op.par.Bindparameterref.val}'")


def _set_bindparameterref(knob_num, ref_name):
    knob_path = f"/midiFighterTwisterV2/knob{knob_num}"
    knob_op = op(knob_path)
    if not knob_op:
        debug(f"[select1_callback] Missing {knob_path}")
        return False
    if not hasattr(knob_op.par, "Bindparameterref"):
        debug(f"[select1_callback] {knob_path} has no Bindparameterref")
        return False

    current = knob_op.par.Bindparameterref.eval() if hasattr(knob_op.par.Bindparameterref, "eval") else knob_op.par.Bindparameterref.val
    current = current.strip() if current else ""
    names = [n.strip() for n in current.split(",") if n.strip()]
    if ref_name not in names:
        names.append(ref_name)
    knob_op.par.Bindparameterref.val = ", ".join(names)

    debug(f"[select1_callback] {knob_path}.Bindparameterref updated: '{current}' -> '{knob_op.par.Bindparameterref.val}'")
    return True


def onDropGetResults(comp, info):
    debug(f"[select1_callback] onDropGetResults called by {comp.path}, info: {info}")

    dropped_replicant_path = info["dragItems"][0]
    visual_container = op(dropped_replicant_path).op("visual")
    if not visual_container:
        debug(f"[select1_callback] No 'visual' container in {dropped_replicant_path}")
        return {"droppedOn": comp}

    slot_digit = int(comp.path[-1])
    debug(f"[select1_callback] Dropped onto slot {slot_digit}")

    # Ensure Sceneslot exists
    if "Sceneslot" not in [p.name for p in visual_container.pars()]:
        page = visual_container.appendCustomPage("Slot")
        page.appendInt("Sceneslot", label="Scene Slot")
        debug(f"[select1_callback] Created 'Sceneslot' param for {visual_container.path}")
    visual_container.par.Sceneslot = slot_digit

    table = op('/project1/lib/visual_bindings')
    if not table:
        debug(f"[select1_callback] ERROR: Missing /project1/lib/visual_bindings")
        return {"droppedOn": comp}

    debug_table(table, msg=f"BEFORE clearing knobs for slot {slot_digit}")
    _clear_slot_knobs(op(dropped_replicant_path))

    mapping_summary = []

    for r in range(1, table.numRows):
        replicant_name = table[r, 0].val
        if replicant_name != visual_container.parent().name:
            continue

        param_name = table[r, 1].val
        bind_type = table[r, 2].val
        value = table[r, 3].val
        orig_slot = int(table[r, 4].val) if table[r, 4].val.isdigit() else 1

        par = getattr(visual_container.par, param_name, None)
        if not par:
            debug(f"[select1_callback][Row {r}] Param '{param_name}' not found on {visual_container.path}")
            continue

        debug(f"[select1_callback][Row {r}] Processing {param_name}: type={bind_type}, value={value}, orig_slot={orig_slot}")

        if bind_type == "bindExpr":
            knob_match = re.search(r"knob(\d+)", value, re.IGNORECASE)
            if knob_match:
                base_knob = int(knob_match.group(1))
                slot_diff = slot_digit - orig_slot
                new_knob = base_knob + slot_diff * 8
                new_value = re.sub(r"knob\d+", f"knob{new_knob}", value)

                par.bindExpr = new_value
                table[r, 3].val = new_value
                table[r, 4].val = str(slot_digit)

                if _set_bindparameterref(new_knob, param_name):
                    mapping_summary.append(f"knob{new_knob} <- {param_name}")

                debug(f"[select1_callback][Row {r}] {param_name}: remapped knob{base_knob} -> knob{new_knob}")
            else:
                par.bindExpr = value
                table[r, 4].val = str(slot_digit)
                debug(f"[select1_callback][Row {r}] {param_name}: bindExpr applied (no knob)")

        elif bind_type == "expr":
            par.expr = value
            table[r, 4].val = str(slot_digit)
            debug(f"[select1_callback][Row {r}] {param_name}: expr applied")

    debug_table(table, msg=f"AFTER processing slot {slot_digit}")

    try:
        op(f"/project1/scene_selector{slot_digit}/select1").par.top = visual_container.path + "/out1"
        op(f"/UI/parameter{slot_digit}").par.op = visual_container.path
        debug(f"[select1_callback] Linked {visual_container.path} to scene_selector{slot_digit} + UI")
    except Exception as e:
        debug(f"[select1_callback] Linking failed: {e}")

    if mapping_summary:
        debug(f"[select1_callback] Mapping summary: {', '.join(mapping_summary)}")
    else:
        debug(f"[select1_callback] Mapping summary: (none)")

    return {"droppedOn": comp}


# Drag callbacks
def onDragStartGetItems(comp, info):
    debug(f"[select1_callback] onDragStartGetItems: {comp.path}")
    return [comp]

def onHoverStartGetAccept(comp, info):
    debug(f"[select1_callback] onHoverStartGetAccept: {comp.path}")
    return True