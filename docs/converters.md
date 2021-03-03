# Data Converters

Four types of data converters are supported: ADCs, DACs, transceivers, and ADC/DAC combinations. However, fundamentally from a clocking perspective, it does not matter if a DAC or ADC is modeled, and integrated parts like transceivers simply have more constraints. It is also possible to limit multiple converters together and will only be limited by the PLLs available in the FPGA or divider degrees of freedom.

### Clocking Architectures

**pyadi-jif** supports both direct clocking and on-board PLL generation for different converters. Assuming the desired parts support those features. Usually an external clock generation source, like a PLL, is used to have better phase noise performance. If a part does support both options (like the [AD9081](https://www.analog.com/en/products/ad9081.html)) the internal solver will not look across both options. One mode must be selected before the solver is called. If both options are available the internal PLL will be used by default.
