#!/usr/bin/env python

# Test the make_worflow tools for Python
# Amaury Dehecq
# 03/2019


import make_workflow as mw
import os, sys    


# Initialize workflow
wf = mw.Workflow(title="*** Test flow ***")

# Create some text file
wf.append("echo foo > hello1", "", "hello1", title='\n** Hello1 **')

# Then, export
wf.append("sed 's/foo/faa/' hello1 > hello2", "hello1", "hello2", title='\n** Hello2 **')

# Another target, do not depend on either hello1 & 2
wf.append("echo bar > hello3", "", "hello3", title='\n** Hello3 **')

# Finaly, create and run workflow
wf.run(njobs=1)
