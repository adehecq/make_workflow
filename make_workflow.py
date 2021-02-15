#!/bin/env python
#
# Utilities to generate an automated workflow with GNU make
# makefile_init is used to initialize the make, then makefile_append or makefile_secondary to add commands and makefile_run to run the workflow.
# Amaury Dehecq
# 03/2019

import os, sys
from tempfile import NamedTemporaryFile, mkstemp
from subprocess import call

class Workflow():

    def __init__(self, filename=None, title=None, overwrite=False):
        """
        Used to initialize the makefile. Will generate a main function for the makefile. Optionally, will display a title string at beginning of execution.
        filename: str, path to the makefile (Default is None, i.e. generate a temporary file)
        title: string to display at the beginning of the execution
        """

        # Create and open temporary file
        if filename==None:
            tmpf = NamedTemporaryFile(mode='w+')
            filename = tmpf.name
            f = tmpf.file
            self.tmpf = tmpf   # Keep otherwise file will be deleted
            self.filename = tmpf.name
            
        # Open chosen file 
        else:
            # If file exists and overwrite+False, just open the file in append mode. Won't work for temporary files though as self.tmpf is deleted.
            if os.path.exists(filename) & (overwrite==False):
                f = open(filename, 'a+')  # append and writing
                f.seek(0)
                self.filename = filename
                self.f = f
                return
            else:
                f = open(filename, 'w+')  # writing and reading
                self.filename = filename

        # Write header
        f.write(".PHONY: MAIN\n\n")

        # Write MAIN line, without title
        if title is None:
            f.write("MAIN: \n\n")

        # with title
        else:
            f.write("MAIN: pre-build \n\n")
            f.write("pre-build:\n\t@printf '%s\\n'\n\n" %title)

        # Add a function to list missing outputs, call with 'make list'
        f.write("list:\n")
        f.write("\t@printf '** Missing outputs **\\n'\n")
        f.write("\t@$(MAKE) -n --debug -f $(lastword $(MAKEFILE_LIST)) | sed -n -e 's/^.*Must remake target //p' | sed -e '/MAIN/d' | sed -e '/pre-build/d'\n\n")

        # save
        f.flush()
        self.f = f

    def append(self, cmds, inputs, outputs, title=None, secondary=False, soft_inputs=[], verbose=True):
        """
        Add a new list of commands to the Makefile with given outputs and inputs and display a title string at beginning of excution.
        Commands can be a single command or a list of commands.
        If secondary set to True, will consider all outputs of that command as secondary and the command won't be re-run if the files are deleted.
        If verbose set to False, will print stdout to /dev/null.
        """
        
        # Convert potential lists into string with space separator
        outputs = check_args_inout(outputs)
        inputs = check_args_inout(inputs)
        soft_inputs = check_args_inout(soft_inputs)

        # Write target:deps line
        if len(soft_inputs)>0:
            self.f.write("\n%s : %s | %s\n" % (outputs, inputs, soft_inputs))
        else:
            self.f.write("\n%s : %s\n" % (outputs, inputs))

        # Add command for title
        if title is not None:
            self.f.write("\t@printf '%s\\n'\n" %escape_char(title))

        # Add all commands
        cmds = check_args_cmd(cmds)

        for cmd in cmds:
            # Escape special characters
            #cmd = escape_char(cmd)

            # Add stdout option
            if not verbose:
                cmd += ' 1> /dev/null'

            # print command with + symbol and green color
            self.f.write("\t-@echo '[32m+%s[0m'\n" %cmd)

            # command to be run
            self.f.write("\t@%s\n" %cmd)                       

        ## Need to update the MAIN function to add new outputs ##
        # Only if outputs are not secondary (intermediate) files
        if secondary==False:
            # Read the text and replace MAIN
            filetext = ''
            self.f.seek(0)
            for line in self.f:
                if line[:4]=='MAIN':
                    line = ' '.join([line.rstrip(),outputs,'\n'])
                    filetext += line
                else:
                    filetext += line

            # Write to file
            f = open(self.filename,'w')
            f.write(filetext)
            f.flush()
            self.f = open(self.filename,'a+')

        # if files are secondary, need to specify
        else:
            self.f.write("\n.SECONDARY : %s\n" %(outputs))
            self.f.flush()

    def clean(self, cmds):
        """
        Add a clean target to the Makefile to perform any additional cleaning commands as part of the workflow.
        Commands can be a single command or a list of commands.
        """
        
        # Write clean line
        self.f.write("\nclean : \n")

        # Add all commands
        cmds = check_args_cmd(cmds)

        for cmd in cmds:
            # print command with + symbol and green color
            self.f.write("\t-@echo '[32m+%s[0m'\n" %cmd)

            # command to be run
            self.f.write("\t@%s\n" %cmd)                       
            self.f.flush()
        
    def display(self):
        """
        Print the current makefile to the screen.
        """
        self.f.seek(0)
        filetext = self.f.read()
        print(filetext)
        #os.system('cat %s' %self.filename)
        


    def run(self, njobs=1, dryrun=False, debug=False, force=False, clean=False, other_args=None):
        """
        Run the makefile with njobs parallel jobs.
        njobs: int, number of parallel jobs to run.
        dryrun: bool, set to True to print the commands without running them.
        debug: bool, set to True to run in debug mode.
        force: bool, set to True to ignore errors and keep the worflow running.
        clean: bool, set to True to run the clean command as well
        other_args: str, any other argument to pass to make
        """
        cmd = "make -f %s" %self.filename

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
        if clean:
            cmd += ' clean'
            
        # Allow any other arguments to be passed
        if other_args is not None:
            cmd += ' ' + other_args 

        # Run make
        call(cmd.split())

        

def check_args_inout(args):
    """
    Accepted arguments for input/outputs are string (in case a single input/output), or some kind of list (list, tuple, numpy array). Convert the latter into a string with a space delimiter for the makefile.
    Remove redundant slashes in filenames as it will be recognized as a different file by make.
    """
    # To comply with both Python3 and 2, string must be detected first
    # in Python3, string have __iter__ attribute too
    if isinstance(args,str):
        if len(args)>0:   # exclude empty string
            args = os.path.normpath(args)
    elif hasattr(args,'__iter__'):  # should work for list, tuples, numpy arrays
        args = [ os.path.normpath(arg) for arg in args ]
        args = ' '.join(args)
    else:
        print("ERROR: argument must be iterable (list, tuple, array) or string")
        print(args)
        sys.exit()

    return args


def check_args_cmd(args):
    """
    Accepted commands for all functions are string (in case a single command), or some kind of list (list, tuple, numpy array). Convert both cases to list.
    """    
    # To comply with both Python3 and 2, string must be detected first
    # in Python3, string have __iter__ attribute too
    if isinstance(args,str):
            args = [args,]
    elif hasattr(args,'__iter__'):  # if arg is iterable
        pass
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
