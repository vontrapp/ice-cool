import argparse
from operator import attrgetter

## constants

# liters per gallon
lpg = 3.7854118
# kg/lb
kpl = 0.45359237
# specific heat of water
Cpw = 4186 # J/kg/C
# specific heat of ice
Cpi = 2108 # J/kg/C
# specific latent heat of ice
Li = 334000 # J/kg

argp = argparse.ArgumentParser()
argp.add_argument("target", help="Target temperature")
argp.add_argument("start", nargs="?", default=100, help="Starting temp (default 100C)")
argp.add_argument("-w", "--wort", default=20, help="Volume of wort (default 20L)")
argp.add_argument("-i", "--ice", default=-10, help="Ice temparature (default -10C)")
argp.add_argument("-t", "--tap", default=18, help="Temperature of tap water (default 18C)")
argp.add_argument("-d", "--differential", default=5, help="Temperature differential desired at target (default 5C)")

argp.add_argument("-r", "--ratio", default=75, help="Ratio of ice/water, in percent (default 75%%)")
argp.add_argument("-v", "--volume", help="Volume of ice bath. If -v given, solve for ratio, otherwise solve for volume given ratio.")

args = argp.parse_args()

# convert arguments
temps = {}
for tk in ("target","ice","start","ice","tap","differential"):
    t = attrgetter(tk)(args)
    if isinstance(t, str) and t.upper().endswith("F"):
        t = (float(t[:-1])-32) * 5.0/9
    if isinstance(t, str) and t.upper().endswith("C"):
        t = float(t[:-1])
    t = float(t)
    temps[tk] = t
volumes = {}
for vk in ("wort","volume"):

    v = attrgetter(vk)(args)
    if not v: continue
    if isinstance(v, str) and v.endswith("L"):
        v = float(v[:-1])
    if isinstance(v, str) and v.endswith("g"):
        v = float(v[:-1])*lpg
    v = float(v)
    volumes[vk] = v

# joules = w*Cpw*(start-target)
coolj = volumes["wort"]*Cpw*(temps["start"] - temps["target"])
print "Need %0.2F Joules to cool wort" % coolj

# joules = v*r*Cpi*(0-i) + v*r*li + v*r*Cpw*(target-tdiff) + v*(1-r)*Cpw*(target-tdiff-tap)
#        = r*(v*Cpi*(0-i) + v*Li + v*Cpw*(target-tdiff)) + (1-r)*v*Cpw*(target-tdiff-tap)
#        = r*(v*Cpi*(0-i) + v*Li + v*Cpw*(target-tdiff)) + v*Cpw*(target-tdiff-tap) - r*v*Cpw*(target-tdiff-tap)
#        = r*(v*Cpi*(0-i) + v*Li + v*Cpw*(target-tdiff) - v*Cpw*(target-tdiff-tap)) + v*Cpw*(target-tdiff-tap)
#        = r*(v*(Cpi*(0-i) + Li + Cpw*((target-tdiff) - (target-tdiff-tap)))) + v*Cpw*(target-tdiff-tap)
#        = r*(v*(Cpi*(0-i) + Li - Cpw*tap)) + v*Cpw*(target-tdiff-tap)
# r = (joules - v*Cpw*(target-tdiff-tap))/(v*(Cpi*(0-i) + Li - Cpw*tap))

# joules = v*r*Cpi*(0-i) + v*r*Li + v*r*Cpw*(target-tdiff) + v*(1-r)*Cpw*(target-tdiff-tap)
#        = r*v*Cpi*(0-i) + r*v*Li + r*v*Cpw*(target-tdiff) + (1-r)*v*Cpw*(target-tdiff-tap)
#        = r*v*Cpi*(0-i) + r*v*Li + r*v*Cpw*(target-tdiff) + v*Cpw*(target-tdiff-tap) - r*v*Cpw*(target-tdiff-tap)
#        = r*v*Cpi*(0-i) + r*v*Li + r*v*Cpw*(target-tdiff) - r*v*Cpw*(target-tdiff-tap) + v*Cpw*(target-tdiff-tap)
# r = (joules - v*Cpw*(target-tdiff-tap))/(v*Cpi*(0-i) + v*Li + v*Cpw*(target-tdiff) - v*Cpw*(target-tdiff-tap))
if "volume" in volumes:
    # solve for ratio
    v = volumes["volume"]
    tdiff = temps["differential"]
    targ = temps["target"]
    tap = temps["tap"]
    i = temps["ice"]

    #r = (coolj - v*Cpw*(targ-tdiff-tap))/v*(Cpi*(0-i) + Li - Cpw*tap)
    r = (coolj - v*Cpw*(targ-tdiff-tap))/(v*Cpi*(0-i) + v*Li + v*Cpw*(targ-tdiff) - v*Cpw*(targ-tdiff-tap))

    print "Ice/water ratio: %0.2f" % (r*100,)
    print "%0.2fLb or %0.2fkg of ice" % (v*r/kpl, v*r)

# joules = v*r*Cpi*(0-i) + v*r*Li + v*r*Cpw*(target-tdiff) + v*(1-r)*Cpw*(target-tdiff-tap)
#        = v*(r*(Cpi*(0-i)) + r*Li + Cpw*(r*(target-tdiff) + (1-r)*(target-tdiff-tap))
#        = v*(r*(Cpi*(0-i)) + Li + (target-tdiff)*Cpw*(r - (1-r)*tap))
# v = joules/(r*(Cpi*(0-i)) + Li + (target-tdiff)*Cpw*(r - (1-r)*tap))
else:
    target = temps["target"]
    tdiff = temps["differential"]
    tap = temps["tap"]
    i = temps["ice"]

    r = float(args.ratio)/100
    v = coolj/((r*(Cpi*(0-i)) + Li + (target-tdiff)*Cpw) + (1-r)*Cpw*(target-tdiff-tap))
    print "%0.2fL of %0.2f%% ice water" % (v, r*100)
    print "%0.2fLb or %0.2fkg of ice" % (v*r/kpl, v*r)
