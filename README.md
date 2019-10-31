
# gbdprog
 Gameboy Disassembly Progress Calculator

## About
gbdprog is a small python3 script meant to give a rough estimate of how far along a gameboy disassembly is. It was originally written for [poketcg](https://github.com/pret/poketcg), but it has been adapted to work with other disassemblies (such as those automatically generated through [mgbdis](https://github.com/mattcurrie/mgbdis)).

## Features

 - **Report amount of bytes being included from a baserom**
	 - Can use the project's Map file to generate a percentage of bytes accounted for
	 - Lists a breakdown of what bank bytes are included from
 - **Report symbols that are unnamed** (i.e. symbols that have their own location in the name)
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
[TODO]
