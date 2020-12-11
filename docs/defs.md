# Definitions

To better understand the system as a whole common definitions must be used between converters, clock chips, and FPGAs used within the system. This page will outline the different clocks and standard configuration parameters for JESD204B and JESD204C.

### Link parameters

### Clocks

**sample clock**
: Data rate in samples per second after decimation stages for ADCs or before interpolation stages for DACs. This is usually referred to as device clock

**local multi-frame clock (LMFC)**
: ss

**system reference (sysref) clock**
: Clock used for synchronization in subclass 1 and subclass 2 configurations for deterministic latency. It is assumed to be aligned with sample clock from clock clock chip but with a periods at integer multiple of device clock

