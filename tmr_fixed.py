#!/usr/bin/env python3
"""
TMR Sensor Array - Analog Front-End Circuit Schematic Implementation
This script recreates the TMR sensor analog front-end circuit diagrams using the SchemaDraw library.

The implementation follows functional programming principles with:
- Pure functions for generating schematic elements
- Separation of side effects (file I/O) from core functionality
- Immutable data structures where possible
- Function composition for complex operations
"""

import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
import os
from functools import partial
from typing import Callable, Dict, Tuple, List, Optional, Any

# Configuration constants
DEFAULT_UNIT_SIZE = 2.5
OUTPUT_DIR = 'schematics'
FILE_FORMATS = ['png']  # Can be extended to ['png', 'svg', 'pdf']

def ensure_output_directory(directory: str) -> None:
    """
    Create output directory if it doesn't exist
    
    Args:
        directory: Path to the output directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        
# Create output directory at import time
ensure_output_directory(OUTPUT_DIR)

def save_drawing(drawing: schemdraw.Drawing, filename: str, 
                formats: List[str] = FILE_FORMATS) -> None:
    """
    Save a schematic drawing in multiple formats
    
    Args:
        drawing: The schemdraw Drawing object
        filename: Base filename without extension
        formats: List of file formats to save (e.g., ['png', 'svg'])
    """
    for fmt in formats:
        full_path = os.path.join(OUTPUT_DIR, f"{filename}.{fmt}")
        drawing.save(full_path)
        
def create_drawing(unit_size: float = DEFAULT_UNIT_SIZE) -> schemdraw.Drawing:
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

def draw_instrumentation_amplifier(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the Stage 1: Instrumentation Amplifier circuit with TMR2305 sensor
    
    Args:
        unit_size: Size of the drawing units
    """
    # Create a new drawing
    d = create_drawing(unit_size=unit_size)
    
    # Add title and notes
    d += elm.Label().label('STAGE 1: INSTRUMENTATION AMPLIFIER', loc='top')
    d += elm.Label().label('All resistors 0.1% tolerance unless otherwise noted', loc='bottom').color('blue')
    
    # Use helper functions to draw each component
    tmr, tmr_pins = draw_tmr_sensor(d)
    in_amp, in_amp_pins = draw_instrumentation_amp(d, tmr_pins)
    draw_power_supply_decoupling(d, in_amp_pins)
    draw_reference_connections(d, in_amp_pins)
    draw_gain_stage(d, in_amp_pins)
    draw_output_stage(d, in_amp_pins)
    
    # Save the completed drawing
    save_drawing(d, 'stage1_instrumentation_amplifier')

def draw_tmr_sensor(d: schemdraw.Drawing) -> Tuple[elm.Element, Dict[str, Tuple[float, float]]]:
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
    d += elm.Line().right(0.5).at(tmr_top)
    d += elm.Label().label('VDD').at((tmr_top[0]+0.25, tmr_top[1]))
    d += elm.Line().up(0.5).at((tmr_top[0], tmr_top[1]))
    d += elm.Label().label('+5V').at((tmr_top[0], tmr_top[1]+0.5)).color('red')
    
    # Add decoupling for TMR2305
    vdd_cap_pos = (tmr_top[0]+1, tmr_top[1]+0.5)
    d += elm.Capacitor().down(1).label('100nF').at(vdd_cap_pos)
    d += elm.Line().right(0.5).at((vdd_cap_pos[0], vdd_cap_pos[1]))
    d += elm.Ground().at((vdd_cap_pos[0]+0.5, vdd_cap_pos[1]))
    
    # GND connection
    d += elm.Line().right(0.5).at(tmr_bottom)
    d += elm.Label().label('GND').at((tmr_bottom[0]+0.25, tmr_bottom[1]))
    d += elm.Ground().at((tmr_bottom[0]+0.5, tmr_bottom[1]))
    
    # Add ESD protection for TMR sensor output
    esd_resistor = d.add(elm.Resistor().right(1).label('100Ω\n(ESD)').at((tmr_right[0]+0.5, tmr_right[1])))
    esd_diode_pos = (esd_resistor.end[0], esd_resistor.end[1]+0.75)
    d += elm.Line().up(0.5).at(esd_resistor.end)
    d += elm.Diode().down(1).fill(True).label('TVS').at(esd_diode_pos)
    d += elm.Ground().at((esd_diode_pos[0], esd_diode_pos[1]-1))
    
    # Add test point
    d += elm.Dot().at(esd_resistor.end)
    d += elm.Label().label('TP1').at((esd_resistor.end[0], esd_resistor.end[1]-0.3))
    
    # Create dictionary of pin locations
    pins = {
        'vdd': tmr_top,
        'out': (esd_resistor.end[0], esd_resistor.end[1]),
        'gnd': tmr_bottom
    }
    
    return tmr, pins

