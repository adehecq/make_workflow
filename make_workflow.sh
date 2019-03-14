#!/bin/bash
#
# Utilities to generate an automated workflow with GNU make
# makefile_init is used to initialize the make
# Amaury Dehecq
# 7/11/2018

function makefile_init {
    # Usage: init_makefile filename target [title]
    # Used to initialize the makefile. Will generate a main function and main targets for the makefile. Optionally, will display a title string at beginning of execution
    printf ".PHONY: MAIN\n\n" > $1
    if [ -z "$3" ]
    then
	printf "MAIN: $2\n\n" >> $1
    else
	printf "MAIN: pre-build $2\n\n" >> $1
	printf "pre-build:\n\t%s\n\n" "@printf '$3\n'" >> $1
    fi
}


function makefile_append {
    # Usage: makefile_append filename title target dependencies cmd1 cmd2...
    # Will add a new list of commands to the makefile 'filename' with given targets and dependencies and display a title string at beginning of excution.
    # commands can be a single command or a list of commands
    filename=$1
    title=$2
    targets=$3
    deps=$4
    ma_cmds=("${@:5}")
    local cmd
    printf "\n$targets : $deps\n"  >> $filename
    printf "\t%s\n" "@printf '$title\n'" >> $filename
    for cmd in "${ma_cmds[@]}";
    do
    	# Remove special characters, need to make it exhaustive
    	cmd=${cmd/'/\\'}
    	cmd=${cmd/"/\\"}
    	cmd=${cmd/'\n'/'\\\n'}
	#printf "\n\n%s\n\n" "$cmd"
    	printf "\t%s\n" "-@echo '\n[32m+$cmd[0m'" >> $filename
    	printf "\t@%s\n" "$cmd" >> $filename
    done
}


function makefile_secondary {
    # Usage makefile_secondary filename second
    # Add files to be considered as secondary, i.e., the files will not be recreated if deleted.
    printf ".SECONDARY : $2\n" >> $1
}

