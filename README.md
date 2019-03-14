# make_workflow

*Python* and *bash* utilities to generate a workflow of file processing based on GNU make.
Many **processing workflows** involve reading and writing files with a set of commands, that must be done in a given order and some dependencies. This can be done easily within Python or Bash, but what if the **processing stops**, if you **update some intermediate files** and only want to start from there again, or if you want to run some steps in **parallel**... These tools provide a solution thanks to *GNU Make*.

## Example 
Let's consider the following workflow where 3 files are created:  
> echo foo > hello1  
> sed s/foo/faa/ hello1 > hello2  
> echo bar > hello3

We can summarize it as:  
-> hello1 -> hello2  
-> hello3  
There are two independant chains, no file is required to create hello1 and hello3, but hello1 is required for hello2.

The Python implementation with make_workflow is simple:

```python
import make_workflow as mw

# Initialize workflow. By default a temporary file is generated, but a path can be set here.
wf = mw.Workflow()

# Create some text file
# The append function takes as arguments a string/list of the commands, inputs and outputs.
wf.append("echo foo > hello1", "", "hello1")

# Use first file to create 2nd file
wf.append("sed 's/foo/faa/' hello1 > hello2", "hello1", "hello2")

# Create another file that does not require hello1 or 2
wf.append("echo bar > hello3", "", "hello3")

# Finaly run workflow
wf.run(njobs=1)
```

Let's save all this in test.py and see what happens:
> python test.py

+echo foo > hello1  
+sed s/foo/faa/ hello1 > hello2  
+echo bar > hello3  

Since no file exist yet, all commands are ran and the files created. If we run the command again... nothing happens as the file exist.

Let's then remove some files to see what happens.  
> rm hello3  
> python test.py

+echo bar > hello3

This time hello3 is missing, hence the last command is re-run **automatically**. The result would be similar with hello2 removed.

> rm hello1  
> python test.py

+echo foo > hello1  
+sed s/foo/faa/ hello1 > hello2  

If hello1 is removed, the first two commands are re-run **automatically**. The same thing would happen if hello1 was updated, with e.g. > touch hello1.

Finally, this can be used to run independant processes in parallel. here e.g., hello2 and hello3 can be processed at the same time by replacing the last line with:  
```python
wf.run(njobs=2)
```

By default, the makefile is saved in a temporary file and deleted at the end. It can be printed with the command `wf.display()`, or it can be saved at a given location at creation: `wf = mw.Workflow('Makefile')`

## Troubleshooting

**Warning :** These tools depend on make, therefore some issues could arise with different versions of make... Please report any issue.

**Windows users :** I haven't tested, but the creation of temporary file on Windows might cause issues. In that case, simply add a path to the makefile like this `wf = mw.Workflow('Makefile')`.
