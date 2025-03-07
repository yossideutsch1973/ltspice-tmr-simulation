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
- `requirements.txt` - Required Python packages
- `schematic_improvements.md` - Summary of engineering enhancements
- `NEXT_SESSION_HANDOFF.md` - Instructions for continuing development
- `simple_test.py`, `opamp_test.py` - Test scripts for SchemaDraw functionality
- `tmr_stage1.py` - Simplified implementation of first stage for testing
- `schematics/` - Output directory for generated circuit diagrams 