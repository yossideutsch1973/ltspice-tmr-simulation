#!/usr/bin/env python3
"""
TMR Sensor Array - Analog Front-End Circuit Schematic Implementation
This script recreates the TMR sensor analog front-end circuit diagrams using the SchemaDraw library.

The implementation follows functional programming principles with:
- Pure functions for generating schematic elements
- Separation of side effects (file I/O) from core functionality
- Immutable data structures where possible
- Function composition for complex operations

The script now also includes LTSpice export functionality, allowing circuit diagrams to be exported
to LTSpice format for simulation.
"""

import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
import os
import traceback
from functools import partial, wraps
from typing import Callable, Dict, Tuple, List, Optional, Any, Union, TypeVar

# Import the LTSpice integration module
try:
    import ltspice_integration as ltspice
except ImportError:
    print("Warning: LTSpice integration module not found. LTSpice export disabled.")
    ltspice = None

# Type aliases for better code readability
Point = Tuple[float, float]
PinMap = Dict[str, Point]
Element = Any  # SchemDraw element type
Drawing = schemdraw.Drawing

# Define a TypeVar for function return type
T = TypeVar('T')

# Configuration constants
DEFAULT_UNIT_SIZE = 2.5
OUTPUT_DIR = 'schematics'
LTSPICE_DIR = 'ltspice_models'
FILE_FORMATS = ['png']  # Can be extended to ['png', 'svg', 'pdf']
ENABLE_LTSPICE_EXPORT = ltspice is not None  # Enable LTSpice export if module is available

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def ensure_output_directory(directory: str) -> str:
    """
    Create output directory if it doesn't exist and return the path.
    
    Args:
        directory: Path to the output directory
        
    Returns:
        The path to the output directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory
        
# Create output directory at import time
ensure_output_directory(OUTPUT_DIR)

def log_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to log errors and provide helpful error messages.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            print(f"Function args: {args}")
            print(f"Function kwargs: {kwargs}")
            print(traceback.format_exc())
            raise
    return wrapper

def save_drawing(drawing: Drawing, filename: str, 
                formats: List[str] = FILE_FORMATS) -> None:
    """
    Save a schematic drawing in multiple formats
    
    Args:
        drawing: The schemdraw Drawing object
        filename: Base filename without extension
        formats: List of file formats to save (e.g., ['png', 'svg'])
    """
    try:
        for fmt in formats:
            full_path = os.path.join(OUTPUT_DIR, f"{filename}.{fmt}")
            drawing.save(full_path)
            print(f"Saved: {full_path}")
    except Exception as e:
        print(f"Error saving drawing {filename}: {str(e)}")

def create_drawing(unit_size: float = DEFAULT_UNIT_SIZE) -> Drawing:
    """
    Create a new schemdraw Drawing with standard configuration
    
    Args:
        unit_size: Size of the drawing units
        
    Returns:
        Configured schemdraw Drawing object
    """
    d = schemdraw.Drawing()
    d.config(unit=unit_size)
    return d

# =============================================================================
# COMMON CIRCUIT ELEMENTS
# =============================================================================

def add_title_and_notes(d: Drawing, title: str, subtitle: str = None, 
                       bottom_note: str = None) -> Drawing:
    """
    Add standard title and notes to a drawing
    
    Args:
        d: The schemdraw Drawing object
        title: Main title text
        subtitle: Optional subtitle text
        bottom_note: Optional note for the bottom of the diagram
        
    Returns:
        Updated drawing with titles and notes
    """
    d += elm.Label().label(title, loc='top')
    
    if subtitle:
        d += elm.Label().label(subtitle, loc='top').at((0, -0.5)).color('blue')
        
    if bottom_note:
        d += elm.Label().label(bottom_note, loc='bottom').color('blue')
        
    return d

def add_power_supply(d: Drawing, position: Point, voltage: str, 
                    is_positive: bool = True, label: str = None) -> Drawing:
    """
    Add a power supply connection with label
    
    Args:
        d: The schemdraw Drawing object
        position: Base position for the power connection
        voltage: Voltage value with unit
        is_positive: Whether this is a positive supply (affects color)
        label: Optional label for the power pin
        
    Returns:
        Updated drawing with power supply connection
    """
    x, y = position
    direction = 'up' if is_positive else 'down'
    color = 'red' if is_positive else 'blue'
    
    if label:
        d += elm.Label().label(label).at((x-0.3, y))
        
    d += elm.Line().at(position).to((x, y + (0.5 if is_positive else -0.5)))
    d += elm.Label().label(voltage).at((x, y + (0.5 if is_positive else -0.5))).color(color)
    
    return d

def add_decoupling_capacitors(d: Drawing, power_point: Point, is_positive: bool = True, 
                            values: List[str] = ['100nF', '10μF']) -> Drawing:
    """
    Add standard decoupling capacitors to a power supply
    
    Args:
        d: The schemdraw Drawing object
        power_point: The power supply connection point
        is_positive: Whether this is a positive supply
        values: List of capacitor values
        
    Returns:
        Updated drawing with decoupling capacitors
    """
    x, y = power_point
    spacing = 0.75
    
    for i, value in enumerate(values):
        cap_x = x + (i+1) * spacing
        line_start = (cap_x - spacing, y)
        line_end = (cap_x, y)
        d += elm.Line().at(line_start).to(line_end)
        
        if is_positive:
            d += elm.Capacitor().at((cap_x, y)).to((cap_x, y-1)).label(value)
            d += elm.Ground().at((cap_x, y-1))
        else:
            d += elm.Capacitor().at((cap_x, y)).to((cap_x, y+1)).label(value)
            d += elm.Ground().at((cap_x, y+1))
    
    return d

def add_input_protection(d: Drawing, input_point: Point, 
                       resistor_value: str = '100Ω') -> Tuple[Drawing, Point]:
    """
    Add input protection circuit with resistor and TVS diode
    
    Args:
        d: The schemdraw Drawing object
        input_point: The input point position
        resistor_value: Value for the protection resistor
        
    Returns:
        Tuple of (updated drawing, output point after protection)
    """
    x, y = input_point
    
    # Add input label and dot
    d += elm.Dot().at(input_point)
    d += elm.Label().label('INPUT').at((x-0.7, y))
    
    # Add protection resistor
    input_end = (x+0.5, y)
    d += elm.Line().at(input_point).to(input_end)
    protect_pos = (x+0.5, y)
    protect_end = (x+1.0, y)
    d += elm.Resistor().at(protect_pos).to(protect_end).label(resistor_value)
    
    # Add TVS diode to ground
    tvs_pos = (protect_pos[0]+0.5, protect_pos[1])
    d += elm.Dot().at(tvs_pos)
    tvs_line_end = (tvs_pos[0], tvs_pos[1]-0.75)
    d += elm.Line().at(tvs_pos).to(tvs_line_end)
    tvs_diode_end = (tvs_pos[0], tvs_pos[1]-1.5)
    d += elm.Zener().at(tvs_line_end).to(tvs_diode_end).label('TVS')
    d += elm.Ground().at(tvs_diode_end)
    
    return d, tvs_pos

def add_test_point(d: Drawing, position: Point, label: str) -> Drawing:
    """
    Add a test point with label
    
    Args:
        d: The schemdraw Drawing object
        position: Position for the test point
        label: Test point label (e.g., 'TP1')
        
    Returns:
        Updated drawing with test point
    """
    x, y = position
    d += elm.Dot().at(position)
    d += elm.Label().label(label).at((x, y-0.3))
    return d

def add_technical_notes(d: Drawing, position: Point, title: str, notes: List[str], 
                      color: str = 'blue') -> Drawing:
    """
    Add technical notes to the schematic
    
    Args:
        d: The schemdraw Drawing object
        position: Top-left position for the notes
        title: Title for the notes section
        notes: List of notes to display
        color: Color for the notes text
        
    Returns:
        Updated drawing with technical notes
    """
    x, y = position
    d += elm.Label().label(title).at(position).color(color)
    
    for i, note in enumerate(notes):
        d += elm.Label().label(f"{i+1}. {note}").at((x, y-(i+0.5)*0.5)).color(color)
    
    return d

def add_opamp_power(d: Drawing, opamp_pos: Point) -> Drawing:
    """
    Add standard power connections to an op-amp
    
    Args:
        d: The schemdraw Drawing object
        opamp_pos: Position of the op-amp center
        
    Returns:
        Updated drawing with op-amp power connections
    """
    x, y = opamp_pos
    
    # V+ connection
    vs_pos = (x, y+1.5)
    add_power_supply(d, vs_pos, '+5V', True, 'V+')
    add_decoupling_capacitors(d, vs_pos, True, ['100nF'])
    
    # V- connection
    vm_pos = (x, y-1.5)
    add_power_supply(d, vm_pos, '-5V', False, 'V-')
    add_decoupling_capacitors(d, vm_pos, False, ['100nF'])
    
    return d

# =============================================================================
# CIRCUIT DRAWING FUNCTIONS - Higher Order Components
# =============================================================================

def with_error_handling(drawing_func: Callable) -> Callable:
    """
    Decorator to add standard error handling to drawing functions
    
    Args:
        drawing_func: The drawing function to decorate
        
    Returns:
        Decorated function with error handling
    """
    @wraps(drawing_func)
    def wrapper(*args, **kwargs):
        try:
            return drawing_func(*args, **kwargs)
        except Exception as e:
            circuit_name = drawing_func.__name__.replace('draw_', '')
            print(f"Error drawing {circuit_name}: {str(e)}")
            print(traceback.format_exc())
            # Still raise to prevent silent failures
            raise
    return wrapper

# =============================================================================
# INSTRUMENTATION AMPLIFIER SECTION
# =============================================================================

def draw_tmr_sensor(d: Drawing) -> Tuple[Element, PinMap]:
    """
    Draw TMR2305 sensor with appropriate connections.
    
    Args:
        d: The schemdraw Drawing object
    
    Returns:
        Tuple of (TMR element, dictionary of pin locations)
    """
    # Draw TMR2305 sensor as a rectangle
    tmr = d.add(elm.Rect(w=1.5, h=2.5).label('TMR2305', 'left'))
    
    # Get the coordinates of the rectangle corners
    tmr_top = (tmr.get_bbox()[0] + tmr.get_bbox()[2])/2, tmr.get_bbox()[3]
    tmr_right = tmr.get_bbox()[2], (tmr.get_bbox()[1] + tmr.get_bbox()[3])/2
    tmr_bottom = (tmr.get_bbox()[0] + tmr.get_bbox()[2])/2, tmr.get_bbox()[1]
    
    # Sensor pins
    d += elm.Line().right(0.5).at(tmr_right)
    d += elm.Label().label('OUT').at((tmr_right[0]+0.25, tmr_right[1]))
    
    # VDD connection with voltage specification
    vdd_line_end = (tmr_top[0]+0.5, tmr_top[1])
    d += elm.Line().at(tmr_top).to(vdd_line_end)
    d += elm.Label().label('VDD').at((tmr_top[0]+0.25, tmr_top[1]))
    vdd_up_end = (tmr_top[0], tmr_top[1]+0.5)
    d += elm.Line().at(tmr_top).to(vdd_up_end)
    d += elm.Label().label('+5V').at(vdd_up_end).color('red')
    
    # Add decoupling for TMR2305
    vdd_cap_pos = (tmr_top[0]+1, tmr_top[1]+0.5)
    vdd_cap_end = (vdd_cap_pos[0], vdd_cap_pos[1]-1)
    d += elm.Capacitor().at(vdd_cap_pos).to(vdd_cap_end).label('100nF')
    vdd_cap_line_end = (vdd_cap_pos[0]+0.5, vdd_cap_pos[1])
    d += elm.Line().at(vdd_cap_pos).to(vdd_cap_line_end)
    d += elm.Ground().at((vdd_cap_pos[0]+0.5, vdd_cap_pos[1]))
    
    # GND connection
    gnd_line_end = (tmr_bottom[0]+0.5, tmr_bottom[1])
    d += elm.Line().at(tmr_bottom).to(gnd_line_end)
    d += elm.Label().label('GND').at((tmr_bottom[0]+0.25, tmr_bottom[1]))
    d += elm.Ground().at((tmr_bottom[0]+0.5, tmr_bottom[1]))
    
    # Add ESD protection for TMR sensor output
    esd_resistor = d.add(elm.Resistor().right(1).label('100Ω\n(ESD)').at((tmr_right[0]+0.5, tmr_right[1])))
    esd_line_end = (esd_resistor.end[0], esd_resistor.end[1]+0.5)
    d += elm.Line().at(esd_resistor.end).to(esd_line_end)
    esd_diode_pos = (esd_resistor.end[0], esd_resistor.end[1]+0.5)
    d += elm.Diode().at(esd_diode_pos).to(esd_line_end).fill(True).label('TVS')
    d += elm.Ground().at(esd_line_end)
    
    # Add test point
    add_test_point(d, esd_resistor.end, 'TP1')
    
    # Create dictionary of pin locations
    pins = {
        'vdd': tmr_top,
        'out': (esd_resistor.end[0], esd_resistor.end[1]),
        'gnd': tmr_bottom
    }
    
    return tmr, pins

def draw_instrumentation_amp(d: Drawing, tmr_pins: PinMap) -> Tuple[Element, PinMap]:
    """
    Draw AD8220 instrumentation amplifier with connections.
    
    Args:
        d: The schemdraw Drawing object
        tmr_pins: Dictionary of TMR sensor pin locations
    
    Returns:
        Tuple of (in-amp element, dictionary of pin locations)
    """
    # Start instrumentation amplifier to the right of the TMR output
    in_amp_left = (tmr_pins['out'][0] + 1.5, tmr_pins['out'][1])
    
    # Draw AD8220 as a rectangular IC
    in_amp = d.add(elm.Rect(w=2.5, h=3).label('AD8220', 'center').at(in_amp_left))
    
    # Define pin locations relative to the in-amp position
    in_amp_bbox = in_amp.get_bbox()
    in_amp_left_edge = in_amp_bbox[0]
    in_amp_right_edge = in_amp_bbox[2]
    in_amp_top_edge = in_amp_bbox[3]
    in_amp_bottom_edge = in_amp_bbox[1]
    in_amp_center_y = (in_amp_top_edge + in_amp_bottom_edge) / 2
    
    # Create pins dictionary with all connection points
    pins = {
        'in+': (in_amp_left_edge, in_amp_center_y + 0.75),
        'in-': (in_amp_left_edge, in_amp_center_y - 0.75),
        'ref': (in_amp_left_edge, in_amp_center_y),
        'rg1': (in_amp_left_edge, in_amp_bottom_edge + 0.5),
        'rg2': (in_amp_right_edge, in_amp_bottom_edge + 0.5),
        'out': (in_amp_right_edge, in_amp_center_y),
        'vs+': (in_amp_right_edge - 0.75, in_amp_top_edge),
        'vs-': (in_amp_right_edge - 0.75, in_amp_bottom_edge),
    }
    
    # Connect TMR output to in_amp input
    d += elm.Line().right().at(tmr_pins['out']).to(pins['in+'])
    
    # Connect inputs with labels
    for pin_name, position in pins.items():
        if pin_name in ['in+', 'in-', 'ref', 'rg1', 'rg2', 'out']:
            d += elm.Label().label(pin_name).at((position[0] - 0.2 if 'in' in pin_name or 'ref' == pin_name or 'rg1' == pin_name 
                                                else position[0] + 0.2, 
                                                position[1] + 0.3))
    
    # Ground the negative input (for single-ended operation)
    neg_in_end = (pins['in-'][0], pins['in-'][1]-0.75)
    d += elm.Line().at(pins['in-']).to(neg_in_end)
    d += elm.Ground()
    
    # Connect ground to reference pin
    ref_end = (pins['ref'][0], pins['ref'][1]-0.5)
    d += elm.Line().at(pins['ref']).to(ref_end)
    d += elm.Ground()
    
    return in_amp, pins

def draw_power_supply_decoupling(d: Drawing, in_amp_pins: PinMap) -> None:
    """
    Draw power supply decoupling for instrumentation amplifier.
    
    Args:
        d: The schemdraw Drawing object
        in_amp_pins: Dictionary of instrumentation amplifier pin locations
    """
    # Connect +5V to VS+
    vs_plus_pin = in_amp_pins['vs+']
    add_power_supply(d, vs_plus_pin, '+5V', True)
    
    # Add decoupling capacitors for +5V
    add_decoupling_capacitors(d, (vs_plus_pin[0], vs_plus_pin[1] + 0.5), True, ['100nF', '10μF']) 
    
    # Connect -5V to VS-
    vs_minus_pin = in_amp_pins['vs-']
    add_power_supply(d, vs_minus_pin, '-5V', False)
    
    # Add decoupling capacitors for -5V
    add_decoupling_capacitors(d, (vs_minus_pin[0], vs_minus_pin[1] - 0.5), False, ['100nF', '10μF'])

def draw_gain_stage(d: Drawing, in_amp_pins: PinMap) -> None:
    """
    Draw gain setting resistor for instrumentation amplifier.
    
    Args:
        d: The schemdraw Drawing object
        in_amp_pins: Dictionary of instrumentation amplifier pin locations
    """
    # Connect RG1 and RG2 with gain resistor
    rg1_pin = in_amp_pins['rg1']
    rg2_pin = in_amp_pins['rg2']
    
    # Draw a line from RG1 down and right
    rg1_end = (rg1_pin[0]-0.75, rg1_pin[1]-0.5)
    d += elm.Line().at(rg1_pin).to(rg1_end)
    
    # Draw a line from RG2 down and left
    rg2_end = (rg2_pin[0]+0.75, rg2_pin[1]-0.5)
    d += elm.Line().at(rg2_pin).to(rg2_end)
    
    # Connect with gain resistor
    # Adjust if positions are not aligned
    if rg1_end[1] != rg2_end[1]:
        # Align them
        rg1_end = (rg1_end[0], (rg1_end[1] + rg2_end[1]) / 2)
        rg2_end = (rg2_end[0], (rg1_end[1] + rg2_end[1]) / 2)
    
    # Draw resistor between extended points
    d += elm.Resistor().right().at(rg1_end).to(rg2_end).label('4.99kΩ\n0.1%')
    
    # Add gain formula note
    d += elm.Label().label('Gain = 1 + (49.4kΩ / 4.99kΩ) = 10.9').at(
        ((rg1_end[0] + rg2_end[0]) / 2, rg1_end[1] - 0.5)
    ).color('blue')

def draw_output_stage(d: Drawing, in_amp_pins: PinMap) -> None:
    """
    Draw output connections for instrumentation amplifier.
    
    Args:
        d: The schemdraw Drawing object
        in_amp_pins: Dictionary of instrumentation amplifier pin locations
    """
    # Add output connection and test point
    out_pin = in_amp_pins['out']
    output_line_end = (out_pin[0]+1.5, out_pin[1])
    d += elm.Line().at(out_pin).to(output_line_end)
    
    # Add test point
    add_test_point(d, output_line_end, 'TP2')
    
    # Add output label
    d += elm.Label().label('To Stage 2\nLow-Pass Filter').at(
        (output_line_end[0] + 0.5, output_line_end[1])
    )
    
    # Add design notes
    notes = [
        'AD8220 configured for single-ended operation',
        'Input protection provided by 100Ω + TVS diode',
        'Gain set to 10.9x for full-scale output',
        'Decoupling includes both 100nF (ceramic) and 10μF (tantalum) capacitors'
    ]
    
    add_technical_notes(d, (output_line_end[0] - 2, output_line_end[1] - 2), 'NOTES:', notes)

@with_error_handling
def draw_instrumentation_amplifier(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the Stage 1: Instrumentation Amplifier circuit with TMR2305 sensor
    
    Args:
        unit_size: Size of the drawing units
    """
    # Create a new drawing
    d = create_drawing(unit_size=unit_size)
    
    # Add title and notes
    add_title_and_notes(
        d, 
        'STAGE 1: INSTRUMENTATION AMPLIFIER',
        None,
        'All resistors 0.1% tolerance unless otherwise noted'
    )
    
    # Use helper functions to draw each component
    tmr, tmr_pins = draw_tmr_sensor(d)
    in_amp, in_amp_pins = draw_instrumentation_amp(d, tmr_pins)
    draw_power_supply_decoupling(d, in_amp_pins)
    draw_gain_stage(d, in_amp_pins)
    draw_output_stage(d, in_amp_pins)
    
    # Save the completed drawing
    save_drawing(d, 'stage1_instrumentation_amplifier')

