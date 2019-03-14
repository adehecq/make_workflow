#!/bin/env python
#
# Utilities to generate an automated workflow with GNU make
# makefile_init is used to initialize the make, then makefile_append or makefile_secondary to add commands and makefile_run to run the workflow.
# Amaury Dehecq
# 03/2019

import os, sys

def check_args_inout(args):
    """
    Accepted arguments for input/outputs are string (in case a single input/output), or some kind of list (list, tuple, numpy array). Convert the latter into a string with a space delimiter for the makefile.
    Remove redundant slashes in filenames as it will be recognized as a different file by make.
    """

    if hasattr(args,'__iter__'):  # should work for list, tuples, numpy arrays
        args = [ os.path.normpath(arg) for arg in args ]
        args = ' '.join(args)
    elif isinstance(args,str):
        args = os.path.normpath(args)
    else:
        print("ERROR: argument must be iterable (list, tuple, array) or string")
        print(args)
        sys.exit()

    return args


def check_args_cmd(args):
    """
    Accepted commands for all functions are string (in case a single command), or some kind of list (list, tuple, numpy array). Convert both cases to list.
    """
    
    if hasattr(args,'__iter__'):  # if arg is iterable
        pass
    elif isinstance(args,str):
            args = [args,]
    else:
        print("ERROR: argument must be iterable (list, tuple, array) or string")
        print(args)
        sys.exit()

    return args


def escape_char(string):
    """
    Escape special characters from string before passing to makefile.
    Maybe more characters will need to be added.
    """
    string = string.replace("'","\\'")  # escape '
    string = string.replace('"','\\"')  # escape "
    string = string.replace("\n","\\n")  # escape \n
    return string
    
    
def makefile_init(filename, targets, title=None):
    """
    Usage: init_makefile(filename,targets,[title])
    Used to initialize the makefile. Will generate a main function and main targets for the makefile. Optionally, will display a title string at beginning of execution.
    """

    # Open file and write initial line
    f = open(filename, 'w')
    f.write(".PHONY: MAIN\n\n")

    # if targets is iterable, create a string separated by spaces
    targets = check_args_inout(targets)

    # Write MAIN line
    if title is None:
        f.write("MAIN: %s\n\n" %targets)
    else:
        f.write("MAIN: pre-build %s\n\n" %targets)
        f.write("pre-build:\n\t@printf '%s\\n'\n\n" %title)
    f.close()

    
def makefile_append(filename, cmds, inputs, outputs, title=None):
    """
    Usage: makefile_append filename title target dependencies cmd1 cmd2...
    Will add a new list of commands to the makefile 'filename' with given outputs and inputs and display a title string at beginning of excution.
    commands can be a single command or a list of commands.
    """
    
    f = open(filename, 'a')

    # Convert potential lists into string with space separator
    outputs = check_args_inout(outputs)
    inputs = check_args_inout(inputs)

    f.write("\n%s : %s\n" %(outputs, inputs))
    
    if title is not None:
        f.write("\t@printf '%s\\n'\n" %escape_char(title))
    
    cmds = check_args_cmd(cmds)

    for cmd in cmds:
        # Escape special characters
        #cmd = escape_char(cmd)

        # print command with + symbol and green color
        f.write("\t-@echo '[32m+%s[0m'\n" %cmd)

        # command to be run
        f.write("\t@%s\n" %cmd)                       
        
    f.close()

    
def makefile_secondary(filename, second):
    """
    Usage makefile_secondary filename second 
    Add files to be considered as secondary, i.e., the files will not be recreated if deleted.
    """
    f = open(filename, 'a')
    f.write(".SECONDARY : %s\n" %second)
    f.close()

    
def makefile_run(filename, njobs=1, dryrun=False, debug=False, force=False, other_args=None):
    """
    Run the makefile with njobs parallel jobs.
    njobs: int, number of parallel jobs to run.
    dryrun: bool, set to True to print the commands without running them.
    debug: bool, set to True to run in debug mode.
    force: bool, set to True to ignore errors and keep the worflow running.
    other_args: str, any other argument to pass to make
    """
    cmd = "make -f %s" %filename

    # Check njobs option and append
    if isinstance(njobs,int):
        if njobs>1:
            cmd.append(' -j %i' %njobs)
    else:
        print("ERROR: njobs must be of type int")
        sys.exit()

    # Append other options
    if dryrun!=False:
        cmd += ' -n'
    if debug!=False:
        cmd += ' -d'
    if force!=False:
        cmd += ' -i'

    # Allow any other arguments to be passed
    if other_args is not None:
        cmd += ' ' + other_args 

    # Run make
    os.system(cmd)
