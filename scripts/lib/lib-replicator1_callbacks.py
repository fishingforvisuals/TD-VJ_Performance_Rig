# me - this DAT
#
# comp - the replicator component which is cooking
# allOps - a list of all replicants, created or existing
# newOps - the subset that were just created
# template - table DAT specifying the replicator attributes
# master - the master operator
#


def onRemoveReplicant(comp, replicant):

    replicant.destroy()
    return


def onReplicate(comp, allOps, newOps, template, master):

    for c in newOps:
        # run("op('{}').viewer = False".format(c.path), delayFrames=1)
        # c.render = True
        c.par.display = 1
        # c.par.clone = comp.par.master
        c.op("visual").par.enableexternaltoxpulse.pulse()
        op("video_input").outputConnectors[0].connect(c.inputConnectors[0])
        c.tags.add("visual")
        # c.op("visual").par.w = 400
        # c.op("visual").par.h = 300
        c.op("visual").par.hmode = 1
        c.op("visual").par.vmode = 1
        # c.op("visual").par.display = 0
        # parent().SetupThumbnail(c)
        # parent().RestoreBindings(c)
        c.par.alignorder = c.digits
        pass

    return
