#!/usr/bin/bash

source make_workflow.sh

# Initialize workflow
makefile_init Makefile "hello2 hello3" "Test flow"

# Create some text file
makefile_append Makefile "Hello1" hello1 "" "echo foo > hello1"

# Then, export
makefile_append Makefile "Hello2" hello2 hello1 "sed 's/foo/faa/' hello1 > hello2"

# Another target, do not depend on either hello1 & 2
makefile_append Makefile "Hello3" hello3 "" "echo bar > hello3"

# Finaly, create and run workflow
make -f Makefile
