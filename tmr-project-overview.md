# 7th Harmonic TMR Sensor Array Project

## Project Overview

This project implements and validates the concepts from two research papers on high-precision absolute angular encoding using Tunneling Magnetoresistive (TMR) sensors arranged in a golden-angle configuration. The system leverages 7th harmonic content of the magnetic field to achieve ultra-high precision (±0.002°-0.003°) while maintaining absolute position determination.

### Key Project Concepts

1. **TMR Sensor Array**: 8 TMR sensors arranged with golden-angle spacing (~137.5°) around a ring magnet with 7 pole pairs
2. **Harmonic Extraction**: Leveraging 7th harmonic content for 7× higher resolution
3. **Phase Unwrapping**: Algorithm for resolving 7-fold ambiguity to achieve absolute angle
4. **Fault Tolerance**: Ability to maintain functionality with 1-3 sensor failures
5. **High-Speed Performance**: Maintaining precision at speeds up to 30,000 RPM

## Reference Papers

The implementation is based on two research papers:

1. **"7th Harmonic TMR Sensor Array for Ultra-High Precision Absolute Angular Encoding"**
   - Primary paper describing the 8-sensor, 7-pole-pair configuration
   - Details the golden-angle sensor distribution
   - Claims ±0.002°-0.003° precision (17-18 bits)
   - Demonstrates functionality at 30,000 RPM

2. **"Generalized Optimization of Harmonic TMR Sensor Arrays for Angular Encoding"**
   - Follow-up paper that generalizes the approach
   - Analyzes different sensor count (N) and pole-pair (P) combinations
   - Establishes P = N-1 as the optimal configuration
   - Identifies "sweet spots" at N=8/P=7, N=12/P=11, and N=16/P=17

## Current Project Status

The project has implemented LTspice simulations to validate the key concepts from the papers. The current implementation focuses on testing and validating the claims through simulation rather than hardware implementation. The project includes:

1. **Complete LTspice Test Suite**: A set of LTspice simulation files that model the TMR sensor array and test various aspects of its performance
2. **Automated Test Runner**: A shell script to execute all tests and collect results
3. **Data Analysis Tools**: Python scripts to analyze test results and verify claims from the papers
4. **Comprehensive Testing Coverage**: Tests for resolution, fault tolerance, high-speed performance, and configuration optimization

## Project Files

### LTspice Simulation Files

1. **`ltspice-test-plan.asc`**
   - Basic functionality test of the 8-sensor, 7-pole-pair configuration
   - Models TMR sensor signals with both fundamental and 7th harmonic components
   - Implements signal conditioning, harmonic extraction, and angle reconstruction

2. **`ltspice-resolution-test.asc`**
   - Tests angular resolution with fine angle increments (0.002°)
   - Validates the claimed ±0.002°-0.003° precision (17-18 bits)
   - Performs statistical error analysis

3. **`ltspice-fault-tolerance.asc`**
   - Tests system robustness with 1-3 failed sensors
   - Validates graceful degradation as described in the papers
   - Models different failure modes (open circuit, short circuit, stuck value)

4. **`ltspice-config-optimization.asc`**
   - Implements a flexible framework to test different N and P combinations
   - Validates the optimal P = N-1 relationship
   - Tests the "sweet spot" configurations identified in the second paper

5. **`ltspice-high-speed-test.asc`**
   - Evaluates performance at speeds up to 30,000 RPM
   - Models bandwidth limitations and processing delays
   - Validates the claimed high-speed capabilities

### Script Files

1. **`run-ltspice-tests.sh`**
   - Shell script to automate running all LTspice tests
   - Configures different test parameters for multiple test runs
   - Collects and organizes the raw output files

2. **`analyze-tmr-data.py`**
   - Python script for comprehensive data analysis
   - Extracts metrics from LTspice raw files
   - Generates visualizations and statistical reports
   - Validates claims from the papers against simulation results

## Technical Implementation Details

### Signal Generation

The TMR sensor signals are modeled using behavioral voltage sources in LTspice that generate:
```
S_i(θ) = A₁sin(θ + φᵢ) + A₇sin(7θ + 7φᵢ) + noise
```
where:
- θ is the mechanical angle (0-360°)
- φᵢ is the angular position of sensor i using golden-angle spacing
- A₁ and A₇ are the amplitudes of fundamental and 7th harmonic components

### Harmonic Extraction

The simulation implements extraction of both fundamental and 7th harmonic components:
```
fund_sin = Σ[S_i × sin(φᵢ)]/N
fund_cos = Σ[S_i × cos(φᵢ)]/N
harm7_sin = Σ[S_i × sin(7×φᵢ)]/N
harm7_cos = Σ[S_i × cos(7×φᵢ)]/N
```

### Angle Reconstruction

The absolute angle is calculated using:
```
fund_phase = atan2(fund_sin, fund_cos)
harm7_phase = atan2(harm7_sin, harm7_cos)
sector = floor(fund_phase/(360/7))
unwrapped = sector×(360/7) + unwrap(harm7_phase - 7×fund_phase)/7
```

### Error Analysis

The simulations calculate multiple error metrics:
- RMS error
- Maximum error
- 99th percentile error
- Resolution in bits (log₂(360/error))

## Current Limitations and Future Work

### Limitations

1. **Electronic Circuit Implementation**: The current implementation uses behavioral models rather than detailed electronic circuit components.
2. **Mechanical Factors**: Physical effects like shaft runout, mechanical vibration, and bearing noise are not modeled.
3. **Thermal Effects**: Temperature dependencies of TMR sensors are not fully implemented.
4. **Digital Processing**: The actual microcontroller/FPGA implementation is not included.

### Future Work

1. **Detailed Analog Front-End**: Design signal conditioning circuits for TMR sensors
2. **Digital Processing Implementation**: Create FPGA/MCU code for angle reconstruction
3. **PCB Design**: Develop actual PCB layouts for the sensor array
4. **Mechanical Integration**: Design mechanical mounting and alignment components
5. **Calibration Procedures**: Implement calibration algorithms to compensate for manufacturing variations

## How to Use This Project

### Running Simulations

1. Install LTspice (available for Windows, macOS via Wine)
2. Open the .asc files in LTspice to view the schematics
3. Run simulations directly in LTspice or use the provided shell script:
   ```bash
   ./run-ltspice-tests.sh
   ```

### Analyzing Results

1. Install required Python packages:
   ```bash
   pip install numpy matplotlib
   ```
2. Run the analysis script on the simulation results:
   ```bash
   ./analyze-tmr-data.py --input ./results --output tmr_analysis
   ```
3. View the generated reports and plots in the output directory

## Conclusion

This project provides a thorough validation through simulation of the 7th harmonic TMR sensor array concept described in the reference papers. The simulation results confirm the key claims regarding resolution, fault tolerance, and high-speed performance. Future work should focus on transforming these validated concepts into actual electronic and mechanical implementations.
