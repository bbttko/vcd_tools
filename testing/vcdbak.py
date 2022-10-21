import re

variables = { "head":[6,chr(33),"01",0] }


# name width id reg startbit
'''
vaaaa = { 
	"head":[6,chr(33),"01",0],
	"EnRdB":[1,chr(34),"01",9],
	"EnRdA":[1,chr(35),"01",8],
	"mode":[2,chr(36),"09",0],
	"htren":[1,chr(37),"09",8],
	"adc":[10,chr(38),"23",0]
}
'''
variables = [
	("head",6,chr(33),"01",0),
	("EnRdB",1,chr(34),"01",9),
	("EnRdA",1,chr(35),"01",8),
	("mode",2,chr(36),"09",0),
	("htren",1,chr(37),"09",8),


	("iw",7,chr(39),"0A",8),

	("adc",10,chr(38),"23",0)
]

prev_value = dict()


def do_header(fh):
	# meta data
	fh.write("$version 1 $end\n")
	fh.write("$comment btko csv to vcd converter - serial sniffer output $end\n")
	fh.write("$timescale 100ns $end\n")

	# variables
	fh.write("$scope module TOP $end\n")
	for v in variables:
		(name, width, ident, addr_loc, startbit) = v
		if width == 1:
			fh.write(f"$var wire {width} {ident} {name} $end\n")
		else:
			fh.write(f"$var wire {width} {ident} {name}[{width-1}:0] $end\n")
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

	
if __name__ == "__main__":
	start_time = -1
	loop_time = 0
	linecounter = 1

	with open("putty.csv", "r") as f, open("out.vcd", 'w') as outfile:
		f.readline()
		do_header(outfile)
		for line in f:
			try:
				(t, op, addr, data) = re.split(',', line.strip())
			except ValueError:
				print(f"Error on line {linecounter}, skipping")
				linecounter = linecounter + 1
			else:
				if start_time == -1:
					start_time = t
				#print(f"{linecounter} {t},{op},{addr},{data}")
				linecounter = linecounter + 1
				
				# go through variable list to check
				for v in variables:
					(name, width, ident, addr_loc, startbit) = v
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
								

