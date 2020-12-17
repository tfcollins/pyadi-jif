# Determine clocking for DAQ2

import adijif

vcxo = 125000000

sys = adijif.system("ad9680", "hmc7044", "xilinx", vcxo)

# Get Converter clocking requirements
sys.converter.sample_clock = 1e9
sys.converter.datapath_decimation = 1
sys.converter.L = 4
sys.converter.M = 2
sys.converter.N = 14
sys.converter.Np = 16
sys.converter.K = 32
sys.converter.F = 1

# Get FPGA clocking requirements
sys.fpga.setup_by_dev_kit_name("zc706")

sys.solve()

print("Clock config:")
for c in sys.clock.config:
    vs = sys.clock.config[c]
    for v in vs:
        if len(vs)>1:
            print(c,v[0])
        else:
            print(c,v)

print("FPGA config:")
for c in sys.fpga.config:
    vs = sys.fpga.config[c]
    for v in vs:
        if len(vs)>1:
            print(c,v[0])
        else:
            print(c,v)

print("Converter config:")
for c in sys.converter.config:
    vs = sys.converter.config[c]
    for v in vs:
        if len(vs)>1:
            print(c,v[0])
        else:
            print(c,v)
