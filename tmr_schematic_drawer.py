#!/usr/bin/env python3
"""
TMR Sensor Array - Analog Front-End Circuit Schematic Implementation
This script recreates the TMR sensor analog front-end circuit diagrams using the SchemaDraw library.
"""

import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt
import os

# Create output directory if it doesn't exist
if not os.path.exists('schematics'):
    os.makedirs('schematics')

def draw_instrumentation_amplifier():
    """
    Draw the Stage 1: Instrumentation Amplifier circuit with TMR2305 sensor
    """
    with schemdraw.Drawing() as d:
        d.config(unit=2.5)
        d += elm.Label().label('STAGE 1: INSTRUMENTATION AMPLIFIER', loc='top')
        d += elm.Label().label('All resistors 0.1% tolerance unless otherwise noted', loc='bottom').color('blue')
        
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
        d += elm.Line().down(0.5).at((tmr_bottom[0], tmr_bottom[1]))
        d += elm.Ground().at((tmr_bottom[0], tmr_bottom[1]-0.5))
        
        # Input protection for TMR output - Add series resistor and TVS
        d += elm.Line().right(0.5).at((tmr_right[0]+0.5, tmr_right[1]))
        protect_pos = (tmr_right[0]+1, tmr_right[1])
        d += elm.Resistor().right(0.5).label('100Ω').at(protect_pos)
        tvs_pos = (protect_pos[0]+0.5, protect_pos[1])
        d += elm.Dot().at(tvs_pos)
        d += elm.Line().down(0.75).at(tvs_pos)
        d += elm.Zener().down(0.75).label('TVS').at((tvs_pos[0], tvs_pos[1]-0.75))
        d += elm.Ground().at((tvs_pos[0], tvs_pos[1]-1.5))
        
        # Connect OUT to R1/R2 junction
        d += elm.Line().right(1).at(tvs_pos)
        junction1 = (tvs_pos[0]+1, tvs_pos[1])
        d += elm.Dot().at(junction1)
        
        # R1 resistor
        r1 = d.add(elm.Resistor().down(1.5).label('R1\n499Ω\n0.1%').at(junction1))
        
        # R2 resistor
        r2 = d.add(elm.Resistor().right(2).label('R2\n10kΩ\n0.1%').at(junction1))
        
        # Connect R1 to VDD
        r1_bottom = r1.get_bbox()[1]
        d += elm.Line().right(1.5).at((junction1[0], r1_bottom))
        d += elm.Line().up(1.5).at((junction1[0]+1.5, r1_bottom))
        d += elm.Line().left(2).at((junction1[0]+1.5, r1_bottom+1.5))
        d += elm.Dot().at((junction1[0]-0.5, r1_bottom+1.5))
        
        # AD8220 opamp position
        ad8220_pos = (r2.get_bbox()[2]+1.5, junction1[1]-1)
        ad8220 = d.add(elm.Opamp(leads=True).at(ad8220_pos))
        
        # Get opamp terminals
        op_in1 = ad8220.anchors['in1']
        op_in2 = ad8220.anchors['in2']
        op_out = ad8220.anchors['out']
        
        # Connect to opamp inputs
        d += elm.Line().left(1.5).at(op_in1)
        d += elm.Dot().at((op_in1[0]-1.5, op_in1[1]))
        
        # Line from junction1 to AD8220 input
        d += elm.Line().down(2).at(junction1)
        d += elm.Line().right(3.5).at((junction1[0], junction1[1]-2))
        d += elm.Dot().at((junction1[0]+3.5, junction1[1]-2))
        
        # C1 capacitor
        c1 = d.add(elm.Capacitor().down(1).label('C1\n100pF\nC0G/NP0').at((junction1[0]+3.5, junction1[1]-0.5)))
        
        # Connect AD8220 inverting input
        d += elm.Line().left(1).at(op_in2)
        d += elm.Dot().at((op_in2[0]-1, op_in2[1]))
        
        # Connect GND to inverting input through R3
        d += elm.Line().down(1.5).at((tmr_bottom[0]+0.5, tmr_bottom[1]))
        gnd_line = (tmr_bottom[0]+0.5, tmr_bottom[1]-1.5)
        d += elm.Line().right(6.5).at(gnd_line)
        d += elm.Ground().at((gnd_line[0], gnd_line[1]-0.25))
        
        # R3 resistor
        r3_pos = (op_in2[0]-1, op_in2[1])
        r3 = d.add(elm.Resistor().down(1.5).label('R3\n10kΩ\n0.1%').at(r3_pos))
        
        # V+ and V- power connections with annotations
        vs_pos = (ad8220_pos[0]-1, ad8220_pos[1]-2.5)
        d += elm.Line().at(vs_pos).right(0.5)
        d += elm.Label().label('V+').at((vs_pos[0]-0.1, vs_pos[1]))
        d += elm.Label().label('4').at((vs_pos[0]+0.3, vs_pos[1]))
        d += elm.Line().right(0.5).at(vs_pos)
        d += elm.Line().up(0.5).at((vs_pos[0]+0.5, vs_pos[1]))
        d += elm.Label().label('+5V').at((vs_pos[0]+0.5, vs_pos[1]+0.5)).color('red')
        
        # Decoupling capacitor for V+
        d += elm.Line().right(0.75).at((vs_pos[0]+0.5, vs_pos[1]))
        d += elm.Capacitor().down(1).label('100nF').at((vs_pos[0]+1.25, vs_pos[1]))
        d += elm.Ground().at((vs_pos[0]+1.25, vs_pos[1]-1))
        
        # Bulk decoupling
        d += elm.Line().right(1.5).at((vs_pos[0]+0.5, vs_pos[1]))
        d += elm.Capacitor(polar=True).down(1).label('10μF').at((vs_pos[0]+2, vs_pos[1]))
        d += elm.Ground().at((vs_pos[0]+2, vs_pos[1]-1))
        
        vm_pos = (ad8220_pos[0]-1, ad8220_pos[1]-3.5)
        d += elm.Line().at(vm_pos).right(0.5)
        d += elm.Label().label('V-').at((vm_pos[0]-0.1, vm_pos[1]))
        d += elm.Label().label('5').at((vm_pos[0]+0.3, vm_pos[1]))
        d += elm.Line().right(0.5).at(vm_pos)
        d += elm.Line().down(0.5).at((vm_pos[0]+0.5, vm_pos[1]))
        d += elm.Label().label('-5V').at((vm_pos[0]+0.5, vm_pos[1]-0.5)).color('blue')
        
        # Decoupling capacitor for V-
        d += elm.Line().right(0.75).at((vm_pos[0]+0.5, vm_pos[1]))
        d += elm.Capacitor().up(1).label('100nF').at((vm_pos[0]+1.25, vm_pos[1]))
        d += elm.Ground().at((vm_pos[0]+1.25, vm_pos[1]+1))
        
        # Add pin numbers to AD8220
        d += elm.Label().label('2').at((op_in1[0]-0.2, op_in1[1]))
        d += elm.Label().label('3').at((op_in2[0]-0.2, op_in2[1]))
        d += elm.Label().label('6').at((op_out[0]-0.6, op_out[1]))
        
        # Connect pin 1 (REF) properly - previously open
        ref_pin_pos = (op_in2[0]-0.2, op_in2[1]-0.7)
        d += elm.Label().label('1 (REF)').at(ref_pin_pos)
        d += elm.Line().right(0.5).at((ref_pin_pos[0]+0.5, ref_pin_pos[1]-0.1))
        d += elm.Line().down(0.5).at((ref_pin_pos[0]+1, ref_pin_pos[1]-0.1))
        d += elm.Ground().at((ref_pin_pos[0]+1, ref_pin_pos[1]-0.6))
        
        # Connect pin 7 (RG) properly - previously open
        rg_pin_pos = (op_out[0]-1.3, op_out[1]-0.7)
        d += elm.Label().label('7 (RG)').at(rg_pin_pos)
        # RG connected to a precision resistor for gain setting
        d += elm.Line().down(0.5).at((rg_pin_pos[0]+0.5, rg_pin_pos[1]))
        d += elm.Resistor().right(1).label('Rgain\n499Ω\n0.1%').at((rg_pin_pos[0]+0.5, rg_pin_pos[1]-0.5))
        d += elm.Line().up(0.5).at((rg_pin_pos[0]+1.5, rg_pin_pos[1]-0.5))
        
        d += elm.Label().label('8').at((op_out[0], op_out[1]+0.3))
        
        # Output connections and R4/R5
        d += elm.Line().right(1).at(op_out)
        d += elm.Label().label('OUTPUT').at((op_out[0]+0.6, op_out[1]+0.3))
        
        # Add test point at output
        d += elm.Dot().at((op_out[0]+1, op_out[1]))
        d += elm.Line().up(0.5).at((op_out[0]+1, op_out[1]))
        d += elm.Dot(open=True).at((op_out[0]+1, op_out[1]+0.5))
        d += elm.Label().label('TP1').at((op_out[0]+1, op_out[1]+0.7))
        
        # R4 and R5 resistors to GND
        r4_pos = (op_out[0]+1, op_out[1]-1.5)
        r4 = d.add(elm.Resistor().right(1.5).label('R4\n10kΩ\n0.1%').at(r4_pos))
        r5 = d.add(elm.Resistor().right(1.5).label('R5\n10kΩ\n0.1%').at((r4.get_bbox()[2], r4_pos[1])))
        
        # Connect R5 to GND
        r5_right = r5.get_bbox()[2]
        d += elm.Line().down(1).at((r5_right, r4_pos[1]))
        d += elm.Ground().at((r5_right, r4_pos[1]-1))
        
        # Connect R4 start to AD8220 pin 5
        d += elm.Line().up(0.5).at(r4_pos)
        d += elm.Line().left(4).at((r4_pos[0], r4_pos[1]+0.5))
        
        # Add AD8220 label
        d += elm.Label().label('AD8220').at((ad8220_pos[0], ad8220_pos[1]-2))
        d += elm.Label().label('Precision Instrumentation Amplifier').at((ad8220_pos[0], ad8220_pos[1]-1.5)).color('blue')
        
        # Add notes
        note_pos = (junction1[0]+5, junction1[1]+3)
        d += elm.Label().label('NOTES:').at(note_pos).color('blue')
        d += elm.Label().label('1. Gain = 1 + (49.4kΩ/Rgain) ≈ 100').at((note_pos[0], note_pos[1]-0.5)).color('blue')
        d += elm.Label().label('2. Bypass capacitors must be placed close to IC').at((note_pos[0], note_pos[1]-1)).color('blue')
        d += elm.Label().label('3. Use star grounding topology').at((note_pos[0], note_pos[1]-1.5)).color('blue')
        
        d.save('schematics/stage1_instrumentation_amplifier.png')

