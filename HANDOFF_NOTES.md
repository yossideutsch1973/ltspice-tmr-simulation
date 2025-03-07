# TMR Sensor Array Project - Handoff Notes

## Project Status

This project implements a high-precision absolute angular encoding system using Tunneling Magnetoresistive (TMR) sensors arranged in a golden-angle configuration. 

The project has been set up with:

1. **Complete Documentation**
   - `README.md` - Main project overview
   - `tmr_hardware_architecture.md` - Detailed hardware specifications
   - `updated_tmr_project_handoff.md` - Project handoff document
   - `updated_file_index.md` - File index

2. **Simulation Code**
   - Python-based TMR sensor model
   - Monte Carlo simulation capabilities
   - Comprehensive analysis scripts

3. **Hardware Design**
   - Detailed analog front-end circuit design
   - Component selection
   - BOM with estimated costs

## Latest Updates (Current Session)

### Environment and API Fixes

We've successfully resolved the Python environment issues and SchemaDraw API compatibility problems:

1. **Environment Solution**:
   - Created `run_script.sh` that properly configures the Python environment before running scripts
   - Unsets problematic environment variables (PYTHONHOME and PYTHONPATH)
   - Uses system Python directly (/usr/bin/python3.10)
   - Automatically installs required dependencies if needed

2. **SchemaDraw API Compatibility**:
   - Fixed anchor naming issues (changed 'in' to 'in1' for Opamp elements)
   - Fixed function parameter issues in nested functions
   - Created `check_opamp_anchors.py` to document available anchors in SchemaDraw 0.19
   - Created `schemdraw_api_changes.md` to document API differences

3. **Documentation Updates**:
   - Updated README.md with environment setup instructions
   - Added troubleshooting information
   - Created detailed API change documentation

### Current Status

All schematics are now generating correctly with SchemaDraw 0.19. The following files have been generated:
- stage1_instrumentation_amplifier.png
- stage2_active_lowpass_filter.png
- stage3_level_shifter.png
- multiplexer_circuit.png
- adc_interface.png

### Next Steps

1. **Schematic Review**:
   - Review generated schematics for correctness and completeness
   - Verify all engineering improvements are properly implemented
   - Check component values and connections

2. **Code Refactoring**:
   - Apply functional programming principles to improve code maintainability
   - Reduce code duplication in similar circuit sections
   - Improve error handling

3. **Additional Improvements**:
   - Implement any remaining items from `schematic_improvements.md`
   - Add more detailed technical notes to schematics
   - Consider adding simulation parameters for LTSpice export

## Repository Structure

This is a Git repository with all the necessary files. Use the following documentation to get started:

1. Start with `README.md` for an overview
2. Review `tmr_hardware_architecture.md` for hardware specifications
3. Check `tmr_analog_frontend.txt` for circuit designs

## Additional Resources

The `analyze-tmr-data.py` script processes simulation results, and various Python scripts enable Monte Carlo simulations.

To run the simulation code, make sure to install the dependencies:
```bash
pip install numpy matplotlib PyLTSpice
```

To execute a Monte Carlo simulation, run:
```bash
python run_comprehensive_monte_carlo.py
``` 