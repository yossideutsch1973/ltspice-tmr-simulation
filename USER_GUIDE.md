# TMR Sensor Array Schematic Tool - User Guide

## Introduction

The TMR Sensor Array Schematic Tool is a Python-based utility for generating professional-grade circuit diagrams of the TMR (Tunneling Magnetoresistive) Sensor Array analog front-end. The tool uses the SchemaDraw library to create clear, high-quality schematics that follow engineering best practices.

This guide provides comprehensive information on using the tool, understanding its outputs, and extending its functionality.

## Features

- **Professional-Grade Schematics**: Creates detailed engineering schematics with proper component values, tolerances, and connections
- **Multiple Circuit Stages**: Generates diagrams for all stages of the TMR sensor analog front-end
- **Engineering Improvements**: Includes decoupling capacitors, proper power connections, protection circuits, and more
- **LTSpice Integration**: Exports circuit diagrams to LTSpice format for simulation and analysis
- **Flexible Output**: Supports multiple output formats (PNG, SVG, PDF)
- **Detailed Technical Notes**: Includes design notes and technical information on schematics

## Installation and Setup

### System Requirements

- Python 3.8 or higher
- pip package manager
- [Optional] LTSpice XVII for simulation

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ltspice-tmr-simulation.git
   cd ltspice-tmr-simulation
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv schematic_venv
   source schematic_venv/bin/activate  # On Windows: schematic_venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Tool

The tool can be run either directly or using the provided shell script:

#### Using the shell script (Recommended)

```bash
# Make script executable (if needed)
chmod +x run_script.sh

# Run the main schematic generator
./run_script.sh tmr_schematic_drawer.py
```

#### Direct execution

```bash
python tmr_schematic_drawer.py
```

### Command-Line Options

The tool supports several command-line options:

```
Options:
  --unit-size UNIT_SIZE   Set the unit size for drawings (default: 2.5)
  --output-dir DIR        Set the output directory (default: schematics)
  --ltspice-dir DIR       Set the LTSpice model directory (default: ltspice_models)
  --format FORMAT [...]   Set the output format(s) (default: ['png'])
```

Example usage:
```bash
./run_script.sh tmr_schematic_drawer.py --unit-size 3.0 --format png svg --output-dir custom_schematics
```

## Generated Schematics

The tool generates the following circuit diagrams:

1. **Instrumentation Amplifier (Stage 1)**
   - TMR2305 sensor interfacing
   - AD8220 instrumentation amplifier
   - Input protection
   - Power decoupling
   - Gain setting circuitry

2. **Active Low-Pass Filter (Stage 2)**
   - 20kHz cutoff frequency
   - OPA2387 precision op-amp
   - Anti-aliasing function
   - Power connections and decoupling

3. **Level Shifter (Stage 3)**
   - 0-3.3V output range
   - Precision voltage reference
   - EMI filtering
   - Output protection

4. **16-Channel Multiplexer**
   - ADG1607 multiplexer
   - Channel selection
   - Digital isolation
   - Input protection
   - Power supply decoupling

5. **ADC Interface**
   - ADS8688 16-bit, 8-channel ADC
   - Anti-aliasing filters
   - Reference circuit
   - SPI interface
   - Clock source
   - Power filtering

## LTSpice Integration

The tool can export the circuit diagrams to LTSpice format for simulation and analysis. This feature allows you to validate the circuit designs before implementation.

### Generated LTSpice Files

The following files are generated in the LTSpice models directory:

1. **Netlist Files (*.net)**
   - Contains the netlist representation of each circuit
   - Can be imported into LTSpice

2. **Model Library (tmr_models.lib)**
   - Contains component models for all ICs used in the circuits
   - Includes AD8220, OPA2387, TMR2305, ADG1607, and ADS8688 models

### Using LTSpice Models

To use the generated LTSpice models:

1. Open LTSpice XVII
2. Select File > Open and navigate to the `ltspice_models` directory
3. Open the desired circuit netlist
4. Simulate the circuit using LTSpice's simulation features

## Extending the Tool

The schematic drawer is designed to be extensible and configurable. Here are some ways to extend its functionality:

### Adding New Circuit Stages

To add a new circuit stage:

1. Create a new drawing function in `tmr_schematic_drawer.py`
2. Follow the pattern of existing functions, using the `@with_error_handling` decorator
3. Add the new function to the `circuits` list in the `main()` function

### Modifying Component Values

Component values can be modified by changing the values in the respective drawing functions. Future versions will support configuration files for easier modification.

### Adding New LTSpice Models

To add new LTSpice component models:

1. Add the model specifications to the `model_specs` dictionary in the `main()` function
2. Follow the pattern of existing models, specifying the type, ports, and definition

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'encodings'"**
   - Use the provided `run_script.sh` script, which properly configures the Python environment
   - The script unsets problematic environment variables that might cause this error

2. **"ModuleNotFoundError: No module named 'schemdraw'"**
   - Make sure to install the required dependencies using `pip install -r requirements.txt`
   - Check that your virtual environment is activated

3. **SchemaDraw API Changes**
   - This tool is designed for SchemaDraw 0.19. If you have a different version, you might encounter issues
   - Check `schemdraw_api_changes.md` for information on API differences

### Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the project documentation, including `README.md` and `NEXT_SESSION_HANDOFF.md`
2. Examine the code comments for additional information
3. Create an issue on the GitHub repository with detailed information about the problem

## Future Enhancements

Planned future enhancements include:

1. **Configuration Management**
   - Move circuit values to configuration files for easier modification
   - Implement a more flexible parameter system

2. **Additional Engineering Improvements**
   - Temperature compensation circuits
   - Self-test capabilities
   - Advanced filtering techniques
   - Differential signaling for critical paths
   - Power sequencing circuits

3. **Enhanced LTSpice Integration**
   - More detailed component models
   - Pre-configured simulation setups for different analysis types
   - Direct ASC file generation for schematic viewing in LTSpice

4. **Improved Documentation**
   - More detailed technical notes on schematics
   - Component selection guides
   - Design considerations documentation

## References

- [SchemaDraw Documentation](https://schemdraw.readthedocs.io/)
- [LTSpice XVII Documentation](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)
- Circuit design references listed in `schematic_improvements.md`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 