def draw_active_filter():
    """
    Draw the Stage 2: Active Low-Pass Filter circuit
    """
    with schemdraw.Drawing() as d:
        d.config(unit=2.5)
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
        d += elm.Label().label('TP2').at((output_point[0], output_point[1]+0.7))
        
        # Feedback connection
        d += elm.Line().up(1).at(output_point)
        d += elm.Line().left(5).at((output_point[0], output_point[1]+1))
        d += elm.Line().down(1).at((output_point[0]-5, output_point[1]+1))
        
        # Add filter characteristics notes
        note_pos = (r7.get_bbox()[0], r7.get_bbox()[1]+4)
        d += elm.Label().label('FILTER CHARACTERISTICS:').at(note_pos).color('blue')
        d += elm.Label().label('1. Cutoff frequency: 20kHz (-3dB)').at((note_pos[0], note_pos[1]-0.5)).color('blue')
        d += elm.Label().label('2. Filter type: 2nd order Butterworth (Q=0.707)').at((note_pos[0], note_pos[1]-1)).color('blue')
        d += elm.Label().label('3. Passband gain: 1 (unity)').at((note_pos[0], note_pos[1]-1.5)).color('blue')
        d += elm.Label().label('4. Phase delay at 10kHz: 45°').at((note_pos[0], note_pos[1]-2)).color('blue')
        
        d.save('schematics/stage2_active_lowpass_filter.png')

