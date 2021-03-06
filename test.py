#!/usr/bin/env python

# Test the make_worflow tools for Python
# Create three types of workflows, one without given name, one with given name that does not exist, one with given name that already exist and append commands
# Should create files hello1, hello2, hello3 and bar1, bar2, bar3.
#
# Amaury Dehecq
# 03/2019

import make_workflow as mw
from tempfile import NamedTemporaryFile


## Test flow 1 without filename ##

# Initialize workflow
wf = mw.Workflow(title="*** Test flow 1 ***", overwrite=True)

# Create some text file
wf.append("echo foo > hello1", "", "hello1", title='\n** Hello1 **')

# Then, export
wf.append("sed 's/foo/faa/' hello1 > hello2", "hello1", "hello2", title='\n** Hello2 **')

# Another target, do not depend on either hello1 & 2
wf.append("echo bar > hello3", "", "hello3", title='\n** Hello3 **')

# Finaly, create and run workflow
wf.run(njobs=1)


## Test flow 2 with given name ##

tmpf = NamedTemporaryFile()
wf2 = mw.Workflow(filename=tmpf.name,title="*** Test flow 2 ***", overwrite=True)

# Create some text file
wf2.append("echo foo > bar1", "", "bar1", title='\n** Bar1 **')

# Then, export
wf2.append("sed 's/foo/faa/' bar1 > bar2", "bar1", "bar2", title='\n** Bar2 **')

# Finaly, create and run workflow
wf2.run(njobs=1)


## Test flow 3 - append to existing file ##
wf3 = mw.Workflow(filename=tmpf.name, overwrite=False)

wf3.append("echo bar > bar3", "", "bar3", title='\n** Bar3 **')

# Finaly, create and run workflow
wf3.run(njobs=1)


## Test flow 4 - test secondary files and clean ##

# Initialize workflow
wf = mw.Workflow(title="*** Test flow 4 - Secondary and clean ***", overwrite=True)

# Create some text file
wf.append("echo foo > bye1", "", "bye1", title='\n** bye1 **')

# Create a first intermediate file
wf.append("sed 's/foo/faa/' bye1 > bye2", "bye1", "bye2", title='\n** bye2 **', secondary=True)

# Create a second intermediate file
wf.append("sed 's/faa/fii/' bye2 > bye3", "bye2", "bye3", title='\n** bye3 **', secondary=True)

# Create final file
wf.append("cp bye3 bye4", "bye3", "bye4", title='\n** bye4 **')

# Add a clean command
wf.clean(['rm -f bye2', 'rm -f bye3'])

# Create and run workflow - second call runs the clean commands
wf.run(njobs=1)
wf.run(njobs=1, clean=True)
