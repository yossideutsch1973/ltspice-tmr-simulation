# TMR Sensor Array Hardware Architecture

## 1. System Architecture Overview

The TMR Sensor Array hardware consists of the following major subsystems:

1. **TMR Sensor Array** - 16 TMR sensors arranged in a golden-angle pattern
2. **Analog Front-End** - Signal conditioning for each sensor channel
3. **Digital Signal Processing** - MCU or FPGA for angle calculation
4. **Power Management** - Regulated power for sensors and electronics
5. **Communication Interface** - External communication protocols
6. **Mechanical Assembly** - Sensor mounting and magnet holder

![System Block Diagram](./diagrams/system_block_diagram.png)

## 2. Optimal Configuration Selection

Based on our simulations, we have selected the following configuration:

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Sensor Count | 16 | Best balance of performance and fault tolerance |
| Pole Pairs | 17 | Optimal for resolution (17-18 bits) |
| Sensor Type | TMR | Higher sensitivity, lower power than Hall effect |
| Magnet Type | Diametrically magnetized NdFeB | Strong field, reliable pole pattern |
| Air Gap | 0.8 mm | Optimal signal strength while allowing mechanical clearance |

## 3. TMR Sensor Array Specification

### 3.1 Sensor Selection

**Recommended Sensor:** TDK/Micronas TMR2305

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Sensitivity | 45%/mT typical | High sensitivity for strong signals |
| Supply Voltage | 3.3V or 5V | Compatible with standard MCU/FPGA I/O |
| Package | SOT23-3 | Small footprint for dense placement |
| Operating Temperature | -40 to +125°C | Wide industrial range |
| Bandwidth | >1MHz | Suitable for high-speed applications |
| Noise Density | <1nV/√Hz | Low noise for high precision |

### 3.2 Sensor Arrangement

**Arrangement:** Golden angle spacing (137.5°) around a circle

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Ring Diameter | 15-20mm | Balance between size and precision |
| Sensor Spacing Tolerance | ±0.1° | Precision placement required |
| Radial Tolerance | ±0.1mm | Precision placement required |
| Z-axis Tolerance | ±0.1mm | Consistent air gap important |

## 4. Analog Front-End Design

### 4.1 Per-Channel Signal Conditioning

Each TMR sensor requires the following signal conditioning:

1. **Differential Input Amplifier**
   - Gain: 10-100 (adjustable)
   - CMRR: >80dB
   - Bandwidth: >100kHz
   - Recommended: AD8220 or INA121

2. **Anti-Aliasing Filter**
   - Type: 2nd-order Butterworth 
   - Cutoff: 20kHz (adjustable)
   - Components: Precision film resistors (0.1%) and NPO/C0G capacitors

3. **Level Shifting & Scaling**
   - Output Range: 0-3.3V (for ADC compatibility)
   - Offset Voltage: ±2mV max
   - Temperature Drift: <5ppm/°C

### 4.2 Multiplexing Strategy

Due to the high channel count (16 sensors), an analog multiplexing approach is recommended:

| Component | Specification | Notes |
|-----------|---------------|-------|
| Multiplexer | 16:4 ratio (4 ADC channels) | Enables 4 simultaneous samples |
| Sampling Rate | >40 kHz per channel | Sufficient for highest speed requirements |
| Switching Time | <1µs | Fast channel switching |
| Crosstalk | <-80dB | Isolation between channels |

## 5. Digital Processing Section

### 5.1 Processor Selection

**Primary Recommendation:** STM32F7 series MCU or Xilinx Artix-7 FPGA

| Parameter | MCU Specification | FPGA Specification | Notes |
|-----------|-------------------|-------------------|-------|
| Clock Speed | >180MHz | >100MHz | Sufficient for real-time processing |
| Memory | >256KB SRAM | >512KB Block RAM | Stores calibration tables |
| ADC | 12-16 bit, >1MSPS | External ADC required | Precision conversion |
| Interfaces | SPI, I2C, UART, CAN | SPI, I2C, UART, CAN | Multiple communication options |
| Package | LQFP100 or BGA | BGA or QFP | Balance of I/O and size |

### 5.2 ADC Requirements

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Resolution | 16-bit minimum | Required for 17-18 bit angle resolution |
| Sampling Rate | >500kSPS per channel | Supports high-speed operation |
| Input Range | 0-3.3V | Matches front-end output |
| SNR | >90dB | Preserves signal quality |
| INL/DNL | <±1LSB | High linearity required |

### 5.3 Angle Calculation Algorithm

The angle calculation will be implemented as follows:

1. **Data Acquisition**
   - Sample all 16 channels at synchronized intervals
   - Apply calibration corrections

2. **Harmonic Extraction**
   - Calculate fundamental sine/cosine components
   - Calculate 17th harmonic sine/cosine components

3. **Phase Calculation**
   - Calculate fundamental phase using atan2
   - Calculate 17th harmonic phase using atan2

4. **Phase Unwrapping**
   - Determine sector from fundamental phase
   - Calculate fine position from harmonic phase
   - Combine for absolute angle

5. **Error Correction**
   - Apply lookup table corrections
   - Filter results (optional)

## 6. Power Management

### 6.1 Power Requirements

| Component | Voltage | Current | Notes |
|-----------|---------|---------|-------|
| TMR Sensors (16) | 3.3V | ~5mA each, 80mA total | Low power sensors |
| Analog Front-End | ±5V | ~150mA | Op-amps, references |
| Digital Processing | 3.3V | ~250mA | MCU/FPGA core |
| Digital I/O | 3.3V | ~50mA | Communication interfaces |
| Total Power | ~1.8W peak | ~1.2W typical | Low power design |

