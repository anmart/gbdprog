#!/usr/bin/env python3
import subprocess
import math
import argparse

# global defaults
banks = 0x40
grepDir = "."
incPrintFormat = "04x"

# TODO: percentage and entire func parser change

def main():
	parser = argparse.ArgumentParser(description='Progress checker for poketcg')
	parser.add_argument('-i', '--inc', action='store_true', help="Turns on include report")
	parser.add_argument('-d', '--directory', default=grepDir, help="Override include search directory. Ignores if include report is off")
	parser.add_argument('-a','--add', default=None, help="Number of bytes that are inc'd using unsupported methods.")
	parser.add_argument('-p','--print_format', default=incPrintFormat, help="Format string for printing byte amounts in include report. Ignores if include report is off")
	parser.add_argument('-n','--no_warn', action='store_true', help="Suppress warnings about unsupported inc methods.")
	parser.add_argument('-s', '--symfile', default=None, type=argparse.FileType('r'), help="Turns on Unnamed Symbol report using given sym file")
	parser.add_argument('-f', '--function_source', action='store_true', help='Shows a breakdown of what bank each unnamed function comes from. Ignores if symfile report is off')
	parser.add_argument('-o', '--other_unnamed', action='store_true', help='Shows all other unnamed symbols and a count of how many there are. Ignores if symfile report is off')
	parser.add_argument('-l', '--list_funcs', nargs="+", default=None, help="Lists every unnamed function in the given banks. WILL BE LONG. ignores if symfile report is off")
	parser.add_argument('-w', '--words', action='store_true', help="Turns on Word report, which shows all nonzero magic number words")

	args = parser.parse_args()

	if args.inc:
		addedBytes = 0
		if args.add != None:
			addedBytes = int(args.add,0)
		reportINCROMs(args.directory, addedBytes, args.no_warn, args.print_format)
		print("\n")

	if args.symfile != None:
		# parse the list command
		listBankSet = set([])
		if args.list_funcs != None:
			listBankSet = parseBankList(args.list_funcs)
		reportUnnamedSymbols(args.symfile,listBankSet, args.function_source, args.other_unnamed)
		print("\n")

	if args.words:
		reportUnnamedWords(args.directory)

def tryIncWarn(skip, line):
	if not skip:
		print("The following line was not accepted, possibly due to using a constant. Please use -a to add bytes that are included using constants")
		print(line)

def tryWeirdWarn(skip, line):
	if not skip:
		print("The following line was not accepted, due to a strange number of $ symbols.")
		print(line)

# does not support expressions or constants. Just checks very standard incbin/incroms
def reportINCROMs(incDir, addedBytes, skipWarning, printFormat):
	grep1Proc = subprocess.Popen(['grep', '-r', 'INCBIN', incDir], stdout=subprocess.PIPE)
	grep2Proc = subprocess.Popen(['grep', '-r', 'INCROM', incDir], stdout=subprocess.PIPE)
	targetLines = grep1Proc.communicate()[0].decode().split('\n')
	targetLines += grep2Proc.communicate()[0].decode().split('\n')
	incBytes = [0]*banks
	incByteTotal = 0
	for line in targetLines:
		line = line.lower() # ignore case

		# ignore the actual definition of the macro
		if 'macro' in line:
			continue

		# ignore anything in tools
		if '/tools/' in line:
			continue

		# ignore binary files in case swp's exist
		if 'binary file' in line:
			continue

