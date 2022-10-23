import re
import sys
from config import *


version = 1.0

# dict to keep previous values
prev_value = dict()


def fromgroup(grp):
	'''
		checks if parameter grp belongs to a group
		returns group which it belongs to, else None
	'''
	for g,gi in groups.items():
		if grp in gi:
			return g
	return(None)


def do_header(fh):
	'''
		sets up value change dump header
	'''
	# meta data
	fh.write(f"$version {version} $end\n")
	fh.write("$comment\n\tbtko csv to vcd converter - serial sniffer output\n\tuse vcd2wlf for modelsim\n$end\n")
	fh.write("$timescale 100ns $end\n")

	# preassign identifiers in variables
	uniqueChar = 33	# unique ascii range from 33 - 126
	for k, v in variables.items():
		variables[k].append(chr(uniqueChar))
		uniqueChar = uniqueChar + 1

	# group signals
	for v,vi in variables.items():
		thegroup = fromgroup(v)
		if thegroup == None:
			try:
				groups["top"]
			except:
				groups["top"] = [v]
			else:
				groups["top"].append(v)

	# variables 
	fh.write("$scope module top $end\n")
	for name in groups["top"]:
		(addr_loc, startbit, width, ident) = variables[name]
		if width == 1:
			fh.write(f"$var wire {width} {ident} {name} $end\n")
		else:
			fh.write(f"$var wire {width} {ident} {name}[{width-1}:0] $end\n")

	del(groups["top"])		# remove 'top' group
	
	# variables - other than top
	for groupname in groups.keys():
		fh.write(f"\t$scope module {groupname} $end\n")
		for groupitems in groups[groupname]:
			(addr_loc, startbit, width, ident) = variables[groupitems]
			if width == 1:
				fh.write(f"\t\t$var wire {width} {ident} {groupitems} $end\n")
			else:
				fh.write(f"\t\t$var wire {width} {ident} {groupitems}[{width-1}:0] $end\n")
		fh.write("\t$upscope $end\n")
		
	fh.write("$upscope $end\n")
	fh.write("$enddefinitions $end\n")
	



def value_changed(name, value):
	'''
		compares if "value" of "name" changed w.r.t. value in dict prev_value 
		returns True if changed, else False
	'''
	changed = True
	if name in prev_value.keys():		# check if value exists
		changed = (prev_value[name] != value)	# check if changed
		
	#if name == "PDW_en":
	#	print(f"pdw en value = {value}\n")
		
	prev_value[name] = value			# store previous value
	return changed						# return changed status
	
	'''
	try:
		prev_value[name]
	except KeyError:
		prev_value[name] = value
		return True
	else:
		if prev_value[name] != value:
			prev_value[name] = value
			return True
		else:
			return False
	'''
		
'''
	main proc
'''	
if __name__ == "__main__":
	start_time = -1
	loop_time = 0
	linecounter = 1
	t_prev = 0

	if len(sys.argv) != 2:
		print(f"{sys.argv[0]} <filename.csv>\n")
	else:
		filename = sys.argv[1]
		with open(filename, "r") as f, open("out.vcd", 'w') as outfile:
			f.readline()
			do_header(outfile)
			for line in f:
				try:
					(t, op, addr, data) = re.split(',', line.strip())
				except ValueError:
					print(f"Error near line {linecounter}, skipping")
				else:
					if start_time == -1: start_time = t
					
					# go through variable list to check
					for name, v in variables.items():
						(addr_loc, startbit, width, ident) = v
						if (addr == addr_loc):
						
							# update time, loop to cater for wraparound over 0xFFFFFF
							if int(start_time,16) > int(t,16):
								loop_time = loop_time + 1
							t_delta = int(t,16) + (loop_time * int("0xffffff",16)) - int(start_time,16)
							t_changed = (t_prev != t_delta)
							
							if width == 1:
								value = (int("0x" + data, 16) & (1 << startbit)  ) >> startbit
								if value_changed(name, value):
									if t_changed: outfile.write(f"#{t_delta}\n")
									outfile.write(f"{value}{ident}\n")
							else:
								value = int("0x" + data, 16)
								mask = int(('1' * width), 2) << startbit
								bits = bin((value & mask) >> startbit)[2:].zfill(width)
								if value_changed(name, bits):
									if t_changed: outfile.write(f"#{t_delta}\n")
									outfile.write(f"b{bits} {ident}\n")
									
							t_prev = t_delta	# record t_delta
				linecounter = linecounter + 1

