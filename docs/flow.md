# Usage Flows

**pyadi-jif** at its core is a modeling tool for configuration and can be used to determine configurations at the component and system levels.

-   _Component level_: Certain components can be isolated or used standalone like clock chip models. This is useful when compartmentalizing a problem or checking an existing configuration.
-   _System level_: When all or most of the top-level constraints need to be modeled together leveraging the system classes provides the most consistent connection between the constraints across the components that must work together.

## Component Level

When working at the component level each component's settings can be constrained or left unconstrained. Since each class's implementation will model possible settings as well as their limitations, any user-applied constraints are checked for validity. By default, all settings are left unconstrained. Constraints for divider settings and clocks can be scalars, lists, or even ranges. This applies to dividers and clock rates.

Below is an example of a configuration of a clock chip where the three desired output clocks and VCXO are supplied but the internal dividers need to be determined. The input divider **n2** is also constrained to 24 as well. Without applying this constraint, the solver could set **n2** to values between 12 and 255.

### AD9523-1 Component Example

```python
# Create instance of AD9523-1 clocking model
clk = adijif.ad9523_1()
# Constrain feedback divider n2 to only 24
clk.n2 = 24
# Define clock sources and output clocks
vcxo = 125000000
output_clocks = [1e9, 500e6, 7.8125e6]
clock_names = ["ADC", "FPGA", "SYSREF"]
clk.set_requested_clocks(vcxo, output_clocks, clock_names)
# Call solver and collect connfiguration
clk.solve()
o = clk.get_config()
pprint.pprint(o)
```

#### Output

```bash
{'m1': 3.0,
 'n2': 24,
 'out_dividers': [1.0, 2.0, 128.0],
 'output_clocks': {'ADC': {'divider': 1.0, 'rate': 1000000000.0},
                   'FPGA': {'divider': 2.0, 'rate': 500000000.0},
                   'SYSREF': {'divider': 128.0, 'rate': 7812500.0}},
 'r2': 1.0,
 'vcxo': 125000000.0}
```

After the solver runs successfully, all the internal dividers and clocks are provided in a single dictionary.

## System Level
