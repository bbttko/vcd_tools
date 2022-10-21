variables = { 
	"head":		["01",0,6],
	"EnRdB":	["01",9,1],
	"EnRdA":	["01",8,1],
	"SnsFltEnR":["04",9,1],
	"MwinOpen":	["05",14,1],
	"undef":	["08",2,1],
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
	"Reader": ["RdGainB", "RdGainA", "RdBiasA", "RdBiasB"],
	"Writer": ["dur","iwtr","ostr"]
}


def fromgroup(grp):
	for g,gi in groups.items():
		if grp in gi:
			return g
	return(None)


for v,vi in variables.items():
	thegroup = fromgroup(v)
	if thegroup == None:
		try:
			groups["top"]
		except:
			groups["top"] = [v]
		else:
			groups["top"].append(v)
print(f"{groups['top']}")
del(groups["top"])
print(f"{groups.keys()}")
print(f"{groups}")
			



		
def testfromgroup():
	print(f"{fromgroup('dur')}")
	print(f"{fromgroup('adc')}")
	print(f"{fromgroup('RdGainA')}")
