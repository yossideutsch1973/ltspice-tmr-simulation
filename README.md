# TMR Sensor Array - Schematic Implementation

This project implements circuit schematics for the TMR Sensor Array's analog front-end using Python and the SchemaDraw library. The implementation is a 1:1 recreation of the original ASCII diagrams used in the design documentation, with professional engineering improvements.

## Implemented Circuits

The implementation includes the following circuit diagrams:

1. **Instrumentation Amplifier** - Stage 1 of the analog front-end with TMR2305 sensor interface
2. **Active Low-Pass Filter** - Stage 2 with 20kHz cutoff frequency
3. **Level Shifter** - Stage 3 providing 0-3.3V output range
4. **16-Channel Multiplexer** - ADG1607 multiplexing circuit
5. **ADC Interface** - ADS8688 16-bit, 8-channel ADC connection

## Engineering Improvements

The schematic implementation has been enhanced based on professional engineering review to include:

- Proper decoupling capacitors for all active components
- Input protection with TVS diodes and series resistors
- Complete power connections and references
- Component tolerances for precision performance
- Proper pin connections for all ICs (no floating pins)
- Anti-aliasing filters and EMI protection
- Digital isolation for interface signals
- Test points for debugging and validation

For a complete list of improvements, see `schematic_improvements.md`.

## LTSpice Integration

A key feature of this project is the ability to export schematics to LTSpice format for simulation and analysis. The integration includes:

- Automated export of circuit diagrams to LTSpice netlist format
- Component model library for all ICs used in the circuits
- Simulation parameters for various analysis types (transient, AC, DC, Monte Carlo)
- Temperature sweep capability for thermal analysis

The exported files are stored in the `ltspice_models` directory and include:
- Individual circuit netlist files (*.net)
- Component model library (tmr_models.lib)

See the `USER_GUIDE.md` for detailed instructions on using the LTSpice integration features.

## Setup and Installation

1. Create a virtual environment:
   ```
   python -m venv schematic_venv
   source schematic_venv/bin/activate  # On Windows: schematic_venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the schematic drawer:
   ```
   python tmr_schematic_drawer.py
   ```

4. View the generated schematics in the `schematics` directory.

**Note:** There's currently an issue with running the script in some Python environments. If you encounter an error about missing 'encodings' module, please see `NEXT_SESSION_HANDOFF.md` for troubleshooting steps.

## Circuit Design Information

The schematic designs follow the TMR Sensor Array analog front-end specification with the following key components:

- **TMR2305** sensors for magnetic field detection
- **AD8220** instrumentation amplifiers for differential signal processing
- **OPA2387** precision op-amps for filtering and level shifting
- **ADG1607** 16-channel analog multiplexer
- **ADS8688** 16-bit, 8-channel ADC

The circuit is designed to provide high-precision signal conditioning for the TMR sensor array, enabling the system to achieve ±0.002°-0.003° angular resolution.

## File Structure

- `tmr_schematic_drawer.py` - Main Python script that generates the schematics
- `ltspice_integration.py` - Module for exporting schematics to LTSpice format
- `requirements.txt` - Required Python packages
- `schematic_improvements.md` - Summary of engineering enhancements
- `REFACTORING.md` - Documentation of code design improvements and refactoring
- `NEXT_SESSION_HANDOFF.md` - Instructions for continuing development
- `USER_GUIDE.md` - Comprehensive guide for using the schematic tool
- `simple_test.py`, `opamp_test.py` - Test scripts for SchemaDraw functionality
- `tmr_stage1.py` - Simplified implementation of first stage for testing
- `schematics/` - Output directory for generated circuit diagrams
- `ltspice_models/` - Output directory for LTSpice model files and netlists

## Environment Setup and Running Scripts

To avoid Python environment issues, use the provided `run_script.sh` shell script to run any Python scripts in this project:

```bash
# Make the script executable (if not already)
chmod +x run_script.sh

# Run a script
./run_script.sh <script_name.py>

# Examples:
./run_script.sh simple_test.py
./run_script.sh tmr_schematic_drawer.py
```

The shell script handles:
- Unsetting problematic environment variables (PYTHONHOME and PYTHONPATH)
- Using the system Python directly
- Installing required dependencies if needed

### Command-Line Options

The main script supports several command-line options:

```
Options:
  --unit-size UNIT_SIZE   Set the unit size for drawings (default: 2.5)
  --output-dir DIR        Set the output directory (default: schematics)
  --ltspice-dir DIR       Set the LTSpice model directory (default: ltspice_models)
  --format FORMAT [...]   Set the output format(s) (default: ['png'])
```

Example usage:
```bash
./run_script.sh tmr_schematic_drawer.py --unit-size 3.0 --format png svg
```

### Troubleshooting

If you encounter the error "ModuleNotFoundError: No module named 'encodings'", it's likely due to Python environment configuration issues. Use the provided `run_script.sh` to resolve this.

### Code Structure

The schematic drawer has been refactored to follow good software engineering practices:

- Functional programming principles for improved maintainability
- Common circuit elements extracted into reusable functions
- Improved error handling with detailed error messages
- Reduced code duplication throughout
- Better type hints and documentation

See `REFACTORING.md` for details on the code design improvements.

### SchemaDraw Version

This project uses SchemaDraw 0.19, which has some API differences from earlier versions. Key changes:
- Op-amp input anchors are named 'in1' and 'in2' (not 'in')
- Different positioning and scaling parameters 

For more details on API changes, see `schemdraw_api_changes.md`.

## Documentation

For detailed information, please refer to the following documents:

- `USER_GUIDE.md` - Comprehensive guide for using the schematic tool
- `schematic_improvements.md` - Details of engineering improvements made
- `REFACTORING.md` - Code design improvements and refactoring
- `NEXT_SESSION_HANDOFF.md` - Current status and next steps 