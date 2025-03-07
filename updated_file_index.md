# TMR Sensor Array Project File Index (Updated)

This document provides a comprehensive index of all files included in the 7th Harmonic TMR Sensor Array project, with descriptions of each file's purpose and content.

## Documentation Files

1. **`README.md`**
   - Main project README
   - Project overview and key features
   - Repository contents and organization
   - Getting started guide for both simulation and hardware

2. **`tmr-project-overview.md`**
   - High-level overview of the entire project
   - Explanation of key concepts from the research papers
   - Summary of project status and implementation approach
   - General information about included files and components

3. **`tmr-implementation-guide.md`**
   - Detailed technical implementation information
   - Mathematical foundations of the TMR sensor array
   - Implementation details for LTspice simulations
   - Guide for hardware implementation
   - Testing methodologies and parameters

4. **`updated_tmr_project_handoff.md`**
   - Complete project context for handoff
   - Current status including completed simulation and hardware design
   - Detailed hardware design decisions
   - Next steps and recommended approach
   - Resource requirements for continuation

5. **`file-index.md`** / **`updated_file_index.md`**
   - Comprehensive index of all project files
   - Descriptions of file contents and relationships
   - Organization structure of the project

6. **`tmr_hardware_architecture.md`**
   - Complete hardware architecture specification
   - Component selection and justification
   - Detailed subsystem design requirements
   - Environmental and production specifications
   - Bill of materials for key components

## LTspice Simulation Files

7. **`ltspice-resolution-test.asc`**
   - Basic functionality test of TMR sensor array
   - Implementation of 8 sensors with golden-angle spacing
   - 7th harmonic signal generation and extraction
   - Angle reconstruction algorithm
   - Reference implementation for other tests

8. **`ltspice-fault-tolerance.asc`**
   - Tests for system robustness to sensor failures
   - Simulation of 1-3 failed sensors
   - Different failure modes (open, short, stuck)
   - Graceful degradation measurement
   - Absolute position retention verification

9. **`ltspice-config-optimization.asc`**
   - Tests for different sensor count (N) and pole-pair (P) combinations
   - Validation of P = N-1 optimality
   - Comparison of "sweet spot" configurations
   - Cost-performance analysis
   - Resolution vs. complexity tradeoffs

10. **`ltspice-high-speed-test.asc`**
    - Performance evaluation at extreme rotation speeds
    - Tests up to 30,000 RPM (500 Hz)
    - Bandwidth and processing delay effects
    - Latency and tracking performance
    - Error vs. speed characterization

## Python Simulation Files

11. **`ltspice_to_python.py`**
    - Python implementation of the TMR sensor model
    - Accurate recreation of the LTspice simulation behavior
    - Supports different sensor/pole-pair configurations
    - Includes Monte Carlo capability

12. **`refine_tmr_model.py`**
    - Enhanced TMR sensor model
    - Includes realistic hardware behavior
    - Models analog front-end, ADC, and other circuit effects
    - Temperature, supply voltage, and noise effects

13. **`monte_carlo_tmr.py`**
    - Monte Carlo simulation for TMR sensor array
    - Parameter variation analysis
    - Statistical error analysis
    - Resolution calculation

14. **`analyze_monte_carlo.py`**
    - Analyzer for Monte Carlo simulation results
    - Statistical analysis and visualization
    - Validation against paper claims
    - Summary reports generation

15. **`run_comprehensive_monte_carlo.py`**
    - Comprehensive Monte Carlo testing framework
    - Tests multiple configurations
    - Evaluates fault tolerance
    - Generates comparative analysis

## Script Files

16. **`run-ltspice-tests.sh`**
    - Shell script to automate LTspice simulations
    - Batch execution of all test configurations
    - Parameter modifications between runs
    - Results collection and organization
    - Summary report generation

17. **`analyze-tmr-data.py`**
    - Python script for comprehensive data analysis
    - LTspice raw file parsing
    - Statistical analysis of error distributions
    - Visualization generation (plots and charts)
    - Validation of paper claims against results
    - Report generation with metrics

## Hardware Design Files

18. **`tmr_analog_frontend.txt`**
    - Detailed circuit design for analog front-end
    - TMR sensor interface circuit
    - Signal conditioning stages
    - Multiplexing and ADC interface
    - Component list and design notes

## File Relationships

The files in this project are organized as follows:

1. **Documentation Files**
   - Provide context, overview, and specifications
   - `README.md` is the entry point
   - `tmr_hardware_architecture.md` guides hardware implementation

2. **Simulation Files**
   - LTspice `.asc` files for circuit simulation
   - Python simulations provide more flexibility
   - Monte Carlo scripts for statistical analysis

3. **Hardware Design Files**
   - Circuit designs and specifications
   - Component selection and BOM

## Using this Project

### To Run Simulations

1. Install required dependencies:
   ```bash
   pip install numpy matplotlib PyLTSpice
   ```

2. Run Python-based simulations:
   ```bash
   python run_comprehensive_monte_carlo.py
   ```

3. Analyze results:
   ```bash
   python analyze_monte_carlo.py
   ```

### For Hardware Development

1. Review the hardware architecture:
   - `tmr_hardware_architecture.md`

2. Examine the circuit designs:
   - `tmr_analog_frontend.txt`

3. Follow the next steps outlined in:
   - `updated_tmr_project_handoff.md` 