# =============================================================================
# ACTIVE FILTER SECTION
# =============================================================================

@with_error_handling
def draw_active_filter(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the Stage 2: Active Low-Pass Filter circuit
    
    Args:
        unit_size: Size of the drawing units
    """
    # Create a new drawing
    d = create_drawing(unit_size=unit_size)
    
    # Add title and notes
    add_title_and_notes(
        d,
        'STAGE 2: ACTIVE LOW-PASS FILTER (20kHz CUTOFF)',
        'Sallen-Key 2nd Order Low-Pass Filter',
        'All resistors 1% tolerance unless otherwise noted'
    )
    
    # Draw input and protection circuit
    input_point = (0, 0)
    d, tvs_pos = add_input_protection(d, input_point)
    
    # Junction for R6 and C2
    d += elm.Line().right(0.5).at(tvs_pos)
    junction1 = (tvs_pos[0]+0.5, tvs_pos[1])
    d += elm.Dot().at(junction1)
    
    # C2 capacitor
    c2_end = (junction1[0]+1.5, junction1[1])
    c2 = d.add(elm.Capacitor().at(junction1).to(c2_end).label('C2\n10nF\nX7R\n±5%'))
    
    # R6 resistor
    r6_end = (junction1[0], junction1[1]-2)
    r6 = d.add(elm.Resistor().at(junction1).to(r6_end).label('R6\n10kΩ\n1%'))
    
    # Junction after C2
    junction2 = c2.end
    d += elm.Dot().at(junction2)
    
    # R7 resistor
    r7_end = (junction2[0]+2, junction2[1])
    r7 = d.add(elm.Resistor().at(junction2).to(r7_end).label('R7\n16.5kΩ\n0.1%'))
    
    # OpAmp
    r7_right = r7.get_bbox()[2]
    opamp_pos = (r7_right+1.5, junction1[1]-1)
    opamp = d.add(elm.Opamp(leads=True).at(opamp_pos))
    
    # Get opamp terminals
    op_in1 = opamp.anchors['in1']
    op_in2 = opamp.anchors['in2']
    op_out = opamp.anchors['out']
    
    d += elm.Label().label('OPA2387').at((opamp_pos[0], opamp_pos[1]+0.7))
    d += elm.Label().label('Precision Op-Amp').at((opamp_pos[0], opamp_pos[1]+0.3)).color('blue')
    
    # Add power connections for opamp
    add_opamp_power(d, opamp_pos)
    
    # Connect junction2 to OpAmp
    junction2_end = (junction2[0], junction2[1]-1)
    d += elm.Line().at(junction2).to(junction2_end)
    d += elm.Line().right(3.5).at((junction2[0], junction2[1]-1))
    
    # R8 resistor and connection to OpAmp
    r8_pos = (op_in2[0]-1, op_in2[1])
    r8_end = (r8_pos[0]-2, r8_pos[1])
    r8 = d.add(elm.Resistor().at(r8_pos).to(r8_end).label('R8\n10kΩ\n1%'))
    
    # Connect R6 to R8
    r6_bottom = r6_end[1]
    r6_line_end = (junction1[0]+5, r6_bottom)
    d += elm.Line().at((junction1[0], r6_bottom)).to(r6_line_end)
    d += elm.Dot().at(r6_line_end)
    
    # Connect dot to opamp
    r6_up_end = (r6_line_end[0], r6_line_end[1]+1)
    d += elm.Line().at(r6_line_end).to(r6_up_end)
    
    # C3 capacitor
    r8_left = r8.get_bbox()[0]
    c3_start = (r8_left-1, r8_pos[1])
    c3_end = (c3_start[0], c3_start[1]-2)
    c3 = d.add(elm.Capacitor().at(c3_start).to(c3_end).label('C3\n100nF\nX7R\n±5%'))
    
    # Connect C3 to output
    c3_bottom = c3_end[1]
    c3_line_end = (c3_start[0]+5, c3_bottom)
    d += elm.Line().at((c3_start[0], c3_bottom)).to(c3_line_end)
    
    # Final output from op-amp
    op_out_end = (op_out[0]+1, op_out[1])
    d += elm.Line().at(op_out).to(op_out_end)
    d += elm.Dot().at(op_out_end)
    output_point = op_out_end
    
    # Add output label
    output_up_end = (output_point[0], output_point[1]+0.5)
    d += elm.Line().at(output_point).to(output_up_end)
    d += elm.Label().label('OUTPUT').at((output_point[0], output_point[1]+0.8))
    
    # Add test point at output
    d += elm.Line().up(0.5).at(output_point)
    d += elm.Dot(open=True).at((output_point[0], output_point[1]+0.5))
    d += elm.Label().label('TP3').at((output_point[0], output_point[1]+0.7))
    
    # Add design notes
    notes = [
        'Cutoff frequency = 20kHz',
        'Damping factor = 0.707 (Butterworth response)',
        'Input impedance > 10kΩ',
        'Use X7R capacitors for temperature stability'
    ]
    add_technical_notes(d, (junction1[0]+3, junction1[1]+3), 'NOTES:', notes)
    
    # Save the drawing
    save_drawing(d, 'stage2_active_lowpass_filter')

# =============================================================================
# LEVEL SHIFTER SECTION
# =============================================================================

@with_error_handling
def draw_level_shifter(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the Stage 3: Level Shifter circuit
    
    Args:
        unit_size: Size of the drawing units
    """
    # Create a new drawing
    d = create_drawing(unit_size=unit_size)
    
    # Add title and notes
    add_title_and_notes(
        d,
        'STAGE 3: LEVEL SHIFTER (0-3.3V OUTPUT RANGE)',
        'Non-inverting Summing Amplifier with Level Shift',
        'All resistors 0.1% tolerance unless otherwise noted'
    )
    
    # Draw input
    input_point = (0, 0)
    d, tvs_pos = add_input_protection(d, input_point)
    
    # Save the drawing
    save_drawing(d, 'stage3_level_shifter')

# =============================================================================
# MULTIPLEXER SECTION
# =============================================================================

@with_error_handling
def draw_multiplexer(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the 16-Channel Multiplexer circuit
    
    Args:
        unit_size: Size of the drawing units
    """
    with schemdraw.Drawing() as d:
        d.config(unit=unit_size)
        d += elm.Label().label('16-CHANNEL MULTIPLEXING CIRCUIT', loc='top')
        d += elm.Label().label('16-to-4 Analog Channel Selection', loc='top').at((0, -0.5)).color('blue')
        
        # Main box for ADG1607
        box = d.add(elm.Rect(w=8, h=12).label('ADG1607 16-Channel Analog Multiplexer', 'top'))
        
        # Get box corners
        box_left = box.get_bbox()[0]
        box_right = box.get_bbox()[2]
        box_top = box.get_bbox()[3]
        box_bottom = box.get_bbox()[1]
        
        # Add digital isolator for control signals
        iso_left = box_left - 5
        iso_top = box_top - 2
        iso_box = d.add(elm.Rect(w=3, h=3).at((iso_left, iso_top)))
        d += elm.Label().label('ADuM140x\nDigital Isolator').at((iso_left+1.5, iso_top+1.5))
        
        # Add microcontroller side
        d += elm.Label().label('From\nMCU').at((iso_left-1.5, iso_top+1.5)).color('green')
        
        # Channel inputs (left side)
        x_start = box_left
        y_start = box_top - 2
        spacing = 0.5
        
        # Add control inputs with isolation
        for i, label in enumerate(['S0', 'S1', 'S2', 'S3']):
            y = y_start - i * spacing
            
            # Connect from isolator to multiplexer
            iso_out = (iso_left+3, iso_top+0.5-(i*0.5))
            iso_up = (iso_left+4, iso_top+0.5-(i*0.5))
            y_connection = (iso_left+4, y)
            mux_in = (box_left, y)
            
            # Fixed: Using .at() and .to() instead of directional methods with .at()
            d += elm.Line().at(iso_out).to(iso_up)
            d += elm.Line().at(iso_up).to(y_connection)
            d += elm.Line().at(y_connection).to(mux_in)
            
            # Add pull-up resistor for each control line
            pull_up_pos = (x_start-1.5, y)
            pull_up_end = (pull_up_pos[0], pull_up_pos[1]+0.75)
            
            # Fixed: Using .at() and .to() instead of .up() with .at()
            d += elm.Resistor().at(pull_up_pos).to(pull_up_end).label('4.7kΩ')
            d += elm.Label().label('+3.3V').at((pull_up_pos[0], pull_up_pos[1]+1)).color('orange')
            
            # Connect to multiplexer
            mux_conn1 = (x_start-1, y)
            mux_conn2 = (x_start, y)
            
            # Fixed: Using .at() and .to() instead of directional methods with .at()
            d += elm.Line().at(mux_conn1).to(mux_conn2)
            d += elm.Label().label(label).at((x_start-1.2, y))
        
        # Add EN (Enable) input with pull-down
        y_en = y_start - 4 * spacing
        en_out = (iso_left+3, iso_top-1.5)
        en_right = (iso_left+4, iso_top-1.5)
        en_down = (iso_left+4, y_en)
        mux_en = (box_left, y_en)
        
        # Fixed: Using .at() and .to() instead of directional methods with .at()
        d += elm.Line().at(en_out).to(en_right)
        d += elm.Line().at(en_right).to(en_down)
        d += elm.Line().at(en_down).to(mux_en)
        d += elm.Label().label('EN').at((x_start-1.2, y_en))
        
        # Add pull-down for EN
        pull_down_pos = (x_start-1.5, y_en)
        pull_down_end = (pull_down_pos[0], pull_down_pos[1]-0.75)
        
        # Fixed: Using .at() and .to() instead of .down() with .at()
        d += elm.Dot().at(pull_down_pos)
        d += elm.Resistor().at(pull_down_pos).to(pull_down_end).label('10kΩ')
        d += elm.Ground().at(pull_down_end)
        
        # Add 16 input channels on the left
        channel_start_y = box_top - 2
        channel_spacing = 0.5
        
        # Add output channels on the right
        x_end = box_right
        
        for i in range(4):
            y = channel_start_y - i * spacing
            
            # Add output channel
            out_end = (x_end+1, y)
            
            # Fixed: Using .at() and .to() instead of .right() with .at()
            d += elm.Line().at((x_end, y)).to(out_end)
            d += elm.Label().label(f'D{i}').at((x_end-0.5, y))
            
            # Add filter and buffer
            filter_pos = (x_end+1, y)
            filter_end = (filter_pos[0]+0.75, filter_pos[1])
            
            d += elm.Dot().at(filter_pos)
            
            # Fixed: Using .at() and .to() instead of .right() with .at()
            d += elm.Resistor().at(filter_pos).to(filter_end).label('33Ω')
            
            # Add capacitor to ground
            cap_pos = (filter_end[0], filter_end[1])
            cap_down = (cap_pos[0], cap_pos[1]-0.5)
            cap_end = (cap_pos[0], cap_pos[1]-1)
            
            d += elm.Dot().at(cap_pos)
            
            # Fixed: Using .at() and .to() instead of .down() with .at()
            d += elm.Line().at(cap_pos).to(cap_down)
            d += elm.Capacitor().at(cap_down).to(cap_end).label('100pF')
            d += elm.Ground().at(cap_end)
            
            # Add buffer op-amp
            buffer_pos = (cap_pos[0]+1, cap_pos[1])
            
            # Fixed: Using proper anchor naming and positioning
            buffer = d.add(elm.Opamp(leads=False).anchor('in1').at(buffer_pos))
        
        # Add decoupling capacitors for multiplexer
        add_decoupling_capacitors(d, (box_left+2, box_top), True, ['100nF', '10μF'])
        
        # Add technical notes
        notes = [
            "Control lines (S0-S3) select channel according to truth table",
            "Digital isolation provided for all control signals",
            "Pull-up/down resistors ensure defined states",
            "Anti-aliasing filters on all outputs",
            "ESD protection on all analog inputs"
        ]
        
        add_technical_notes(d, (box_left+1, box_bottom-3), 'NOTES:', notes)
        
        d.save('schematics/multiplexer_circuit.png')

# =============================================================================
# ADC SECTION
# =============================================================================

@with_error_handling
def draw_adc(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the ADC Interface circuit
    
    Args:
        unit_size: Size of the drawing units
    """
    with schemdraw.Drawing() as d:
        d.config(unit=unit_size)
        d += elm.Label().label('ADC INTERFACE CIRCUIT (ADS8688)', loc='top')
        d += elm.Label().label('8-Channel, 16-Bit Analog-to-Digital Converter', loc='top').at((0, -0.5)).color('blue')
        
        # Create a helper function for drawing input filters
        def draw_input_filter(d, x_start, y, channel):
            # Draw input line from left
            input_point = (x_start, y)
            d += elm.Dot().at(input_point)
            d += elm.Label().label(f'AIN{channel}').at((input_point[0]-0.5, input_point[1]))
            
            # Add anti-aliasing filter (2-pole RC)
            # First resistor
            res1_start = input_point
            res1_end = (res1_start[0]+1, res1_start[1])
            
            # Fixed: Using .at() and .to() instead of .right() with .at()
            d += elm.Resistor().at(res1_start).to(res1_end).label('33Ω')
            
            # First capacitor
            cap1_pos = res1_end
            cap1_down = (cap1_pos[0], cap1_pos[1]-0.75)
            cap1_end = (cap1_pos[0], cap1_pos[1]-1.5)
            
            d += elm.Dot().at(cap1_pos)
            
            # Fixed: Using .at() and .to() instead of .down() with .at()
            d += elm.Line().at(cap1_pos).to(cap1_down)
            d += elm.Capacitor().at(cap1_down).to(cap1_end).label('100pF')
            d += elm.Ground().at(cap1_end)
            
            # Second resistor
            res2_start = cap1_pos
            res2_end = (res2_start[0]+1, res2_start[1])
            
            # Fixed: Using .at() and .to() instead of .right() with .at()
            d += elm.Resistor().at(res2_start).to(res2_end).label('33Ω')
            
            # Second capacitor
            cap2_pos = res2_end
            cap2_down = (cap2_pos[0], cap2_pos[1]-0.75)
            cap2_end = (cap2_pos[0], cap2_pos[1]-1.5)
            
            d += elm.Dot().at(cap2_pos)
            
            # Fixed: Using .at() and .to() instead of .down() with .at()
            d += elm.Line().at(cap2_pos).to(cap2_down)
            d += elm.Capacitor().at(cap2_down).to(cap2_end).label('100pF')
            d += elm.Ground().at(cap2_end)
            
            # ESD protection
            diode_pos = (cap2_pos[0]+1, cap2_pos[1])
            
            # Fixed: Using .at() and .to() instead of .right() with .at()
            d += elm.Line().at(cap2_pos).to(diode_pos)
            
            # TVS diodes in both directions
            diode_up = (diode_pos[0], diode_pos[1]+0.75)
            diode_up_end = (diode_pos[0], diode_pos[1]+1.5)
            
            # Fixed: Using .at() and .to() instead of .up() with .at()
            d += elm.Line().at(diode_pos).to(diode_up)
            d += elm.Diode().at(diode_up).to(diode_up_end).label('ESD')
            d += elm.Label().label('+3.3V').at(diode_up_end).color('orange')
            
            diode_down = (diode_pos[0], diode_pos[1]-0.75)
            diode_down_end = (diode_pos[0], diode_pos[1]-1.5)
            
            # Fixed: Using .at() and .to() instead of .down() with .at()
            d += elm.Line().at(diode_pos).to(diode_down)
            d += elm.Diode().at(diode_down).to(diode_down_end).flip().label('ESD')
            d += elm.Ground().at(diode_down_end)
            
            # Connect to ADC input
            adc_conn = (diode_pos[0]+1.25, diode_pos[1])
            
            # Fixed: Using .at() and .to() instead of .right() with .at()
            d += elm.Line().at(diode_pos).to(adc_conn)
            
            return adc_conn
            
        # Main box for ADS8688
        box_width = 8
        box_height = 12
        box_left = -4  # Center the box horizontally
        box_top = 6    # Position the top of the box
        # Use 'at' instead of non-existent 'center' method
        box = d.add(elm.Rect(w=box_width, h=box_height).at((box_left, box_top-box_height)).label('ADS8688', 'top'))
        
        # Get box corners
        box_left = box.get_bbox()[0]
        box_right = box.get_bbox()[2]
        box_top = box.get_bbox()[3]
        box_bottom = box.get_bbox()[1]
        
        # Add section labels
        d += elm.Label().label('Analog Inputs').at((box_left+2, box_top-1))
        d += elm.Label().label('Digital Interface').at((box_right-2, box_top-1))
        d += elm.Label().label('Reference').at((box_left+2, box_top-6))
        d += elm.Label().label('Clock').at((box_right-2, box_top-6))
        
        # Draw 8 input channels
        for i in range(8):
            y_pos = box_top - 1 - i * 1.25
            draw_input_filter(d, box_left - 6, y_pos, i)
            
        # SPI Interface with digital isolation
        iso_right = box_right + 2
        iso_top = box_top - 2
        iso_box = d.add(elm.Rect(w=3, h=3).at((iso_right, iso_top)))
        d += elm.Label().label('ISO7741\nDigital Isolator').at((iso_right+1.5, iso_top+1.5))
        
        # Add MCU side
        d += elm.Label().label('To\nMCU').at((iso_right+4.5, iso_top+1.5)).color('green')
        
        # Add SPI connections with pull-up resistors
        spi_labels = ['SCLK', 'MOSI', 'MISO', '/CS']
        
        # Define spacing for SPI signals
        spacing = 0.5
        
        # Draw digital connections
        for i, label in enumerate(spi_labels):
            y = box_top - 1 - i * spacing
            
            # Add connection from ADC to isolator
            x_end = box_right
            iso_in = (iso_right, y)
            
            # Fixed: Using .at() and .to() instead of .right() with .at()
            d += elm.Line().at((x_end, y)).to(iso_in)
            
            # Add pull-up resistors
            pull_up_pos = (x_end+1, y)
            pull_up_top = (pull_up_pos[0], pull_up_pos[1]+0.75)
            pull_up_end = (pull_up_pos[0], pull_up_pos[1]+1.5)
            
            d += elm.Dot().at(pull_up_pos)
            
            # Fixed: Using .at() and .to() instead of .up() with .at()
            d += elm.Line().at(pull_up_pos).to(pull_up_top)
            d += elm.Resistor().at(pull_up_top).to(pull_up_end).label('4.7kΩ')
            d += elm.Label().label('+3.3V').at((pull_up_end[0], pull_up_end[1]+0.25)).color('orange')
            
            # Add label
            d += elm.Label().label(label).at((x_end-0.5, y))
        
        # Add reference circuit
        ref_pos = (box_left-2, box_top-8)
        ref_box = d.add(elm.Rect(w=2, h=1.5).at(ref_pos).label('REF5025', 'top'))
        d += elm.Label().label('2.5V Reference').at((ref_pos[0]+1, ref_pos[1]-0.5)).color('blue')
        
        # Connect reference to ADC
        ref_out = (ref_pos[0]+2, ref_pos[1]-0.75)
        adc_ref = (box_left, box_top-8)
        
        # Fixed: Using .at() and .to() instead of directional methods with .at()
        d += elm.Line().at(ref_out).to(adc_ref)
        d += elm.Label().label('REFP').at((box_left-0.5, box_top-8))
        
        # Add decoupling
        add_decoupling_capacitors(d, (ref_pos[0]+1, ref_pos[1]-1.5), False, ['100nF', '1μF'])
        
        # Add notes
        notes = [
            "2-pole anti-aliasing filters on all inputs (33Ω, 100pF)",
            "Digital isolation for all SPI signals",
            "Precision 2.5V voltage reference with buffer",
            "ESD protection on all analog inputs",
            "4.7kΩ pull-up resistors on all SPI signals"
        ]
        
        add_technical_notes(d, (box_left+1, box_bottom-4), 'NOTES:', notes)
        
        d.save('schematics/adc_interface.png')

# =============================================================================
# MAIN FUNCTION AND ENTRY POINT
# =============================================================================

def main(unit_size: float = DEFAULT_UNIT_SIZE, 
         output_dir: str = OUTPUT_DIR,
         ltspice_dir: str = LTSPICE_DIR,
         formats: List[str] = FILE_FORMATS,
         enable_ltspice: bool = ENABLE_LTSPICE_EXPORT) -> None:
    """
    Main function to draw all circuit diagrams and save to files.
    
    Args:
        unit_size: Size of the grid units for drawing
        output_dir: Directory to save output files
        ltspice_dir: Directory to save LTSpice model files
        formats: List of file formats to save (e.g. ['png', 'svg', 'pdf'])
        enable_ltspice: Whether to enable LTSpice export functionality
    """
    print("TMR Sensor Array - Analog Front-End Circuit Schematics")
    print("------------------------------------------------------")
    
    # Create output directories
    ensure_output_directory(output_dir)
    if enable_ltspice:
        ensure_output_directory(ltspice_dir)
    
    # List of circuit drawing functions and their names
    circuits = [
        (draw_instrumentation_amplifier, "stage1_instrumentation_amplifier"),
        (draw_active_filter, "stage2_active_lowpass_filter"),
        (draw_level_shifter, "stage3_level_shifter"),
        (draw_multiplexer, "multiplexer_circuit"),
        (draw_adc, "adc_interface")
    ]
    
    # Draw and save each circuit
    for draw_func, name in circuits:
        try:
            print(f"Drawing {name}...")
            # Call the drawing function to generate the circuit
            drawing = draw_func(unit_size)
            
            # Save the drawing to files
            save_drawing(drawing, os.path.join(output_dir, name), formats)
            
            # Export to LTSpice if enabled
            if enable_ltspice and ltspice is not None:
                try:
                    print(f"Exporting {name} to LTSpice format...")
                    ltspice.export_to_ltspice(name, drawing, ltspice_dir)
                    print(f"LTSpice export successful: {os.path.join(ltspice_dir, name + '.net')}")
                except Exception as e:
                    print(f"Error exporting to LTSpice: {str(e)}")
            
            print(f"Successfully completed {name}")
        except Exception as e:
            print(f"Error drawing {name}: {str(e)}")
            traceback.print_exc()
    
    # Create LTSpice component model library if enabled
    if enable_ltspice and ltspice is not None:
        try:
            print("Creating LTSpice model library...")
            # Define component models for the TMR sensor array circuits
            model_specs = {
                'AD8220': {
                    'type': 'subckt',
                    'ports': 'IN+ IN- REF RG VS+ VS- OUT',
                    'definition': [
                        "* AD8220 Instrumentation Amplifier",
                        "X1 IN+ REF VS+ VS- BUFF OUT OPAMP1",
                        "X2 IN- REF VS+ VS- BUFF OPAMP1",
                        "RG1 RG BUFF 1",
                        ".MODEL OPAMP1 AMP(A=100K GAIN=110dB)"
                    ]
                },
                'OPA2387': {
                    'type': 'subckt',
                    'ports': 'IN+ IN- VS+ VS- OUT',
                    'definition': [
                        "* OPA2387 Precision Op-Amp",
                        "A1 IN+ IN- VS+ VS- OUT OPAMP2",
                        ".MODEL OPAMP2 AMP(A=1E6 GAIN=120dB GBW=10MEG)"
                    ]
                },
                'TMR2305': {
                    'type': 'subckt',
                    'ports': 'P1 P2',
                    'definition': [
                        "* TMR2305 Tunneling Magnetoresistive Sensor",
                        "R1 P1 P2 R={2.5k+2.5k*sin((angle-90)*pi/180)}",
                        ".PARAM angle=0"
                    ]
                },
                'ADG1607': {
                    'type': 'subckt',
                    'ports': 'S1 S2 S3 S4 S5 S6 S7 S8 S9 S10 S11 S12 S13 S14 S15 S16 D S0 S1 S2 S3 EN VDD GND',
                    'definition': [
                        "* ADG1607 16-channel Multiplexer",
                        "* Simplified model for simulation purposes"
                    ]
                },
                'ADS8688': {
                    'type': 'subckt',
                    'ports': 'AIN0 AIN1 AIN2 AIN3 AIN4 AIN5 AIN6 AIN7 REFP REFN AVDD DVDD GND SCLK MOSI MISO CS',
                    'definition': [
                        "* ADS8688 16-bit ADC",
                        "* Simplified model for simulation purposes"
                    ]
                }
            }
            # Create the model library
            lib_file = ltspice.create_ltspice_model_library(model_specs, ltspice_dir)
            print(f"LTSpice model library created: {lib_file}")
        except Exception as e:
            print(f"Error creating LTSpice model library: {str(e)}")
    
    print("\nAll circuit diagrams completed.")
    print(f"Output files saved to {os.path.abspath(output_dir)}")
    if enable_ltspice:
        print(f"LTSpice models saved to {os.path.abspath(ltspice_dir)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TMR Sensor Array Schematic Generator')
    parser.add_argument('--unit-size', type=float, default=DEFAULT_UNIT_SIZE,
                       help=f'Set the unit size for all drawings (default: {DEFAULT_UNIT_SIZE})')
    parser.add_argument('--output-dir', type=str, default=OUTPUT_DIR,
                       help=f'Set the output directory (default: {OUTPUT_DIR})')
    parser.add_argument('--ltspice-dir', type=str, default=LTSPICE_DIR,
                       help=f'Set the LTSpice model directory (default: {LTSPICE_DIR})')
    parser.add_argument('--format', nargs='+', default=FILE_FORMATS,
                       help=f'Set the output format(s) (default: {FILE_FORMATS})')
    
    args = parser.parse_args()
    
    main(
        unit_size=args.unit_size,
        output_dir=args.output_dir,
        ltspice_dir=args.ltspice_dir,
        formats=args.format
    )
