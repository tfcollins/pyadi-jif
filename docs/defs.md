# Definitions

To better understand the system as a whole common definitions must be used between converters, clock chips, and FPGAs used within the system. This page will outline the different clocks and standard configuration parameters for JESD204B and JESD204C.

### JESD204 Link parameters

**F**
: Octets per frame per link

**K**
: Frames per multiframe

**L**
: Number of lanes

**M**
: Number of virtual converters

**N**
: Number of non-dummy bits per sample. Usually converter resolution.

**Np**
: Number of bits per sample

**S**
: Samples per converter per frame

### Clocks

**frame_clock**
: Frames per second $$ \text{frame clock} = \frac{\text{sample clock}}{S} $$

**sample clock**
: Data rate in samples per second after decimation stages for ADCs or before interpolation stages for DACs. This is usually referred to as device clock

**local multi-frame clock (LMFC)**
: ss

**system reference (sysref) clock**
: Clock used for synchronization in subclass 1 and subclass 2 configurations for deterministic latency. It is assumed to be aligned with the sample clock from the clock chip but with periods at integer multiples of the device clock.