def draw_instrumentation_amp(d: schemdraw.Drawing, tmr_pins: Dict[str, Tuple[float, float]]) -> Tuple[elm.Element, Dict[str, Tuple[float, float]]]:
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
    d += elm.Line().down(0.75).at(pins['in-'])
    d += elm.Ground()
    
    # Connect ground to reference pin
    d += elm.Line().down(0.5).at(pins['ref'])
    d += elm.Ground()
    
    return in_amp, pins

def draw_power_supply_decoupling(d: schemdraw.Drawing, in_amp_pins: Dict[str, Tuple[float, float]]) -> None:
    """
    Draw power supply decoupling for instrumentation amplifier.
    
    Args:
        d: The schemdraw Drawing object
        in_amp_pins: Dictionary of instrumentation amplifier pin locations
    """
    # Connect +5V to VS+
    vs_plus_pin = in_amp_pins['vs+']
    d += elm.Line().up(0.5).at(vs_plus_pin)
    d += elm.Label().label('+5V').at((vs_plus_pin[0], vs_plus_pin[1] + 0.5)).color('red')
    
    # Add decoupling capacitor for +5V
    d += elm.Line().right(0.75).at((vs_plus_pin[0], vs_plus_pin[1] + 0.5))
    d += elm.Capacitor().down(1).label('100nF').at((vs_plus_pin[0] + 0.75, vs_plus_pin[1] + 0.5))
    d += elm.Line().right(0.5).at((vs_plus_pin[0] + 0.75, vs_plus_pin[1] + 0.5))
    d += elm.Capacitor().down(1).label('10μF').at((vs_plus_pin[0] + 1.25, vs_plus_pin[1] + 0.5))
    d += elm.Ground().at((vs_plus_pin[0] + 0.75, vs_plus_pin[1] - 0.5))
    d += elm.Ground().at((vs_plus_pin[0] + 1.25, vs_plus_pin[1] - 0.5))
    
    # Connect -5V to VS-
    vs_minus_pin = in_amp_pins['vs-']
    d += elm.Line().down(0.5).at(vs_minus_pin)
    d += elm.Label().label('-5V').at((vs_minus_pin[0], vs_minus_pin[1] - 0.5)).color('blue')
    
    # Add decoupling capacitor for -5V
    d += elm.Line().right(0.75).at((vs_minus_pin[0], vs_minus_pin[1] - 0.5))
    d += elm.Capacitor().up(1).label('100nF').at((vs_minus_pin[0] + 0.75, vs_minus_pin[1] - 0.5))
    d += elm.Line().right(0.5).at((vs_minus_pin[0] + 0.75, vs_minus_pin[1] - 0.5))
    d += elm.Capacitor().up(1).label('10μF').at((vs_minus_pin[0] + 1.25, vs_minus_pin[1] - 0.5))
    d += elm.Ground().at((vs_minus_pin[0] + 0.75, vs_minus_pin[1] - 0.5))
    d += elm.Ground().at((vs_minus_pin[0] + 1.25, vs_minus_pin[1] - 0.5))

def draw_reference_connections(d: schemdraw.Drawing, in_amp_pins: Dict[str, Tuple[float, float]]) -> None:
    """
    Draw reference connections for the instrumentation amplifier.
    
    Args:
        d: The schemdraw Drawing object
        in_amp_pins: Dictionary of instrumentation amplifier pin locations
    """
    # REF pin is already connected to ground in draw_instrumentation_amp
    pass

def draw_gain_stage(d: schemdraw.Drawing, in_amp_pins: Dict[str, Tuple[float, float]]) -> None:
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
    rg1_extend = (rg1_pin[0] - 0.75, rg1_pin[1] - 0.5)
    d += elm.Line().down(0.5).left(0.75).at(rg1_pin)
    
    # Draw a line from RG2 down and left
    rg2_extend = (rg2_pin[0] + 0.75, rg2_pin[1] - 0.5)
    d += elm.Line().down(0.5).right(0.75).at(rg2_pin)
    
    # Connect with gain resistor
    # Adjust if positions are not aligned
    if rg1_extend[1] != rg2_extend[1]:
        # Align them
        rg1_extend = (rg1_extend[0], (rg1_extend[1] + rg2_extend[1]) / 2)
        rg2_extend = (rg2_extend[0], (rg1_extend[1] + rg2_extend[1]) / 2)
    
    # Draw resistor between extended points
    d += elm.Resistor().right().at(rg1_extend).to(rg2_extend).label('4.99kΩ\n0.1%')
    
    # Add gain formula note
    d += elm.Label().label('Gain = 1 + (49.4kΩ / 4.99kΩ) = 10.9').at(
        ((rg1_extend[0] + rg2_extend[0]) / 2, rg1_extend[1] - 0.5)
    ).color('blue')

