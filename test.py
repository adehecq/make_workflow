#!/usr/bin/env python

# Test the makefile_utils for Python
# Amaury Dehecq
# 03/2019


import make_workflow as mw
import os, sys    


# Initialize workflow
mw.makefile_init('Makefile',targets=['hello2','hello3'],title="*** Test flow ***")


# Create some text file
hello1_ins = []
hello1_outs = ["hello1"]
hello1_cmds = ["echo foo > "+hello1_outs[0] ]
mw.makefile_append('Makefile',hello1_cmds, hello1_ins, hello1_outs, title='\n** Hello1 **')

# Then, export
hello2_outs = ["hello2"]
hello2_cmds = ["sed 's/foo/faa/' "+hello1_outs[0]+" > "+hello2_outs[0]]
mw.makefile_append('Makefile', hello2_cmds, hello1_outs, hello2_outs, title='\n** Hello2 **')

# Another target, do not depend on either hello1 & 2
hello3_ins = []
hello3_outs = ["hello3"]
hello3_cmds = ["echo bar > "+hello3_outs[0]]
mw.makefile_append('Makefile',hello3_cmds, hello3_ins, hello3_outs, title='\n** Hello3 **')

# Finaly, create and run workflow
mw.makefile_run('Makefile',njobs=1)