# different starting here
		# find the last two hex location values
		splitLine = line.split("$")

		### Consider possible patterns for either inc type

		lineParts = len(splitLine)
		if lineParts <= 1:
			# including an entire file (ignore) or including with unsupported constant
			if "," in line: # more than one arg, just not split
				tryIncWarn(skipWarning, line)
			continue

		elif lineParts == 2:
			# only one hex value, other is an unsupported constant
			tryIncWarn(skipWarning, line)
			continue

		elif lineParts == 3:
			# INCROM with 2 arguments, or INCBIN with an unsupported constant or only 2 args
			if "incrom" in line:
				incEnd = int(splitLine[-1],16)
				incStart = int(splitLine[-2].split(",",1)[0],16)
			else:
				if "-" in splitLine[-1]:
					tryIncWarn(skipWarning, line)
					continue
				else:
					incDiff = int(splitLine[-1],16)
					incStart = int(splitLine[-2].split(",",1)[0],16)
					incEnd = incStart + incDiff

		elif lineParts == 4:
			# INCBIN with 3 arguments, or very odd INCROM
			if "incrom" in line:
				tryWeirdWarn(skipWarning, line)
			else:
				incStart = int(splitLine[-3].split(",",1)[0],16)
				if "-" in splitLine[-2]:
					incEnd = int(splitLine[-2].split("-",1)[0].strip(),16) # isolate the second arg and use it as the end
				else:
					print("Not sure what to do with line, possible arithmetic? " + line)
					continue

		else:
			# Absolutely no clue what this could be
			tryWeirdWarn(skipWarning, line)

		incBank = math.floor(incStart / 0x4000)
		diff = incEnd - incStart
		incBytes[incBank] += diff
		incByteTotal += diff
	incByteTotal += addedBytes
	print("Total: " + format(incByteTotal, printFormat) + " bytes")
	print("Made up of the following: ")

	baseNote = ""
	if "x" in printFormat:
		baseNote = "0x"

	for i in range(0,banks):
		if incBytes[i] == 0:
			continue

		bankName= "bank" + format(i,"02") + ": "
		if i == 0:
			bankName = "home:   "

		bytesString = format(incBytes[i],printFormat)
		formattingStrings = " "*(8-len(bytesString)) 
		print(bankName + baseNote + bytesString + formattingStrings + "bytes")
	if addedBytes > 0:
		bytesString = format(addedBytes, printFormat)
		print("Additional Bytes: " + baseNote + bytesString)


