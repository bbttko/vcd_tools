import re


# 	"name"      [addr,startbit,width]
variables = { 
	"head":		["01",0,6],
	"EnRdB":	["01",9,1],
	"EnRdA":	["01",8,1],
	"SnsFltEnR":["04",9,1],
	"MwinOpen":	["05",14,1],
	# "undef":	["08",2,1],
	"mode":		["09",0,2],
	"dfctl":	["09",3,2],
	"htren":	["09",8,1],
	"wtroff":	["09",9,1],
	"rdivbias":	["09",11,1],
	"iw": 		["0A",8,7],
	"os": 		["0A",0,5],
	"dur": 		["0B",0,5],
	"iwtr": 	["0B",8,3],
	"iwtf": 	["0B",5,3],
	"ostr":		["0B",12,3],
	"patpolEN":	["0F",15,1],
	"patpoldet":["0F",4,1],
	"pdw":		["10",0,5],
	"wht_w":	["1B",8,8],
	"wht_r":	["1B",0,8],
	"fltamux":	["22",15,1],
	"tmux":		["22",14,1],
	"digon":	["22",7,1],
	"adc":		["23",0,10],
	"RdGainA":	["32",4,4],
	"RdBiasA":	["32",8,8],
	"RdGainB":	["35",4,4],
	"RdBiasB":	["35",8,8]
}

groups = {
	"writer": 	["wtroff","iw","os","dur","iwtr","iwtf","ostr","pdw"],
	"pdw": 		["patpolEN","patpoldet"],
	"heater":	["htren","wht_w","wht_r"],
	"reader": 	["EnRdB","EnRdA","rdivbias","RdGainB", "RdGainA", "RdBiasA", "RdBiasB"]
}

prev_value = dict()


def fromgroup(grp):
	for g,gi in groups.items():
		if grp in gi:
			return g
	return(None)


def do_header(fh):
	# meta data
	fh.write("$version 1 $end\n")
	fh.write("$comment\n\tbtko csv to vcd converter - serial sniffer output\n\tuse vcd2wlf for modelsim\n$end\n")
	fh.write("$timescale 100ns $end\n")

	# preassign identifiers in variables
	uniqueChar = 33
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
			
	del(groups["top"])
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
def init():
	# preassign identifiers in variables
	uniqueChar = 33
	for k, v in variables.items():
		variables[k].append(chr(uniqueChar))
		uniqueChar = uniqueChar + 1
'''
	
	
if __name__ == "__main__":
	start_time = -1
	loop_time = 0
	linecounter = 1

	# init()
	with open("putty.csv", "r") as f, open("out.vcd", 'w') as outfile:
		f.readline()
		do_header(outfile)
		for line in f:
			try:
				(t, op, addr, data) = re.split(',', line.strip())
			except ValueError:
				print(f"Error near line {linecounter}, skipping")
			else:
				if start_time == -1:
					start_time = t
				#print(f"{linecounter} {t},{op},{addr},{data}")
				# linecounter = linecounter + 1
				
				# go through variable list to check
				for name, v in variables.items():
					(addr_loc, startbit, width, ident) = v
					if (addr == addr_loc):
						# update time
						if int(start_time,16) > int(t,16):
							loop_time = loop_time + 1
						t_delta = int(t,16) + (loop_time * int("0xffffff",16)) - int(start_time,16)
						
						
						if width == 1:
							value = (int("0x" + data, 16) & (1 << width)  ) >> width
							if value_changed(name, value):
								outfile.write(f"#{t_delta}\n")
								outfile.write(f"{value}{ident}\n")
								
						else:
							value = int("0x" + data, 16)
							mask = int(('1' * width), 2) << startbit
							bits = bin((value & mask) >> startbit)[2:].zfill(width)
							if value_changed(name, bits):
								outfile.write(f"#{t_delta}\n")
								outfile.write(f"b{bits} {ident}\n")
			linecounter = linecounter + 1
								

