# base COMP with extension
base = op(f'{parent(2)}')

def onRemoveReplicant(comp, replicant):
    # print("remove replicants")
    # parent().StoreCurrentValues(param_name="Knoblevelcolorr")
    # parent().StoreCurrentValues(param_name="Knoblevelcolorg")
    # parent().StoreCurrentValues(param_name="Knoblevelcolorb")
    # parent().StoreCurrentValues(param_name="Mfthue")
    # parent().StoreCurrentValues(param_name="Bindparameterref")
    # parent().StoreCurrentValues(param_name="Value0")

    replicant.destroy()
    return


def onReplicate(comp, allOps, newOps, template, master):
    for c in newOps:        
        # c.display = True
        # c.render = True
        c.par.display = 1

        # reset LED status to make it susceptable to new values
        midiout = c.op("constant1")
        midiout.par.value0 = 0
        
        # recreate knob colors
        try:
            base.ChangeKnobColor(c)
            print("ran changeLED script onReplicate")
        except Exception as e:
            print("didn't run chopexec2")
            print("Error:", e)
        
        c.tags.add("knob")
        # c.par.clone = comp.par.master
    pass    

    # parent().DelayHelper(parent().ApplyAssignments, delay_frames=120)

    return
