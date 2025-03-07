# TMR Sensor Array Implementation Guide

## Technical Implementation Details

This guide provides detailed technical information about the 7th Harmonic TMR Sensor Array implementation. It is intended as a reference for continued development of the project.

### Mathematical Foundations

#### Golden Angle Distribution

The 8 TMR sensors are positioned at angles determined by the golden angle (~137.5°):

```
φᵢ = 2π(i/φ) mod 2π, for i = 0,1,2,...,7
```

where φ ≈ 1.618 is the golden ratio.

This creates the following sensor positions (in degrees):
- Sensor 0: 0°
- Sensor 1: 137.5°
- Sensor 2: 275.0°
- Sensor 3: 52.5°
- Sensor 4: 190.0°
- Sensor 5: 327.5°
- Sensor 6: 105.0°
- Sensor 7: 242.5°

#### Harmonic Decomposition

The key mathematical operation is extracting the fundamental (1×) and 7th harmonic components from the sensor signals. The extraction uses a weighted sum approach:

```
fund_sin = Σ[S_i × sin(φᵢ)]/N
fund_cos = Σ[S_i × cos(φᵢ)]/N
harm7_sin = Σ[S_i × sin(7×φᵢ)]/N
harm7_cos = Σ[S_i × cos(7×φᵢ)]/N
```

#### Phase Unwrapping

The phase unwrapping algorithm combines the fundamental and 7th harmonic phases:

```
fund_phase = atan2(fund_sin, fund_cos)
harm7_phase = atan2(harm7_sin, harm7_cos)
sector = floor(fund_phase/(360/7))
unwrapped = sector×(360/7) + unwrap(harm7_phase - 7×fund_phase)/7
```

where `unwrap()` normalizes the angle difference to [0, 360/7).

### LTspice Implementation Notes

#### B-Sources for Sensor Signals

The sensor signals are generated using behavioral sources (B-sources) in LTspice. Each sensor's output is modeled as:

```
BS0 S0 0 V=A1*sin(theta*pi/180 + phi0*pi/180) + A7*sin(P*theta*pi/180 + P*phi0*pi/180) + noise_level*A7*white(time*1e3)
```

where:
- `A1` is the fundamental amplitude (typically 0.2)
- `A7` is the 7th harmonic amplitude (typically 1.0)
- `P` is the number of pole pairs (7)
- `phi0` is the position of sensor 0
- `noise_level` controls the noise amplitude (typically 0.01 = 1%)

#### Harmonic Extraction Circuit

The harmonic extraction is implemented using weighted sums:

```
BS_fund_sin fund_sin 0 V=sum(i=0,7,V(S{i})*sin(phi{i}*pi/180))/8
BS_fund_cos fund_cos 0 V=sum(i=0,7,V(S{i})*cos(phi{i}*pi/180))/8
```

#### Angle Reconstruction

The phase extraction and unwrapping are implemented with:

```
BS_fund_phase fund_phase 0 V=mod(atan2(V(fund_sin),V(fund_cos))*180/pi+360,360)
BS_7th_phase harm7_phase 0 V=mod(atan2(V(harm7_sin),V(harm7_cos))*180/pi+360,360)
BS_sector sector 0 V=floor(V(fund_phase)/(360/P))
BS_unwrapped unwrapped 0 V=V(sector)*(360/P) + (mod(V(harm7_phase) - P*V(fund_phase) + 360, 360))/P
```

#### Error Calculation

The angular error is calculated as:

```
BS_error error 0 V=mod(theta - V(unwrapped) + 180, 360) - 180
```

This normalizes the error to the range [-180°, 180°].

### Test Parameter Reference

#### Resolution Test

- Parameter sweep: Increments angle by 0.002° steps
- Noise level: 0.1% to 10%
- Analysis metrics: RMS error, max error, 99th percentile error

#### Fault Tolerance Test

- Failure modes: Open circuit, short circuit, stuck value
- Failure counts: 1, 2, or 3 sensors
- Analysis metrics: Resolution reduction, tracking capability

#### Configuration Optimization Test

- N values: 4, 6, 8, 12, 16, 24, 32
- P values: 3, 5, 7, 11, 13, 17, 23, 29, 47, 97
- Key configurations:
  - N=8, P=7 (original design)
  - N=12, P=11 (optimal cost-performance)
  - N=16, P=17 (high-performance)
  - N=16, P=13 (better fault tolerance)

