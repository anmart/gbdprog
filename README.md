# gbdprog
Gameboy Disassembly Progress Calculator

---
gbdprog is a small python3 script meant to give a rough estimate of how far along a gameboy disassembly is. It was originally written for [poketcg](https://github.com/pret/poketcg) but I'm slowly adapting it to follow syntax changes from other disassemblies (such as those automatically generated through [mgbdis](https://github.com/mattcurrie/mgbdis).

It can check for remaining incbins to tell you how many bytes of the baserom are still being included, and can search for unnamed labels (those that contain the location at the end) through the sym file.