# reads sym files and looks for instances of tcgdisasm's automatic symbols
def reportUnnamedSymbols(symfile, listBankSet, showFunctionBanks, showOtherUnnamed):
	data = symfile.read().split("\n")

	# format [ [ "type" : number ], ... ]
	typeCounts = []

	# to cut back on for loops I'll manually list the super common ones, such as Func
	funcCounts = [0]*banks
	funcCount = 0
	wramCount = 0
	sramCount = 0
	hramCount = 0

	labelTotal = 0
	localLabelTotal = 0
	unnamedLocalLabelTotal = 0
	unnamedLabelTotal = 0

	# expecting all lines to be formated as `bank:addr name`
	for line in data:

		splitline = line.split(":")

		# line not formatted as expected
		if len(splitline) < 2:
			continue

		# at this point it's probably some form of label
		if "." in line:
			localLabelTotal += 1
		else:
			labelTotal += 1

		bank = int(splitline[0], 16)
		splitline = splitline[1].split(" ")

		# line not formatted as expected
		if len(splitline) < 2:
			continue

		localAddr = int(splitline[0], 16)
		name = splitline[1]

		globalAddr = bank*0x4000 + localAddr
		if bank > 0:
			globalAddr -= 0x4000
		
		globalAddrString = format(globalAddr,"04x")
		localAddrString = format(bank,"03x") + "_" + format(localAddr,"04x") # for mgbdis format
		if name.endswith(globalAddrString) or name.endswith(localAddrString):

			# don't pay as much attention to local labels
			if "." in line:
				unnamedLocalLabelTotal += 1
				continue
			else:
				unnamedLabelTotal += 1

			# get different label type depending on which name.endswith matched
			if name.endswith(localAddrString): # start with local as it's harder to match
				labelType = name[0:len(localAddrString)*-1]
			else:
				labelType = name[0:len(globalAddrString)*-1]

			if labelType.endswith("_"):
				labelType = labelType[0:-1]

			# take care of the common ones before looping
			if labelType == "Func":
				if bank in listBankSet:
					print("bank " + format(bank,'02x') + ":" + name)
				funcCounts[bank] += 1
				funcCount += 1
				continue
			elif labelType == "w":
				wramCount += 1
				continue
			elif labelType in ["s0","s1","s2","s3"]: # all that are listed in sram.asm
				sramCount += 1
				continue
			elif labelType == "h":
				hramCount += 1
				continue

			foundType = False
			for tc in typeCounts:
				if tc[0] == labelType:
					tc[1] += 1
					foundType = True

			if not foundType:
				typeCounts.append([labelType,1])
					

	# do some sorting.
	typeCounts = sorted(typeCounts, key = lambda x: x[1], reverse = True) 

	namedLabelTotal = labelTotal - unnamedLabelTotal
	namedLabelPercent = round((namedLabelTotal / labelTotal)*100, 3)
	namedLocalLabelTotal = localLabelTotal - unnamedLocalLabelTotal
	namedLocalLabelPercent = round((namedLocalLabelTotal / localLabelTotal)*100, 3)

	print("Named Labels: " + str(namedLabelTotal) + "/" + str(labelTotal) + " (" + str(namedLabelPercent) + "%)")
	print("Named Local Labels: " + str(namedLocalLabelTotal) + "/" + str(localLabelTotal) + " (" + str(namedLocalLabelPercent) + "%)")
	print()
	print("func count:   " + str(funcCount))
	if showFunctionBanks:
		for i in range(0,banks):
			if funcCounts[i] == 0:
				continue
			bank = "bank" + format(i,"02x") + ":"
			if i == 0:
				bank = "home:  "
			print("\t" + bank + " " + str(funcCounts[i]))

	print("wram count:   " + str(wramCount))
	print("sram count:   " + str(sramCount))
	print("hram count:   " + str(hramCount))
	if showOtherUnnamed:
		print()
		print("Additional types:")

		for tc in typeCounts:
			spaces = " " * (30 - len(tc[0]))
			if tc[1] == 1:
				print(tc[0])
				continue
			print(tc[0] + spaces + "x" + format(tc[1],"02"))

def parseBankList(strList):
	retSet = set([])
	for bankName in strList:
		if bankName == "home":
			retSet.add(0)
		elif bankName.startswith("bank"):
			retSet.add(int(bankName[4:],16))
		else:
			retSet.add(int(bankName,0))
	return retSet

# TODO: This works roughly, but it could be rewritten to be a lot better.
# Make the search just for $.... then after discarding things we don't want, 
# split the list by $ and see how many valid 4 digit hex numbers we can find
# Can use int(str[x][0:4], 16) and catch the error to determine if it's legit.
def reportUnnamedWords(searchDir):
	grep1Proc = subprocess.Popen(['grep', '-r', '\\$....$', searchDir], stdout=subprocess.PIPE)
	grep2Proc = subprocess.Popen(['grep', '-r', '\\$....]', searchDir], stdout=subprocess.PIPE) # grep doesn't seem to like or's
	targetLines = grep1Proc.communicate()[0].decode().split('\n')
	targetLines += grep2Proc.communicate()[0].decode().split('\n')
	fileWordList = []
	longest = 0
	for line in targetLines:
		line = line.lower()
		if ".asm" not in line:
			continue
		if "binary" in line:
			continue
		if "incrom" in line or "incbin" in line:
			continue
		fileName = line.split(":")[0]
		found = False
		for i in range(len(fileWordList)):
			if fileName == fileWordList[i][0]:
				found = True
				fileWordList[i][1] += 1
		if not found:
			fileWordList.append([fileName,1])
			if len(fileName) > longest:
				longest = len(fileName)

	fileWordList = sorted(fileWordList, key = lambda x: x[1], reverse = True) 

	for fileList in fileWordList:
		spaces = " " * (longest + 5 - len(fileList[0]))
		print(fileList[0] + ":" + spaces + "x" + format(fileList[1], "d"))

if __name__ == '__main__':
	main()
