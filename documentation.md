# Documentation
## Dependencies
This program uses the following libraries
* re
* sys
* itertools
* logging
* pygraphviz

Apart from pygraphviz these are all part of the python standard libraries so should come included with your python installation.

To install pygraphviz run
```
pip install pygraphviz  
```
Depending on your permissions you may need to run it with the user flag
```
pip install pygraphviz --user
```

## Command line input
 To run the code via the command line, you should run the command as follows
 ```
python main.py example.txt
 ```
 Replacing example.txt with the text file of your language

## Forbidden strings
The following are non terminals in my grammar, and so can't be used in the language:

S,F,R,V,C,E,F,O,Q,A

Along with these, in parsing I use numbers as identifiers so none of the strings apart from constants should be pure numbers e.g. 1, however symbols including numbers e.g. cost1 are fine.

## Output
There are 3 output files
### parse.log
This is the log file, it uses standard python syntax for logs, and for a valid formula will only contain info statements.
### AST.png
This is an image of the Abstract Syntax Tree (AST) generated when parsing
### grammar.txt
This holds the generated grammar, using formal notation, in G the strings in the first set of brackets are the terminals, the second set of brackets is the terminals, then the two following characters are the production rule and start symbol, respectively.

Then the following lines detail the production rules

## Errors
For errors in the command line input, they will be printed back to the command line, for all other errors they will be logged in parse.log and the program will terminate with exit code 1.
