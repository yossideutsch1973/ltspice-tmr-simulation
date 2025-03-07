# TMR Sensor Array Project File Index

This document provides a comprehensive index of all files included in the 7th Harmonic TMR Sensor Array project, with descriptions of each file's purpose and content.

## Documentation Files

1. **`tmr-project-overview.md`**
   - High-level overview of the entire project
   - Explanation of key concepts from the research papers
   - Summary of project status and implementation approach
   - General information about included files and components

2. **`tmr-implementation-guide.md`**
   - Detailed technical implementation information
   - Mathematical foundations of the TMR sensor array
   - Implementation details for LTspice simulations
   - Guide for future hardware implementation
   - Testing methodologies and parameters

3. **`tmr-project-handoff.md`**
   - Complete project context for handoff
   - Current status of all components
   - Next steps and recommended approach
   - Technical challenges and considerations
   - Resource requirements for continuation

4. **`file-index.md`**
   - This file - comprehensive index of all project files
   - Descriptions of file contents and relationships
   - Organization structure of the project

## LTspice Simulation Files

5. **`ltspice-test-plan.asc`**
   - Basic functionality test of TMR sensor array
   - Implementation of 8 sensors with golden-angle spacing
   - 7th harmonic signal generation and extraction
   - Angle reconstruction algorithm
   - Reference implementation for other tests

6. **`ltspice-resolution-test.asc`**
   - Detailed test for angular resolution
   - Parameter sweep with 0.002° increments
   - Statistical error analysis
   - Validation of ±0.002°-0.003° precision claim
   - Configurable noise levels

7. **`ltspice-fault-tolerance.asc`**
   - Tests for system robustness to sensor failures
   - Simulation of 1-3 failed sensors
   - Different failure modes (open, short, stuck)
   - Graceful degradation measurement
   - Absolute position retention verification

8. **`ltspice-config-optimization.asc`**
   - Tests for different sensor count (N) and pole-pair (P) combinations
   - Validation of P = N-1 optimality
   - Comparison of "sweet spot" configurations
   - Cost-performance analysis
   - Resolution vs. complexity tradeoffs

9. **`ltspice-high-speed-test.asc`**
   - Performance evaluation at extreme rotation speeds
   - Tests up to 30,000 RPM (500 Hz)
   - Bandwidth and processing delay effects
   - Latency and tracking performance
   - Error vs. speed characterization

## Script Files

10. **`run-ltspice-tests.sh`**
    - Shell script to automate LTspice simulations
    - Batch execution of all test configurations
    - Parameter modifications between runs
    - Results collection and organization
    - Summary report generation

11. **`analyze-tmr-data.py`**
    - Python script for comprehensive data analysis
    - LTspice raw file parsing
    - Statistical analysis of error distributions
    - Visualization generation (plots and charts)
    - Validation of paper claims against results
    - Report generation with metrics

## Reference Papers

12. **`journal-article-html-improved.html`**
    - First research paper: "7th Harmonic TMR Sensor Array for Ultra-High Precision Absolute Angular Encoding"
    - Original implementation of 8-sensor, 7-pole-pair configuration
    - Mathematical theory and golden-angle distribution
    - Performance claims and experimental results
    - System architecture and signal processing description

13. **`optimization-paper-with-figures.html`**
    - Second research paper: "Generalized Optimization of Harmonic TMR Sensor Arrays for Angular Encoding"
    - Generalization of the approach to different N,P combinations
    - Information theory analysis of optimal configurations
    - Monte Carlo simulation results for different combinations
    - Cost-efficiency and fault tolerance analysis

## File Relationships

The LTspice files build on each other in complexity:

- `ltspice-test-plan.asc` serves as the foundation
- Other test files extend this with specific test configurations
- `run-ltspice-tests.sh` orchestrates execution of all files
- `analyze-tmr-data.py` processes the results from all tests

The documentation files have the following relationships:

- `tmr-project-overview.md` is the starting point for understanding the project
- `tmr-implementation-guide.md` provides technical depth for implementation
- `tmr-project-handoff.md` synthesizes everything for project continuation
- `file-index.md` (this file) serves as a navigation guide

## File Usage Instructions

### To Run Tests

1. Save all LTspice (.asc) files to a working directory
2. Make the shell script executable: `chmod +x run-ltspice-tests.sh`
3. Run the tests: `./run-ltspice-tests.sh`
4. Results will be saved in the `./results` directory

### To Analyze Results

1. Make the Python script executable: `chmod +x analyze-tmr-data.py`
2. Run the analysis: `./analyze-tmr-data.py --input ./results --output tmr_analysis`
3. Review reports in `tmr_analysis/reports/`
4. Examine plots in `tmr_analysis/plots/`

### To Modify Tests

1. Open the desired `.asc` file in LTspice
2. Modify parameters at the top of the file:
   - `.param` statements control fundamental settings
   - Test configurations can be changed by uncommenting alternative sections
3. Re-run specific tests or the entire suite

## Notes on LTspice Files

- All `.asc` files require LTspice XVII or later
- Behavioral sources (B-sources) are used extensively
- Some test configurations are selected by commenting/uncommenting sections
- Parameters at the top of each file control test behavior
- Simulation settings (.tran, .step) are at the bottom of each file

## Additional Notes

- The `.raw` files from LTspice simulations can be large and are not included
- The analysis script generates derivative data that is not included
- Documentation files should be viewed with a markdown-compatible viewer
- Reference papers are included in HTML format with embedded figures