#### High-Speed Test

- RPM values: 1,000, 5,000, 10,000, 20,000, 30,000
- Processing delay: 100 µs
- Op-amp bandwidth: 100 kHz
- Update rate: 10 kHz

## Analysis Script Details

The `analyze-tmr-data.py` script provides comprehensive analysis of the LTspice simulation results. Here's a breakdown of its key functions:

### LTSpiceRawReader Class

Parses LTspice raw files to extract simulation data, handling:
- Variable definitions
- Time-domain data
- Step information

### TMRAnalyzer Class

Performs analysis on the extracted data:

1. **Basic Analysis**: Calculates RMS error, max error, 99th percentile error, and equivalent bit resolution
2. **Resolution Analysis**: Creates error histograms and validates the ±0.002°-0.003° precision claim
3. **Fault Tolerance Analysis**: Calculates performance degradation with failed sensors
4. **Speed Analysis**: Evaluates error vs. RPM relationship
5. **Configuration Analysis**: Compares different N,P combinations

### Visualization Functions

Generates multiple visualization plots:
- Error distribution histograms
- Angle tracking plots
- Error vs. time plots
- Speed performance comparisons
- Configuration optimization graphs

### Report Generation

Creates comprehensive reports validating the paper's claims:
- Text reports with key metrics
- JSON data for further analysis
- Statistical validation of each key claim

## Next Steps for Implementation

### Analog Front-End Design

1. **TMR Sensor Interface**:
   - Linear voltage regulator for sensor power
   - Differential amplifiers for sensor signals
   - Low-pass filtering to remove high-frequency noise

2. **Signal Conditioning**:
   - Gain and offset adjustment for each channel
   - Anti-aliasing filters before ADC
   - Simultaneous sample-and-hold circuits

### Digital Processing Design

1. **ADC Selection**:
   - 8+ channel simultaneous sampling
   - 16-bit resolution minimum
   - 10+ kHz sampling rate

2. **Processor Selection**:
   - FPGA for parallel processing (Xilinx Artix or Intel Cyclone)
   - or DSP/MCU with sufficient processing power
   - Hardware multiply-accumulate for efficient harmonic extraction

3. **Algorithm Implementation**:
   - Optimized CORDIC for atan2 function
   - Fixed-point arithmetic for phase unwrapping
   - Look-up tables for trigonometric functions

### PCB Design Considerations

1. **Layout Guidelines**:
   - Star-ground configuration for analog signals
   - Separate analog and digital ground planes
   - Short, direct traces for sensor signals
   - Ground planes under signal traces for controlled impedance

2. **Sensor Mounting**:
   - Precision mounting holes for exact sensor positioning
   - Golden-angle spacing verification during assembly
   - Fiducial markers for placement verification

### Mechanical Integration

1. **Magnet Selection**:
   - 7-pole-pair ring or disc magnet
   - NdFeB material for strong field
   - Diametric magnetization pattern

2. **Sensor Positioning**:
   - 0.8mm typical air gap
   - Precision alignment features
   - Rotational adjustment capability for calibration

### Calibration Procedures

1. **Sensor Offset Calibration**:
   - Measure and store DC offset for each sensor
   - Amplitude matching between channels

2. **Phase Calibration**:
   - Correction for sensor position errors
   - Look-up table for systematic error compensation

3. **Temperature Compensation**:
   - Temperature measurement circuit
   - Gain/offset adjustment vs. temperature

## Performance Verification Testing

### Static Accuracy Testing

1. **Reference Equipment**:
   - Precision rotary stage (better than 0.001° resolution)
   - Optical encoder reference (>20-bit)

2. **Test Procedure**:
   - Full 360° rotation in 0.1° increments
   - Fine 1° segment in 0.001° increments
   - Statistical error analysis

### Dynamic Testing

1. **High-Speed Setup**:
   - Precision motor with speed control
   - Synchronization with reference encoder
   - Data acquisition at 100+ kHz

2. **Performance Metrics**:
   - Error vs. RPM curves
   - Latency measurement
   - Step response characterization

### Environmental Testing

1. **Temperature Testing**:
   - -40°C to +125°C operating range
   - Error vs. temperature curves
   - Thermal cycling endurance

2. **Vibration and Shock**:
   - Performance under vibration
   - Mechanical shock resistance
   - Long-term reliability testing