### 6.2 Regulator Selection

| Rail | Specification | Recommended Part | Notes |
|------|---------------|------------------|-------|
| 5V Main | 5V ±2%, 500mA | TPS7A4501 | Low-noise LDO |
| 3.3V Analog | 3.3V ±1%, 200mA | TPS7A49 | Ultra-low noise for sensors |
| 3.3V Digital | 3.3V ±3%, 300mA | TPS62840 | High-efficiency buck |
| -5V | -5V ±5%, 100mA | LT3090 | Negative LDO for op-amps |

## 7. Communication Interfaces

### 7.1 Primary Interfaces

| Interface | Specification | Purpose |
|-----------|---------------|---------|
| SPI | 10MHz, 4-wire | High-speed angle data output |
| I²C | 400kHz | Configuration and diagnostics |
| UART | 115200 baud | Debug and development |
| CAN | 1Mbps | Industrial applications |

### 7.2 Protocol Implementation

The device will implement the following protocol stack:

1. **Raw Data Mode**
   - Direct access to angle data (SPI)
   - Low latency (<10µs)
   - Simple register structure

2. **Standard Protocol Mode**
   - Command-response structure
   - Extended diagnostics
   - Configuration and calibration access

3. **Industrial Protocol Support**
   - CANopen profile implementation
   - EtherCAT (optional)
   - Modbus RTU (optional)

## 8. Mechanical Design

### 8.1 PCB Form Factor

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Main PCB Diameter | 36mm | Accommodates sensor ring |
| PCB Thickness | 1.6mm | Standard, rigid construction |
| Layer Count | 6 layers | Separate analog/digital planes |
| Sensor PCB Type | Rigid-Flex | Allows precise sensor positioning |

### 8.2 Magnet Specifications

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Magnet Type | NdFeB (N52) | High field strength |
| Diameter | 12mm | Sized for field strength |
| Thickness | 3mm | Provides adequate field |
| Configuration | 17 pole pairs | Matching sensor array | 
| Mounting | Press-fit to shaft | Secure mounting |

### 8.3 Housing

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Material | Aluminum | Good EMI shielding |
| Sealing | IP67 | Dust and water resistant |
| Mounting | Flange or threaded | Multiple mounting options |
| Connector | M12 8-pin | Industrial standard |

## 9. Environmental Specifications

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Operating Temperature | -40°C to +85°C | Industrial range |
| Storage Temperature | -55°C to +125°C | Extended range |
| Humidity | 5% to 95% RH, non-condensing | Conformal coating optional |
| Vibration | 10g, 10-2000Hz | Suitable for automotive/industrial |
| Shock | 50g, 11ms half-sine | Rugged design |
| EMC | EN 61000-4-2,3,4,6 | Industrial immunity levels |
| ESD Protection | ±8kV contact, ±15kV air | Built-in ESD protection |

## 10. Production Engineering Requirements

### 10.1 Manufacturing Considerations

| Aspect | Requirement | Notes |
|--------|-------------|-------|
| PCB Fabrication | IPC Class 3 | High reliability |
| Component Placement | ±0.05mm accuracy | Precision placement for sensors |
| Soldering | Lead-free, nitrogen atmosphere | High-quality joints |
| Testing | 100% functional test | Every unit tested |
| Burn-in | 24hr at 85°C | Optional for high-reliability versions |

### 10.2 Calibration Procedure

Each TMR sensor array will require calibration:

1. **Sensor Offset Calibration**
   - Measure and store DC offset for each sensor
   - Temperature characterization (optional)

2. **Angular Calibration**
   - Mount on precision rotary stage
   - Measure errors at minimum 1024 points
   - Generate and store correction table

3. **Temperature Calibration** (optional)
   - Characterize performance across temperature range
   - Store temperature compensation coefficients

## 11. Bill of Materials (Key Components)

| Component | Description | Quantity | Estimated Cost |
|-----------|-------------|----------|----------------|
| TMR2305 | TMR Sensor | 16 | $48.00 |
| AD8220 | Precision Instrumentation Amplifier | 16 | $64.00 |
| OPA2387 | Precision Op-Amp | 8 | $16.00 |
| ADG1607 | 16-Channel Multiplexer | 1 | $12.00 |
| ADS8688 | 16-bit, 8-Channel ADC | 1 | $28.00 |
| STM32F767 | Microcontroller | 1 | $18.00 |
| TPS7A4501 | Low-Noise LDO Regulator | 3 | $9.00 |
| Custom Magnet | 17 pole-pair ring magnet | 1 | $15.00 |
| PCB | 6-layer with rigid-flex section | 1 | $25.00 |
| Aluminum Housing | Custom machined enclosure | 1 | $35.00 |
| **Total BOM Cost** | | | **~$270.00** |

## 12. Next Steps

1. **Schematic Design**
   - Create complete circuit schematic
   - Component selection and validation
   - Design review

2. **PCB Layout**
   - Floor planning and component placement
   - Routing with signal integrity focus
   - EMC considerations

3. **Firmware Development**
   - Algorithm implementation
   - Communication protocol stack
   - Performance optimization

4. **Prototype Manufacturing**
   - PCB fabrication
   - Assembly and testing
   - Validation against requirements

5. **Production Documentation**
   - Manufacturing files
   - Test procedures
   - Calibration instructions 