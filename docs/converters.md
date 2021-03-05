# Data converters

Four types of data converters are supported: ADCs, DACs, transceivers, and ADC/DAC combinations. However, fundamentally from a clocking perspective, it does not matter if a DAC or ADC is modeled, and integrated parts like transceivers simply have more constraints. It is also possible to limit multiple converters together and will only be limited by the PLLs available in the FPGA or divider degrees of freedom.

### Clocking architectures

sys.converter.use_direct_clocking = False
**pyadi-jif** supports both direct clocking and on-board PLL generation for different converters. Assuming the desired parts support those features. Usually an external clock generation source, like a PLL, is used to have better phase noise performance. However, routing faster clocks can be challenging above 10 GHz. If a part does support both options (like the [AD9081](https://www.analog.com/en/products/ad9081.html)) the internal solver will not look across both options. One mode must be selected before the solver is called. If both options are available the internal PLL will be used by default. This is set through the property __use_direct_clocking__.

```python
sys = adijif.system("ad9081_rx", "hmc7044", "xilinx", vcxo)
# Enable internal PLL
sys.converter.use_direct_clocking = False
```

### Configuring converters

Currently converter objects cannot be used outside of the system class when leveraging solvers. Standalone they could be used to evaluate basic JESD parameters and clocks, but you cannt solve for internal dividers standalone. Here is an example below of examining different effective rates based on the JESD config:

```python
cnv = adijif.ad9690()
cnv.sample_clock = 1e9
cnv.datapath_decimation = 1
cnv.L = 4
cnv.M = 2
cnv.N = 14
cnv.Np = 16
cnv.K = 32
cnv.F = 1

print(cnv.bit_clock, cnv.multiframe_clock, cnv.device_clock)
```

```bash
10000000000.0 31250000.0 250000000.0 
```

### Nested converters

For devices with both ADCs and DACs like transceivers or mixed-signal front-ends, nested models are used that model both ADC and DAC paths together. This is important since they can share a common device clock or reference clock but have different JESD link configurations. [AD9081](https://www.analog.com/en/products/ad9081.html)) is an example of a part that is has such an implementation. AD9081 also has RX or TX only models.

When using a nested converter model there are sub-properties **adc** and **dac** which handle the individual configurations. When the solver is called the cross configurations are validated first then possible clocking configurations are explored.