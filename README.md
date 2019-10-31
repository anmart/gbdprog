

# gbdprog
 Gameboy Disassembly Progress Calculator

## About
gbdprog is a small python3 script meant to give a rough estimate of how far along a gameboy disassembly is. It was originally written for [poketcg](https://github.com/pret/poketcg), but it has been adapted to work with other disassemblies (such as those automatically generated through [mgbdis](https://github.com/mattcurrie/mgbdis)).

Written in Python 3

## Features

 - **Report amount of bytes being included from a baserom**
	 - Can use the project's Map file to generate a percentage of bytes accounted for
	 - Lists a breakdown of what bank bytes are included from
 - **Report unnamed symbols** (i.e. symbols that have their own location in the name)
	 - can list banks by the amount of unnamed symbols they have
	 - Shows a percentage of unnamed vs named symbols
	 - Can show a list of unique label prefixes (Any text before the location of the symbol)
	 - Can be fed a list of banks to name every single unnamed symbol in that bank.
 - **Report magic/unnamed Words** (straight hex 16 bit nonzero values)
	 - Shows a count of how many 16 bit words are written in the code with no symbol or constant.
	 - Shows a breakdown of what files contain how many magic words
	 - Has a(n overly) strict mode that hides certain values
 - Minimal run mode
	 - Good for quick webhook messages

## Usage

    usage: gbdprog.py [-h] [-e MAP] [--auto_map] [-i] [-d DIRECTORY] [-a ADD] [-m]
                      [-p PRINT_FORMAT] [-n] [-s SYMFILE] [-f] [-o]
                      [-l LIST_FUNCS [LIST_FUNCS ...]] [-w] [-t]
    
    Progress checker for poketcg
    
    optional arguments:
      -h, --help            show this help message and exit
      -e MAP, --map MAP     The project's Map file. Used to find various bank data
                            if not already defined. Use --auto_map to assume the
                            map file
      --auto_map            Assume the project's map file using the sym file
      -i, --inc             Turns on include report
      -d DIRECTORY, --directory DIRECTORY
                            Override include search directory. Ignored if include
                            report is off
      -a ADD, --add ADD     Number of bytes that are inc'd using unsupported
                            methods.
      -m, --minimal         Runs reports minimally where possible, using fewer
                            lines than normal
      -p PRINT_FORMAT, --print_format PRINT_FORMAT
                            Format string for printing byte amounts in include
                            report. Ignored if include report is off
      -n, --no_warn         Suppress warnings about unsupported inc methods.
      -s SYMFILE, --symfile SYMFILE
                            Turns on Unnamed Symbol report using given sym file
      -f, --function_source
                            Shows a breakdown of what bank each unnamed function
                            comes from. Ignored if symfile report is off
      -o, --other_unnamed   Shows all other unnamed symbols and a count of how
                            many there are. Ignored if symfile report is off
      -l LIST_FUNCS [LIST_FUNCS ...], --list_funcs LIST_FUNCS [LIST_FUNCS ...]
                            Lists every unnamed function in the given banks. WILL
                            BE LONG. ignored if symfile report is off
      -w, --words           Turns on Word report, which shows all nonzero magic
                            number words
      -t, --strict          Caused Word Report to be more strict, only allowing
                            end of line or ] at the end NOTE: NOT RECOMMENDED DUE
                            TO LINES WITH COMMENTS
    
    Examples:
    
    Simple useful run:
    	gbdprog -mis game.sym --auto_map
    Full report with too much info:
    	gbdprog -ifow -l home -s game.sym