def draw_level_shifter():
    """
    Draw the Stage 3: Level Shifter circuit
    """
    with schemdraw.Drawing() as d:
        d.config(unit=2.5)
        d += elm.Label().label('STAGE 3: LEVEL SHIFTER (0-3.3V OUTPUT RANGE)', loc='top')
        d += elm.Label().label('Non-inverting Summing Amplifier with Level Shift', loc='top').at((0, -0.5)).color('blue')
        d += elm.Label().label('All resistors 0.1% tolerance unless otherwise noted', loc='bottom').color('blue')
        
        # Draw input
        input_point = (0, 0)
        d += elm.Dot().at(input_point)
        d += elm.Label().label('INPUT').at((input_point[0]-0.7, input_point[1]))
        
        # Add input protection
        d += elm.Line().right(0.5).at(input_point)
        protect_pos = (input_point[0]+0.5, input_point[1])
        d += elm.Resistor().right(0.5).label('100Ω').at(protect_pos)
        tvs_pos = (protect_pos[0]+0.5, protect_pos[1])
        d += elm.Dot().at(tvs_pos)
        d += elm.Line().down(0.75).at(tvs_pos)
        d += elm.Zener().down(0.75).label('TVS').at((tvs_pos[0], tvs_pos[1]-0.75))
        d += elm.Ground().at((tvs_pos[0], tvs_pos[1]-1.5))
        
        # Continue with main circuit after protection
        d += elm.Line().right(0.5).at(tvs_pos)
        input_protected = (tvs_pos[0]+0.5, tvs_pos[1])
        
        # R9 resistor
        r9 = d.add(elm.Resistor().right(2).label('R9\n10kΩ\n0.1%').at(input_protected))
        
        # R10 resistor
        r9_right = r9.get_bbox()[2]
        r10 = d.add(elm.Resistor().right(2).label('R10\n10kΩ\n0.1%').at((r9_right, input_protected[1])))
        
        # OpAmp
        r10_right = r10.get_bbox()[2]
        opamp_pos = (r10_right+1.5, input_protected[1]-1)
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
        
        # Connect R10 to OpAmp
        d += elm.Line().down(1).at((r10_right, input_protected[1]))
        
        # Proper 3.3V reference with voltage divider
        vref_start = (op_in2[0]-3, op_in2[1]-1.5)
        
        # 3.3V reference chip
        vref_rect = d.add(elm.Rect(w=2, h=1.5).at(vref_start))
        d += elm.Label().label('REF3330\n3.3V Reference').at((vref_start[0]+1, vref_start[1]+0.75))
        
        # Connect reference to power
        d += elm.Line().up(0.5).at((vref_start[0]+0.5, vref_start[1]+1.5))
        d += elm.Label().label('+5V').at((vref_start[0]+0.5, vref_start[1]+2)).color('red')
        
        # Connect reference output to op-amp
        d += elm.Line().right(0.5).at((vref_start[0]+2, vref_start[1]+0.75))
        d += elm.Label().label('3.3V').at((vref_start[0]+2.5, vref_start[1]+0.75)).color('orange')
        
        # Add decoupling capacitor to reference
        d += elm.Line().down(1).at((vref_start[0]+1.5, vref_start[1]))
        d += elm.Capacitor().right(1).label('1μF').at((vref_start[0]+1.5, vref_start[1]-1))
        d += elm.Ground().at((vref_start[0]+2.5, vref_start[1]-1))
        
        # Connect reference to non-inverting input through buffer resistor
        d += elm.Line().right(1).at((vref_start[0]+2.5, vref_start[1]+0.75))
        d += elm.Resistor().right(1.5).label('1kΩ\n0.1%').at((vref_start[0]+3.5, vref_start[1]+0.75))
        
        # 3.3V to non-inverting input
        vcc_point = (op_in2[0], op_in2[1]-0.5)
        d += elm.Line().up(1.25).at((vref_start[0]+5, vref_start[1]+0.75))
        d += elm.Line().right(1).at((vref_start[0]+5, vref_start[1]+2))
        d += elm.Line().down(2.5).at((vref_start[0]+6, vref_start[1]+2))
        d += elm.Line().right(0.5).at(vcc_point)
        d += elm.Label().label('3.3V REF').at((vcc_point[0]-0.7, vcc_point[1])).color('orange')
        
        # R11 resistor to GND
        r11_pos = (op_in2[0]+1, op_in2[1]-1.5)
        r11 = d.add(elm.Resistor().down(2).label('R11\n10kΩ\n0.1%').at(r11_pos))
        
        # GND connection
        r11_bottom = r11.get_bbox()[1]
        d += elm.Ground().at((r11_pos[0], r11_bottom-0.25))
        d += elm.Label().label('GND').at((r11_pos[0], r11_bottom-0.75))
        
        # C4 capacitor
        c4_start = (r11_pos[0]+1, r11_pos[1]-0.5)
        c4 = d.add(elm.Capacitor().left(2).label('C4\n100nF\nX7R\n±5%').at(c4_start))
        
        # Output connection
        d += elm.Line().right(1).at(op_out)
        output_point = (op_out[0]+1, op_out[1])
        d += elm.Dot().at(output_point)
        d += elm.Label().label('OUTPUT').at((output_point[0]+0.7, output_point[1]))
        
        # Add test point at output
        d += elm.Line().up(0.5).at(output_point)
        d += elm.Dot(open=True).at((output_point[0], output_point[1]+0.5))
        d += elm.Label().label('TP3').at((output_point[0], output_point[1]+0.7))
        
        # Add EMI filter at output
        d += elm.Line().right(1).at(output_point)
        emi_pos = (output_point[0]+1, output_point[1])
        d += elm.Dot().at(emi_pos)
        d += elm.Resistor().right(1).label('33Ω').at(emi_pos)
        filter_pos = (emi_pos[0]+1, emi_pos[1])
        d += elm.Dot().at(filter_pos)
        d += elm.Line().down(0.75).at(filter_pos)
        d += elm.Capacitor().down(0.75).label('100nF').at((filter_pos[0], filter_pos[1]-0.75))
        d += elm.Ground().at((filter_pos[0], filter_pos[1]-1.5))
        d += elm.Line().right(0.5).at(filter_pos)
        d += elm.Label().label('TO ADC').at((filter_pos[0]+0.7, filter_pos[1])).color('green')
        
        # Connect capacitor to output
        c4_left = c4.get_bbox()[0]
        d += elm.Line().up(2.5).at((c4_left, c4_start[1]))
        d += elm.Line().right(4).at((c4_left, c4_start[1]+2.5))
        
        # Add level shifter notes
        note_pos = (vref_start[0], vref_start[1]+3.5)
        d += elm.Label().label('LEVEL SHIFTER CHARACTERISTICS:').at(note_pos).color('blue')
        d += elm.Label().label('1. Input range: ±2.5V bipolar').at((note_pos[0], note_pos[1]-0.5)).color('blue')
        d += elm.Label().label('2. Output range: 0-3.3V unipolar').at((note_pos[0], note_pos[1]-1)).color('blue')
        d += elm.Label().label('3. Precision matched resistors (0.1%) for accurate shifting').at((note_pos[0], note_pos[1]-1.5)).color('blue')
        d += elm.Label().label('4. 3.3V reference: ±0.05% initial accuracy, 10ppm/°C').at((note_pos[0], note_pos[1]-2)).color('blue')
        
        d.save('schematics/stage3_level_shifter.png')