def draw_output_stage(d: schemdraw.Drawing, in_amp_pins: Dict[str, Tuple[float, float]]) -> None:
    """
    Draw output connections for instrumentation amplifier.
    
    Args:
        d: The schemdraw Drawing object
        in_amp_pins: Dictionary of instrumentation amplifier pin locations
    """
    # Add output connection and test point
    out_pin = in_amp_pins['out']
    out_extend = (out_pin[0] + 1.5, out_pin[1])
    d += elm.Line().right(1.5).at(out_pin)
    d += elm.Dot().at(out_extend)
    d += elm.Label().label('TP2').at((out_extend[0], out_extend[1] - 0.3))
    
    # Add output label
    d += elm.Label().label('To Stage 2\nLow-Pass Filter').at(
        (out_extend[0] + 0.5, out_extend[1])
    )
    
    # Add design note
    d += elm.Label().label(
        'NOTES:\n'
        '1. AD8220 configured for single-ended operation\n'
        '2. Input protection provided by 100Ω + TVS diode\n'
        '3. Gain set to 10.9x for full-scale output\n'
        '4. Decoupling includes both 100nF (ceramic) and 10μF (tantalum) capacitors'
    ).at((out_extend[0] - 2, out_extend[1] - 2)).color('blue')

def draw_active_filter(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the Stage 2: Active Low-Pass Filter circuit
    
    Args:
        unit_size: Size of the drawing units
    """
    # Create a new drawing
    d = create_drawing(unit_size=unit_size)
    
    d += elm.Label().label('STAGE 2: ACTIVE LOW-PASS FILTER (20kHz CUTOFF)', loc='top')
    d += elm.Label().label('Sallen-Key 2nd Order Low-Pass Filter', loc='top').at((0, -0.5)).color('blue')
    d += elm.Label().label('All resistors 1% tolerance unless otherwise noted', loc='bottom').color('blue')
    
    # Draw input and first components
    input_point = (0, 0)
    d += elm.Dot().at(input_point)
    d += elm.Label().label('INPUT').at((input_point[0]-0.7, input_point[1]))
    
    # Add input protection components
    d += elm.Line().right(0.5).at(input_point)
    protect_pos = (input_point[0]+0.5, input_point[1])
    d += elm.Resistor().right(0.5).label('100Ω').at(protect_pos)
    tvs_pos = (protect_pos[0]+0.5, protect_pos[1])
    d += elm.Dot().at(tvs_pos)
    d += elm.Line().down(0.75).at(tvs_pos)
    d += elm.Zener().down(0.75).label('TVS').at((tvs_pos[0], tvs_pos[1]-0.75))
    d += elm.Ground().at((tvs_pos[0], tvs_pos[1]-1.5))
    
    # Junction for R6 and C2
    d += elm.Line().right(0.5).at(tvs_pos)
    junction1 = (tvs_pos[0]+0.5, tvs_pos[1])
    d += elm.Dot().at(junction1)
    
    # C2 capacitor
    c2 = d.add(elm.Capacitor().right(1.5).label('C2\n10nF\nX7R\n±5%').at(junction1))
    
    # R6 resistor
    r6 = d.add(elm.Resistor().down(2).label('R6\n10kΩ\n1%').at(junction1))
    
    # Junction after C2
    c2_right = c2.get_bbox()[2]
    junction2 = (c2_right, junction1[1])
    d += elm.Dot().at(junction2)
    
    # R7 resistor
    r7 = d.add(elm.Resistor().right(2).label('R7\n16.5kΩ\n0.1%').at(junction2))
    
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
    # V+ connection
    vs_pos = (opamp_pos[0], opamp_pos[1]+1.5)
    d += elm.Line().at(vs_pos).right(0.5)
    d += elm.Label().label('V+').at((vs_pos[0]-0.3, vs_pos[1]))
    d += elm.Line().up(0.5).at(vs_pos)
    d += elm.Label().label('+5V').at((vs_pos[0], vs_pos[1]+0.5)).color('red')
    
    # Decoupling capacitor for V+
    d += elm.Line().right(0.75).at(vs_pos)
    d += elm.Capacitor().down(1).label('100nF').at((vs_pos[0]+0.75, vs_pos[1]))
    d += elm.Ground().at((vs_pos[0]+0.75, vs_pos[1]-1))
    
    # V- connection
    vm_pos = (opamp_pos[0], opamp_pos[1]-1.5)
    d += elm.Line().at(vm_pos).right(0.5)
    d += elm.Label().label('V-').at((vm_pos[0]-0.3, vm_pos[1]))
    d += elm.Line().down(0.5).at(vm_pos)
    d += elm.Label().label('-5V').at((vm_pos[0], vm_pos[1]-0.5)).color('blue')
    
    # Decoupling capacitor for V-
    d += elm.Line().right(0.75).at(vm_pos)
    d += elm.Capacitor().up(1).label('100nF').at((vm_pos[0]+0.75, vm_pos[1]))
    d += elm.Ground().at((vm_pos[0]+0.75, vm_pos[1]+1))
    
    # Connect junction2 to OpAmp
    d += elm.Line().down(1).at(junction2)
    d += elm.Line().right(3.5).at((junction2[0], junction2[1]-1))
    
    # R8 resistor and connection to OpAmp
    r8_pos = (op_in2[0]-1, op_in2[1])
    r8 = d.add(elm.Resistor().left(2).label('R8\n10kΩ\n1%').at(r8_pos))
    
    # Connect R6 to R8
    r6_bottom = r6.get_bbox()[1]
    d += elm.Line().right(5).at((junction1[0], r6_bottom))
    d += elm.Dot().at((junction1[0]+5, r6_bottom))
    d += elm.Line().up(1).at((junction1[0]+5, r6_bottom))
    
    # C3 capacitor
    r8_left = r8.get_bbox()[0]
    c3_start = (r8_left-1, r8_pos[1])
    c3 = d.add(elm.Capacitor().down(2).label('C3\n100nF\nX7R\n±5%').at(c3_start))
    
    # Connect C3 to output
    c3_bottom = c3.get_bbox()[1]
    d += elm.Line().right(5).at((c3_start[0], c3_bottom))
    
    # Output connection
    d += elm.Line().right(1).at(op_out)
    output_point = (op_out[0]+1, op_out[1])
    d += elm.Dot().at(output_point)
    d += elm.Label().label('OUTPUT').at((output_point[0]+0.7, output_point[1]))
    
    # Add test point at output
    d += elm.Line().up(0.5).at(output_point)
    d += elm.Dot(open=True).at((output_point[0], output_point[1]+0.5))
    d += elm.Label().label('TP3').at((output_point[0], output_point[1]+0.7))
    
    # Add design notes
    note_pos = (junction1[0]+3, junction1[1]+3)
    d += elm.Label().label('NOTES:').at(note_pos).color('blue')
    d += elm.Label().label('1. Cutoff frequency = 20kHz').at((note_pos[0], note_pos[1]-0.5)).color('blue')
    d += elm.Label().label('2. Damping factor = 0.707 (Butterworth response)').at((note_pos[0], note_pos[1]-1)).color('blue')
    d += elm.Label().label('3. Input impedance > 10kΩ').at((note_pos[0], note_pos[1]-1.5)).color('blue')
    d += elm.Label().label('4. Use X7R capacitors for temperature stability').at((note_pos[0], note_pos[1]-2)).color('blue')
    
    # Save the drawing
    save_drawing(d, 'stage2_active_lowpass_filter')

def draw_level_shifter(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the Stage 3: Level Shifter circuit
    
    Args:
        unit_size: Size of the drawing units
    """
    # Create a new drawing
    d = create_drawing(unit_size=unit_size)
    
    d += elm.Label().label('STAGE 3: LEVEL SHIFTER (0-3.3V OUTPUT RANGE)', loc='top')
    d += elm.Label().label('Non-inverting Summing Amplifier with Level Shift', loc='top').at((0, -0.5)).color('blue')
    d += elm.Label().label('All resistors 0.1% tolerance unless otherwise noted', loc='bottom').color('blue')
    
    # Draw input
    input_point = (0, 0)
    d += elm.Dot().at(input_point)
    d += elm.Label().label('INPUT').at((input_point[0]-0.7, input_point[1]))
    
    # Add input protection components
    d += elm.Line().right(0.5).at(input_point)
    protect_pos = (input_point[0]+0.5, input_point[1])
    d += elm.Resistor().right(0.5).label('100Ω').at(protect_pos)
    tvs_pos = (protect_pos[0]+0.5, protect_pos[1])
    d += elm.Dot().at(tvs_pos)
    d += elm.Line().down(0.75).at(tvs_pos)
    d += elm.Zener().down(0.75).label('TVS').at((tvs_pos[0], tvs_pos[1]-0.75))
    d += elm.Ground().at((tvs_pos[0], tvs_pos[1]-1.5))
    
    # Save the drawing
    save_drawing(d, 'stage3_level_shifter')

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
            d += elm.Line().right(1).at((iso_left+3, iso_top+0.5-(i*0.5)))
            d += elm.Line().up(y-(iso_top+0.5-(i*0.5))).at((iso_left+4, iso_top+0.5-(i*0.5)))
            d += elm.Line().right(box_left-(iso_left+4)).at((iso_left+4, y))
            
            # Add pull-up resistor for each control line
            pull_up_pos = (x_start-1.5, y)
            d += elm.Resistor().up(0.75).label('4.7kΩ').at(pull_up_pos)
            d += elm.Label().label('+3.3V').at((pull_up_pos[0], pull_up_pos[1]+1)).color('orange')
            
            # Connect to multiplexer
            d += elm.Line().right(1).at((x_start-1, y))
            d += elm.Line().left(1).at((x_start, y))
            d += elm.Label().label(label).at((x_start-1.2, y))
        
        # Add channel inputs with protection
        y_chan_start = y_start - 5 * spacing
        for i in range(16):
            y = y_chan_start - i * spacing
            
            # Add protection circuit for each input
            d += elm.Line().left(3).at((x_start, y))
            
            # Series resistor
            d += elm.Resistor().left(1).label('100Ω').at((x_start-1, y))
            
            # TVS protection
            tvs_pos = (x_start-2, y)
            d += elm.Dot().at(tvs_pos)
            d += elm.Line().down(0.35).at(tvs_pos)
            d += elm.Zener().down(0.35).at((tvs_pos[0], tvs_pos[1]-0.35))
            d += elm.Ground().at((tvs_pos[0], tvs_pos[1]-0.7))
            
            # Input label
            d += elm.Label().label(f'CH{i}').at((x_start-4, y))
            d += elm.Label().label(f'A{i}').at((x_start+0.5, y))
        
        # Add enable input with pull-down
        y_en = y_chan_start - 17 * spacing
        d += elm.Line().left(3).at((x_start, y_en))
        
        # Pull-down resistor for enable
        pull_down_pos = (x_start-2, y_en)
        d += elm.Dot().at(pull_down_pos)
        d += elm.Resistor().down(0.75).label('10kΩ').at(pull_down_pos)
        d += elm.Ground().at((pull_down_pos[0], pull_down_pos[1]-0.75))
        
        d += elm.Label().label('EN').at((x_start-1.2, y_en))
        d += elm.Label().label('Active HIGH').at((x_start-3, y_en-0.5)).color('blue')
        
        # Add outputs (right side) with anti-aliasing filters
        x_end = box_right
        y_out_start = y_start - 5 * spacing
        
        for i in range(4):
            y = y_out_start - i * spacing
            
            # Add buffer op-amp for each output
            d += elm.Line().right(1).at((x_end, y))
            d += elm.Label().label(f'D{i}').at((x_end-0.5, y))
            
            # RC filter on output
            filter_pos = (x_end+1, y)
            d += elm.Dot().at(filter_pos)
            d += elm.Resistor().right(0.75).label('33Ω').at(filter_pos)
            
            # Capacitor to ground
            cap_pos = (x_end+1.75, y)
            d += elm.Dot().at(cap_pos)
            d += elm.Line().down(0.5).at(cap_pos)
            d += elm.Capacitor().down(0.5).label('100pF').at((cap_pos[0], cap_pos[1]-0.5))
            d += elm.Ground().at((cap_pos[0], cap_pos[1]-1))
            
            # Add buffer amplifier 
            buffer_pos = (x_end+3, filter_pos[1])
            buffer = d.add(elm.Opamp(leads=False).right().anchor('in1').at(buffer_pos))
            d += elm.Line().right(0.5).at(filter_pos)
            
            # Output label
            d += elm.Label().label(f'OUT{i}').at((buffer.out[0]+0.7, buffer.out[1]))
        
        # Add power connections with decoupling
        y_pwr = box_bottom
        x_pwr_start = box_left + 1
        pwr_spacing = 2
        
        # Add power labels with decoupling capacitors
        for i, (label, voltage) in enumerate([('GND', ''), ('AGND', ''), ('VDD', '+5V'), ('VREF', '+3.3V')]):
            x = x_pwr_start + i * pwr_spacing
            
            # Power connection line
            d += elm.Line().down(0.5).at((x, y_pwr))
            
            # Ground symbols
            if 'GND' in label:
                d += elm.Ground().at((x, y_pwr-0.5))
            
            # Label
            d += elm.Label().label(label).at((x, y_pwr-1))
            
            # Add voltage label for power pins
            if voltage:
                d += elm.Label().label(voltage).at((x, y_pwr-1.5)).color('red' if '+5V' in voltage else 'orange')
                
                # Add decoupling capacitors for VDD and VREF
                d += elm.Line().right(0.75).at((x, y_pwr-0.5))
                d += elm.Capacitor().down(1).label('100nF').at((x+0.75, y_pwr-0.5))
                d += elm.Ground().at((x+0.75, y_pwr-1.5))
                
                # Add bulk capacitor
                d += elm.Line().left(0.75).at((x, y_pwr-0.5))
                d += elm.Capacitor(polar=True).down(1).label('10μF').at((x-0.75, y_pwr-0.5))
                d += elm.Ground().at((x-0.75, y_pwr-1.5))
        
        # Add channel selection truth table
        table_x = box_right + 3
        table_y = box_top - 1
        table_width = 5
        table_height = 6
        
        # Draw table outline
        d += elm.Rect(w=table_width, h=table_height).at((table_x, table_y-table_height))
        
        # Draw table header
        d += elm.Line().right(table_width).at((table_x, table_y-1))
        
        # Draw vertical lines for columns
        for i in range(5):
            col_x = table_x + i
            d += elm.Line().down(table_height).at((col_x, table_y))
        
        # Add table title
        d += elm.Label().label('CHANNEL SELECT TRUTH TABLE').at((table_x+table_width/2, table_y-0.5)).color('blue')
        
        # Add column headers
        d += elm.Label().label('S3').at((table_x+0.5, table_y-1.5))
        d += elm.Label().label('S2').at((table_x+1.5, table_y-1.5))
        d += elm.Label().label('S1').at((table_x+2.5, table_y-1.5))
        d += elm.Label().label('S0').at((table_x+3.5, table_y-1.5))
        d += elm.Label().label('CH').at((table_x+4.5, table_y-1.5))
        
        # Add a few example rows
        examples = [
            ('0', '0', '0', '0', '0'),
            ('0', '0', '0', '1', '1'),
            ('0', '0', '1', '0', '2'),
            ('0', '0', '1', '1', '3'),
            ('1', '1', '1', '1', '15')
        ]
        
        for i, (s3, s2, s1, s0, ch) in enumerate(examples):
            row_y = table_y - 2 - i*0.75
            d += elm.Label().label(s3).at((table_x+0.5, row_y))
            d += elm.Label().label(s2).at((table_x+1.5, row_y))
            d += elm.Label().label(s1).at((table_x+2.5, row_y))
            d += elm.Label().label(s0).at((table_x+3.5, row_y))
            d += elm.Label().label(ch).at((table_x+4.5, row_y))
        
        # Add design notes
        note_x = box_left
        note_y = box_bottom - 3
        d += elm.Label().label('DESIGN NOTES:').at((note_x, note_y)).color('blue')
        d += elm.Label().label('1. Digital isolation protects MCU from analog noise').at((note_x, note_y-0.5)).color('blue')
        d += elm.Label().label('2. All analog inputs protected with 100Ω + TVS').at((note_x, note_y-1)).color('blue')
        d += elm.Label().label('3. Anti-aliasing filters on outputs (33Ω + 100pF)').at((note_x, note_y-1.5)).color('blue')
        d += elm.Label().label('4. Bypass capacitors must be placed close to IC').at((note_x, note_y-2)).color('blue')
        
        d.save('schematics/multiplexer_circuit.png')

def draw_adc(unit_size: float = DEFAULT_UNIT_SIZE) -> None:
    """
    Draw the ADC Interface Circuit
    
    Args:
        unit_size: Size of the drawing units
    """
    with schemdraw.Drawing() as d:
        d.config(unit=unit_size)
        d += elm.Label().label('ADC INTERFACE CIRCUIT', loc='top')
        d += elm.Label().label('ADS8688 16-bit, 8-Channel Precision ADC (500kSPS)', loc='top').at((0, -0.5)).color('blue')
        
        # Main box for ADS8688
        box = d.add(elm.Rect(w=8, h=10).label('ADS8688 16-bit, 8-Channel ADC', 'top'))
        
        # Get box corners
        box_left = box.get_bbox()[0]
        box_bottom = box.get_bbox()[1]
        box_right = box.get_bbox()[2]
        box_top = box.get_bbox()[3]
        box_center = (box_left + box_right) / 2, (box_top + box_bottom) / 2
        
        # Add analog inputs on the left side
        num_analog_inputs = 8
        y_spacing = box.get_bbox()[3] / (num_analog_inputs + 1)
        
        # Define a helper function to draw the input filter for each channel
        def draw_input_filter(d, x_start, y, channel):
            # Draw input line from left
            d += elm.Line().left(4).at((x_start, y))
            
            # Add label for connector
            d += elm.Label().label(f'J{channel+1}').at((x_start-4.3, y))
            
            # Add filter components - RC filter
            # Series resistors
            d += elm.Resistor().right(1).label('33Ω').at((x_start-4, y))
            d += elm.Resistor().right(1).label('33Ω').at((x_start-3, y))
            
            # Add ESD protection
            d += elm.Line().down(0.75).at((x_start-2.5, y))
            d += elm.Zener().down(0.75).label('TVS').at((x_start-2.5, y-0.75))
            d += elm.Ground().at((x_start-2.5, y-1.5))
            
            # Capacitor to GND
            d += elm.Line().down(0.75).at((x_start-1.5, y))
            d += elm.Capacitor().down(0.75).label('100nF').at((x_start-1.5, y-0.75))
            d += elm.Ground().at((x_start-1.5, y-1.5))
            
            # Secondary RC filter (anti-aliasing)
            d += elm.Resistor().right(1).label('100Ω').at((x_start-2, y))
            d += elm.Line().down(0.75).at((x_start-0.5, y))
            d += elm.Capacitor().down(0.75).label('10nF').at((x_start-0.5, y-0.75))
            d += elm.Ground().at((x_start-0.5, y-1.5))
            
            # Return input point
            return (x_start, y)
        
        # Draw the 8 input channels
        analog_inputs = []
        for i in range(num_analog_inputs):
            y_pos = box_top - (i + 1) * y_spacing
            input_point = draw_input_filter(d, box_left, y_pos, i)
            d += elm.Label().label(f'AIN{i}').at((box_left+0.5, y_pos))
            analog_inputs.append(input_point)
        
        # Add digital interface on the right side
        # SPI interface
        spi_start_y = box_top - 1
        
        # SCLK
        d += elm.Line().right(3).at((box_right, spi_start_y))
        sclk_point = (box_right+3, spi_start_y)
        d += elm.Label().label('SCLK').at((box_right+3.5, spi_start_y))
        
        # MOSI (DIN)
        d += elm.Line().right(3).at((box_right, spi_start_y-1))
        din_point = (box_right+3, spi_start_y-1)
        d += elm.Label().label('DIN').at((box_right+3.5, spi_start_y-1))
        
        # MISO (DOUT)
        d += elm.Line().right(3).at((box_right, spi_start_y-2))
        dout_point = (box_right+3, spi_start_y-2)
        d += elm.Label().label('DOUT').at((box_right+3.5, spi_start_y-2))
        
        # CS
        d += elm.Line().right(3).at((box_right, spi_start_y-3))
        cs_point = (box_right+3, spi_start_y-3)
        d += elm.Label().label('CS').at((box_right+3.5, spi_start_y-3))
        
        # Digital isolator for SPI
        iso_box = d.add(elm.Rect(w=2, h=5).label('Digital\nIsolator\nADUM1401', 'top').at((box_right+5, spi_start_y-2.5)))
        
        # Connect isolator to SPI lines
        d += elm.Line().right(2).at(sclk_point)
        d += elm.Line().right(2).at(din_point)
        d += elm.Line().right(2).at(dout_point)
        d += elm.Line().right(2).at(cs_point)
        
        # Add MCU connections from isolator
        spi_mcu_x = iso_box.get_bbox()[2] + 2
        
        # SCLK to MCU
        d += elm.Line().right(2).at((iso_box.get_bbox()[2], spi_start_y))
        d += elm.Dot().at((spi_mcu_x, spi_start_y))
        d += elm.Label().label('To MCU SCLK').at((spi_mcu_x+1, spi_start_y))
        
        # MOSI to MCU
        d += elm.Line().right(2).at((iso_box.get_bbox()[2], spi_start_y-1))
        d += elm.Dot().at((spi_mcu_x, spi_start_y-1))
        d += elm.Label().label('To MCU MOSI').at((spi_mcu_x+1, spi_start_y-1))
        
        # MISO to MCU
        d += elm.Line().right(2).at((iso_box.get_bbox()[2], spi_start_y-2))
        d += elm.Dot().at((spi_mcu_x, spi_start_y-2))
        d += elm.Label().label('To MCU MISO').at((spi_mcu_x+1, spi_start_y-2))
        
        # CS to MCU
        d += elm.Line().right(2).at((iso_box.get_bbox()[2], spi_start_y-3))
        d += elm.Dot().at((spi_mcu_x, spi_start_y-3))
        d += elm.Label().label('To MCU GPIO').at((spi_mcu_x+1, spi_start_y-3))
        
        # Pull-up resistors for SPI
        for i, y in enumerate([spi_start_y, spi_start_y-1, spi_start_y-3]):
            d += elm.Line().up(1).at((box_right+3, y))
            d += elm.Resistor().up(1).label('4.7kΩ').at((box_right+3, y+1))
            d += elm.Line().up(0.5).at((box_right+3, y+2))
            d += elm.Label().label('+3.3V').at((box_right+3, y+2.5)).color('red')
        
        # Add clock source
        clk_y = box_bottom + 1
        d += elm.Line().down(2).at((box_center[0], box_bottom))
        
        # Add crystal oscillator
        xtal_x = box_center[0]
        xtal_y = box_bottom - 3
        d += elm.Crystal().right(2).at((xtal_x-1, xtal_y))
        
        # Add capacitors to GND
        d += elm.Line().down(1).at((xtal_x-1, xtal_y))
        d += elm.Capacitor().down(1).label('22pF').at((xtal_x-1, xtal_y-1))
        d += elm.Ground().at((xtal_x-1, xtal_y-2))
        
        d += elm.Line().down(1).at((xtal_x+1, xtal_y))
        d += elm.Capacitor().down(1).label('22pF').at((xtal_x+1, xtal_y-1))
        d += elm.Ground().at((xtal_x+1, xtal_y-2))
        
        d += elm.Label().label('16MHz').at((xtal_x, xtal_y-0.5))
        
        # Add reference voltage section
        ref_x = box_left - 6
        ref_y = box_bottom + 3
        d += elm.Rect(w=2, h=1.5).label('REF5025\n2.5V Reference').at((ref_x, ref_y))
        
        # Connect reference to ADC
        d += elm.Line().right(6).at((ref_x+2, ref_y+0.75))
        d += elm.Label().label('REFP').at((ref_x+4, ref_y+0.75))
        d += elm.Line().right(6).at((ref_x+2, ref_y+0.25))
        d += elm.Label().label('REFN').at((ref_x+4, ref_y+0.25))
        
        # Add decoupling for reference
        d += elm.Line().down(1.5).at((ref_x+1, ref_y))
        d += elm.Capacitor().right(1.5).label('10μF').at((ref_x+1, ref_y-1.5))
        d += elm.Capacitor().right(1.5).label('0.1μF').at((ref_x+1, ref_y-2.5))
        d += elm.Ground().at((ref_x+2.5, ref_y-2.5))
        
        # Power supplies
        # Analog supply
        avdd_x = box_center[0] - 2
        avdd_y = box_top + 2
        d += elm.Line().up(2).at((avdd_x, box_top))
        d += elm.Label().label('AVDD').at((avdd_x-1, avdd_y))
        
        # Add power filtering
        d += elm.Inductor().right(2).label('Ferrite\n100MHz').at((avdd_x, avdd_y))
        d += elm.Line().right(0.5).at((avdd_x+2, avdd_y))
        filter_point = (avdd_x+2.5, avdd_y)
        d += elm.Dot().at(filter_point)
        d += elm.Line().down(1).at(filter_point)
        d += elm.Capacitor().down(1).label('10μF').at((filter_point[0], filter_point[1]-1))
        d += elm.Ground().at((filter_point[0], filter_point[1]-2))
        
        d += elm.Line().right(1).at(filter_point)
        d += elm.Capacitor().down(1).label('0.1μF').at((filter_point[0]+1, filter_point[1]))
        d += elm.Ground().at((filter_point[0]+1, filter_point[1]-1))
        
        d += elm.Line().left(6).at((avdd_x, avdd_y))
        d += elm.Label().label('+5V').at((avdd_x-6, avdd_y)).color('red')
        
        # Digital supply
        dvdd_x = box_center[0] + 2
        dvdd_y = box_top + 2
        d += elm.Line().up(2).at((dvdd_x, box_top))
        d += elm.Label().label('DVDD').at((dvdd_x+1, dvdd_y))
        
        # Digital supply filtering
        d += elm.Line().right(2).at((dvdd_x, dvdd_y))
        d += elm.Capacitor().down(1).label('0.1μF').at((dvdd_x+2, dvdd_y))
        d += elm.Ground().at((dvdd_x+2, dvdd_y-1))
        
        d += elm.Line().right(1).at((dvdd_x, dvdd_y))
        d += elm.Capacitor().down(1).label('10μF').at((dvdd_x+1, dvdd_y))
        d += elm.Ground().at((dvdd_x+1, dvdd_y-1))
        
        d += elm.Line().right(3).at((dvdd_x, dvdd_y))
        d += elm.Label().label('+3.3V').at((dvdd_x+3, dvdd_y)).color('red')
        
        # Add technical notes to the schematic
        note_x = ref_x - 6
        note_y = box_top + 4
        d += elm.Label().label('ADC INTERFACE TECHNICAL NOTES:').at((note_x, note_y)).color('blue')
        d += elm.Label().label('1. Dual precision anti-aliasing filters on all inputs').at((note_x, note_y-0.5)).color('blue')
        d += elm.Label().label('2. ESD protection with TVS diodes on all analog inputs').at((note_x, note_y-1)).color('blue')
        d += elm.Label().label('3. Digital isolation for SPI interface to prevent noise coupling').at((note_x, note_y-1.5)).color('blue')
        d += elm.Label().label('4. Separate analog and digital power supplies with proper filtering').at((note_x, note_y-2)).color('blue')
        d += elm.Label().label('5. AVDD and AGND connected at single star point ground').at((note_x, note_y-2.5)).color('blue')
        
        d.save('schematics/adc_interface.png')

def main(unit_size: float = DEFAULT_UNIT_SIZE, 
         output_dir: str = OUTPUT_DIR,
         formats: List[str] = FILE_FORMATS) -> None:
    """
    Main function to draw all schematics
    
    Args:
        unit_size: Base unit size for all drawings
        output_dir: Directory to save output files
        formats: List of file formats to save (e.g., ['png', 'svg'])
    """
    try:
        print(f"Generating TMR Sensor Array schematics with unit size {unit_size}...")
        
        # Ensure output directory exists
        ensure_output_directory(output_dir)
        
        # Use a dictionary to map circuit names to their drawing functions
        # This makes it easy to add or remove circuits
        drawing_functions = {
            'instrumentation_amplifier': draw_instrumentation_amplifier,
            'active_filter': draw_active_filter,
            'level_shifter': draw_level_shifter,
            'multiplexer': draw_multiplexer,
            'adc': draw_adc
        }
        
        # Draw all circuits
        for name, func in drawing_functions.items():
            print(f"Drawing {name.replace('_', ' ').title()}...")
            try:
                # Pass unit size to each drawing function
                func(unit_size=unit_size)
            except Exception as e:
                print(f"Error drawing {name}: {str(e)}")
        
        print(f"Schematics have been generated and saved to the '{output_dir}' directory.")
        
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TMR Sensor Array Schematic Generator')
    parser.add_argument('--unit-size', type=float, default=DEFAULT_UNIT_SIZE,
                       help=f'Set the unit size for all drawings (default: {DEFAULT_UNIT_SIZE})')
    parser.add_argument('--output-dir', type=str, default=OUTPUT_DIR,
                       help=f'Set the output directory (default: {OUTPUT_DIR})')
    parser.add_argument('--format', nargs='+', default=FILE_FORMATS,
                       help=f'Set the output format(s) (default: {FILE_FORMATS})')
    
    args = parser.parse_args()
    
    main(
        unit_size=args.unit_size,
        output_dir=args.output_dir,
        formats=args.format
    )