def draw_multiplexer():
    """
    Draw the 16-Channel Multiplexing Circuit
    """
    with schemdraw.Drawing() as d:
        d.config(unit=2.5)
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

def draw_adc():
    """
    Draw the ADC Interface Circuit
    """
    with schemdraw.Drawing() as d:
        d.config(unit=2.5)
        d += elm.Label().label('ADC INTERFACE CIRCUIT', loc='top')
        d += elm.Label().label('ADS8688 16-bit, 8-Channel Precision ADC (500kSPS)', loc='top').at((0, -0.5)).color('blue')
        
        # Main box for ADS8688
        box = d.add(elm.Rect(w=8, h=10).label('ADS8688 16-bit, 8-Channel ADC', 'top'))
        
        # Get box corners
        box_left = box.get_bbox()[0]
        box_right = box.get_bbox()[2]
        box_top = box.get_bbox()[3]
        box_bottom = box.get_bbox()[1]
        
        # Section labels
        d += elm.Label().label('Analog Inputs').at((box_left+2, box_top-1))
        d += elm.Label().label('Digital Interface').at((box_right-2, box_top-1))
        d += elm.Label().label('Reference').at((box_left+2, box_top-6))
        d += elm.Label().label('Clock').at((box_right-2, box_top-6))
        
        # Anti-aliasing filter circuit template (reused for each input)
        def draw_input_filter(d, x_start, y, channel):
            # Draw input line from left
            d += elm.Line().left(4).at((x_start, y))
            
            # Add label for connector
            d += elm.Label().label(f'J{channel+1}').at((x_start-4.3, y))
            
            # Add filter components - RC filter
            # Series resistors
            d += elm.Resistor().right(1).label('33Ω').at((x_start-4, y))
            
            # First capacitor to ground
            cap1_pos = (x_start-3, y)
            d += elm.Dot().at(cap1_pos)
            d += elm.Line().down(0.75).at(cap1_pos)
            d += elm.Capacitor().down(0.75).label('100pF').at((cap1_pos[0], cap1_pos[1]-0.75))
            d += elm.Ground().at((cap1_pos[0], cap1_pos[1]-1.5))
            
            # Second resistor
            d += elm.Resistor().right(1).label('33Ω').at(cap1_pos)
            
            # Second capacitor to ground  
            cap2_pos = (x_start-2, y)
            d += elm.Dot().at(cap2_pos)
            d += elm.Line().down(0.75).at(cap2_pos)
            d += elm.Capacitor().down(0.75).label('100pF').at((cap2_pos[0], cap2_pos[1]-0.75))
            d += elm.Ground().at((cap2_pos[0], cap2_pos[1]-1.5))
            
            # Add ESD protection
            d += elm.Line().right(0.75).at(cap2_pos)
            diode_pos = (x_start-1.25, y)
            d += elm.Dot().at(diode_pos)
            
            # Protection diodes
            d += elm.Line().up(0.75).at(diode_pos)
            d += elm.Diode().up().label('ESD').at((diode_pos[0], diode_pos[1]+0.75))
            d += elm.Label().label('+3.3V').at((diode_pos[0], diode_pos[1]+1.5)).color('orange')
            
            d += elm.Line().down(0.75).at(diode_pos)
            d += elm.Diode().down(0.75).flip().label('ESD').at((diode_pos[0], diode_pos[1]-0.75))
            d += elm.Ground().at((diode_pos[0], diode_pos[1]-1.5))
            
            # Final connection to ADC
            d += elm.Line().right(1.25).at(diode_pos)
            
            # Add channel label
            d += elm.Label().label(f'AIN{channel}').at((x_start+0.8, y))
            d += elm.Label().label(f'IN{channel}').at((x_start-1.3, y))
        
        # Analog inputs (left side)
        x_start = box_left
        y_start = box_top - 2
        spacing = 0.5
        
        # Add analog inputs with anti-aliasing filters
        for i in range(8):
            y = y_start - i * spacing
            draw_input_filter(d, x_start, y, i)
        
        # SPI interface to MCU with isolation
        # Add digital isolator
        iso_right = box_right + 5
        iso_top = box_top - 2
        iso_box = d.add(elm.Rect(w=3, h=3).at((iso_right, iso_top)))
        d += elm.Label().label('ISO7741\nDigital Isolator').at((iso_right+1.5, iso_top+1.5))
        
        # Add microcontroller side
        d += elm.Label().label('To\nMCU').at((iso_right+4.5, iso_top+1.5)).color('green')
        
        # Digital interface (right side) with pull-up resistors
        x_end = box_right
        y_end_start = y_start
        
        for i, (label, pin) in enumerate([
            ('SCLK', 'SPI_CLK'), 
            ('SDI', 'SPI_MOSI'), 
            ('SDO', 'SPI_MISO'), 
            ('CS', 'SPI_CS')
        ]):
            y = y_end_start - i * spacing
            
            # Connect from ADC to isolator with pull-up resistors
            d += elm.Line().right(1).at((x_end, y))
            # Pull-up resistor
            pull_up_pos = (x_end+1, y)
            d += elm.Dot().at(pull_up_pos)
            d += elm.Line().up(0.75).at(pull_up_pos)
            d += elm.Resistor().up(0.75).label('4.7kΩ').at((pull_up_pos[0], pull_up_pos[1]+0.75))
            d += elm.Label().label('+3.3V').at((pull_up_pos[0], pull_up_pos[1]+1.5)).color('orange')
            
            # Connection to isolator
            d += elm.Line().right(2).at(pull_up_pos)
            
            # Connect to isolator
            iso_pin_y = iso_top+0.5-(i*0.5)
            d += elm.Line().up(iso_pin_y - y).at((x_end+3, y))
            d += elm.Line().right(1).at((x_end+3, iso_pin_y))
            
            # Labels
            d += elm.Label().label(label).at((x_end-0.8, y))
            d += elm.Label().label(pin).at((iso_right+4, iso_pin_y))
        
        # Add RST and BUSY with digital isolation
        y_rst = y_end_start - 5 * spacing
        d += elm.Line().right(1).at((x_end, y_rst))
        pull_up_rst = (x_end+1, y_rst)
        d += elm.Dot().at(pull_up_rst)
        d += elm.Line().up(0.75).at(pull_up_rst)
        d += elm.Resistor().up(0.75).label('4.7kΩ').at((pull_up_rst[0], pull_up_rst[1]+0.75))
        d += elm.Line().right(2).at(pull_up_rst)
        
        # Connect to isolator
        iso_rst_y = iso_top+0.5-(4*0.5)
        d += elm.Line().up(iso_rst_y - y_rst).at((x_end+3, y_rst))
        d += elm.Line().right(1).at((x_end+3, iso_rst_y))
        
        d += elm.Label().label('RST').at((x_end-0.8, y_rst))
        d += elm.Label().label('RESET').at((iso_right+4, iso_rst_y))
        
        y_busy = y_end_start - 7 * spacing
        d += elm.Line().right(3).at((x_end, y_busy))
        
        # Connect to isolator
        iso_busy_y = iso_top+0.5-(5*0.5)
        d += elm.Line().up(iso_busy_y - y_busy).at((x_end+3, y_busy))
        d += elm.Line().right(1).at((x_end+3, iso_busy_y))
        
        d += elm.Label().label('BUSY').at((x_end-0.8, y_busy))
        d += elm.Label().label('BUSY').at((iso_right+4, iso_busy_y))
        
        # Reference circuit (more complete)
        # Add external voltage reference
        y_ref_start = box_top - 7
        ref_left = box_left - 6
        ref_rect = d.add(elm.Rect(w=2.5, h=2).at((ref_left, y_ref_start-1)))
        d += elm.Label().label('ADR4550\nPrecision 5V\nReference').at((ref_left+1.25, y_ref_start))
        
        # Connect reference to power
        d += elm.Line().up(0.5).at((ref_left+0.5, y_ref_start+1))
        d += elm.Label().label('+12V').at((ref_left+0.5, y_ref_start+1.5)).color('red')
        
        # Reference output
        d += elm.Line().right(0.5).at((ref_left+2.5, y_ref_start))
        d += elm.Label().label('5.000V\n±0.02%').at((ref_left+3, y_ref_start)).color('red')
        
        # Capacitor for noise filtering
        d += elm.Line().right(0.5).at((ref_left+3, y_ref_start))
        cap_ref = (ref_left+3.5, y_ref_start)
        d += elm.Dot().at(cap_ref)
        d += elm.Line().down(1).at(cap_ref)
        d += elm.Capacitor().down(1).label('10μF').at((cap_ref[0], cap_ref[1]-1))
        d += elm.Ground().at((cap_ref[0], cap_ref[1]-2))
        
        # Buffer op-amp
        d += elm.Line().right(0.5).at(cap_ref)
        # Op-amp for buffering
        buffer_pos = (ref_left+4.5, y_ref_start)
        buffer = d.add(elm.Opamp(leads=False).right().anchor('in1').at(buffer_pos))
        d += elm.Label().label('OPA2387').at((buffer_pos[0]+0.75, buffer_pos[1]-1))
        
        # Buffer output to REFIO
        d += elm.Line().right(1).at(buffer.out)
        d += elm.Resistor().right(1).label('10Ω').at((buffer.out[0]+1, buffer.out[1]))
        
        # Capacitor after resistor
        cap_buf = (buffer.out[0]+2, buffer.out[1])
        d += elm.Dot().at(cap_buf)
        d += elm.Line().down(1).at(cap_buf)
        d += elm.Capacitor().down(1).label('1μF').at((cap_buf[0], cap_buf[1]-1))
        d += elm.Ground().at((cap_buf[0], cap_buf[1]-2))
        
        # Connect to REFIO pin
        d += elm.Line().right(2).at(cap_buf)
        
        y_refio = y_ref_start
        d += elm.Line().left(0.5).at((x_start, y_refio))
        d += elm.Label().label('REFIO').at((x_start+0.8, y_refio))
        
        y_refgnd = y_ref_start - spacing
        d += elm.Line().left(0.5).at((x_start, y_refgnd))
        d += elm.Label().label('REFGND').at((x_start+0.9, y_refgnd))
        
        # Connect REFGND to ground
        d += elm.Line().left(2).at((x_start, y_refgnd))
        d += elm.Ground().at((x_start-2, y_refgnd))
        
        # Clock circuit with crystal
        # Add crystal oscillator circuit
        y_clk_start = y_ref_start
        osc_right = box_right + 5
        
        # Crystal component
        crystal_pos = (osc_right-3, y_clk_start)
        d += elm.Crystal().right().label('16MHz').at(crystal_pos)
        
        # Capacitors to ground
        c_xtal1 = (crystal_pos[0]-0.5, crystal_pos[1])
        d += elm.Line().down(0.75).at(c_xtal1)
        d += elm.Capacitor().down(0.75).label('18pF').at((c_xtal1[0], c_xtal1[1]-0.75))
        d += elm.Ground().at((c_xtal1[0], c_xtal1[1]-1.5))
        
        c_xtal2 = (crystal_pos[0]+1.5, crystal_pos[1])
        d += elm.Line().down(0.75).at(c_xtal2)
        d += elm.Capacitor().down(0.75).label('18pF').at((c_xtal2[0], c_xtal2[1]-0.75))
        d += elm.Ground().at((c_xtal2[0], c_xtal2[1]-1.5))
        
        # Connect to ADC
        d += elm.Line().left(1.5).at(c_xtal1)
        
        y_clkin = y_clk_start
        d += elm.Line().right(1).at((x_end, y_clkin))
        d += elm.Label().label('CLKIN').at((x_end-0.9, y_clkin))
        d += elm.Label().label('16MHz').at((x_end+1.5, y_clkin)).color('green')
        
        # Connect CLKSEL to ground
        y_clksel = y_clk_start - spacing
        d += elm.Line().right(1).at((x_end, y_clksel))
        d += elm.Line().down(0.75).at((x_end+1, y_clksel))
        d += elm.Ground().at((x_end+1, y_clksel-0.75))
        d += elm.Label().label('CLKSEL').at((x_end-0.9, y_clksel))
        d += elm.Label().label('GND (Internal Clock)').at((x_end+2, y_clksel)).color('blue')
        
        # Add power connections with proper decoupling network
        y_pwr = box_bottom
        x_pwr_start = box_left + 1.5
        pwr_spacing = 2.5
        
        # Power supply section
        for i, (label, voltage) in enumerate([('GND', 'GND'), ('AGND', 'AGND'), ('AVDD', '+5V')]):
            x = x_pwr_start + i * pwr_spacing
            
            # Power connection
            d += elm.Line().down(0.5).at((x, y_pwr))
            
            # Ground symbols
            if 'GND' in label:
                d += elm.Ground().at((x, y_pwr-0.5))
                
            # Digital and analog ground connection note
            if label == 'AGND':
                d += elm.Line().right(0.5).at((x, y_pwr-0.5))
                d += elm.Line().left(0.5).at((x, y_pwr-0.5))
                d += elm.Line().down(0.75).at((x, y_pwr-0.5))
                d += elm.Label().label('Connect at\nsingle point').at((x, y_pwr-1.5)).color('blue')
            
            # Label
            d += elm.Label().label(label).at((x, y_pwr-1))
            
            # Add voltage label and decoupling for AVDD
            if label == 'AVDD':
                d += elm.Label().label(voltage).at((x, y_pwr-1.5)).color('red')
                
                # Decoupling network
                # 100nF capacitor close to pin
                d += elm.Line().right(0.75).at((x, y_pwr-0.5))
                d += elm.Capacitor().down(1).label('100nF').at((x+0.75, y_pwr-0.5))
                d += elm.Ground().at((x+0.75, y_pwr-1.5))
                
                # 10μF bulk capacitor
                d += elm.Line().left(0.75).at((x, y_pwr-0.5))
                d += elm.Capacitor(polar=True).down(1).label('10μF').at((x-0.75, y_pwr-0.5))
                d += elm.Ground().at((x-0.75, y_pwr-1.5))
                
                # LC filter for power
                d += elm.Line().up(1).at((x, y_pwr-0.5))
                d += elm.Inductor().left(1.5).label('10μH').at((x, y_pwr-1.5))
                
                # Another bulk capacitor at power input
                cap_bulk = (x-1.5, y_pwr-1.5)
                d += elm.Dot().at(cap_bulk)
                d += elm.Line().down(1).at(cap_bulk)
                d += elm.Capacitor(polar=True).down(1).label('47μF').at((cap_bulk[0], cap_bulk[1]-1))
                d += elm.Ground().at((cap_bulk[0], cap_bulk[1]-2))
                
                # Power input from regulator
                d += elm.Line().left(1).at(cap_bulk)
                d += elm.Label().label('From LDO\nRegulator').at((cap_bulk[0]-1.5, cap_bulk[1])).color('red')
        
        # Add design notes
        note_x = box_left - 6
        note_y = box_bottom - 3
        d += elm.Label().label('ADC DESIGN NOTES:').at((note_x, note_y)).color('blue')
        d += elm.Label().label('1. Anti-aliasing filters on all inputs (2-pole, 125kHz cutoff)').at((note_x, note_y-0.5)).color('blue')
        d += elm.Label().label('2. Precision 5V reference with 0.02% accuracy (±1 LSB error)').at((note_x, note_y-1)).color('blue')
        d += elm.Label().label('3. Digital isolation to prevent ground loops and noise coupling').at((note_x, note_y-1.5)).color('blue')
        d += elm.Label().label('4. LC filter on power supply for reduced noise').at((note_x, note_y-2)).color('blue')
        d += elm.Label().label('5. AVDD and AGND connected at single star point ground').at((note_x, note_y-2.5)).color('blue')
        
        d.save('schematics/adc_interface.png')

def main():
    """
    Main function to draw all schematics
    """
    print("Generating TMR Sensor Array schematics...")
    
    # Draw all circuits
    draw_instrumentation_amplifier()
    draw_active_filter()
    draw_level_shifter()
    draw_multiplexer()
    draw_adc()
    
    print("Schematics have been generated and saved to the 'schematics' directory.")

if __name__ == "__main__":
    main() 