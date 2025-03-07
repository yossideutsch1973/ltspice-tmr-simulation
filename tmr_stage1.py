#!/usr/bin/env python3
"""
TMR Sensor Array - Stage 1 Instrumentation Amplifier
This script recreates the Stage 1 circuit diagram using the SchemaDraw library.
"""

import schemdraw
import schemdraw.elements as elm
import os

# Create output directory if it doesn't exist
if not os.path.exists('schematics'):
    os.makedirs('schematics')

# Draw the Stage 1: Instrumentation Amplifier circuit with TMR2305 sensor
with schemdraw.Drawing() as d:
    d.config(unit=2.5)
    d += elm.Label().label('STAGE 1: INSTRUMENTATION AMPLIFIER', loc='top')
    
    # Draw TMR2305 sensor as a rectangle
    tmr = d.add(elm.Rect(w=1.5, h=2.5).label('TMR2305', 'left'))
    # Get the coordinates of the rectangle corners
    tmr_top = (tmr.get_bbox()[0] + tmr.get_bbox()[2])/2, tmr.get_bbox()[3]
    tmr_right = tmr.get_bbox()[2], (tmr.get_bbox()[1] + tmr.get_bbox()[3])/2
    tmr_bottom = (tmr.get_bbox()[0] + tmr.get_bbox()[2])/2, tmr.get_bbox()[1]
    
    # Sensor pins
    d += elm.Line().right(0.5).at(tmr_right)
    d += elm.Label().label('OUT').at((tmr_right[0]+0.25, tmr_right[1]))
    d += elm.Line().right(0.5).at(tmr_top)
    d += elm.Label().label('VDD').at((tmr_top[0]+0.25, tmr_top[1]))
    d += elm.Line().right(0.5).at(tmr_bottom)
    d += elm.Label().label('GND').at((tmr_bottom[0]+0.25, tmr_bottom[1]))
    
    # Connect OUT to R1/R2 junction
    d += elm.Line().right(1.5).at((tmr_right[0]+0.5, tmr_right[1]))
    junction1 = (tmr_right[0]+2, tmr_right[1])
    d += elm.Dot().at(junction1)
    
    # R1 resistor
    r1 = d.add(elm.Resistor().down(1.5).label('R1\n499Ω').at(junction1))
    
    # R2 resistor
    r2 = d.add(elm.Resistor().right(2).label('R2\n10kΩ').at(junction1))
    
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
    c1 = d.add(elm.Capacitor().down(1).label('C1\n100pF').at((junction1[0]+3.5, junction1[1]-0.5)))
    
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
    r3 = d.add(elm.Resistor().down(1.5).label('R3\n10kΩ').at(r3_pos))
    
    # V+ and V- power connections
    d += elm.Line().at((ad8220_pos[0]-1, ad8220_pos[1]-2.5)).right(0.5)
    d += elm.Label().label('V+').at((ad8220_pos[0]-1.1, ad8220_pos[1]-2.5))
    d += elm.Label().label('4').at((ad8220_pos[0]-0.7, ad8220_pos[1]-2.5))
    
    d += elm.Line().at((ad8220_pos[0]-1, ad8220_pos[1]-3)).right(0.5)
    d += elm.Label().label('V-').at((ad8220_pos[0]-1.1, ad8220_pos[1]-3))
    d += elm.Label().label('5').at((ad8220_pos[0]-0.7, ad8220_pos[1]-3))
    
    # Add pin numbers to AD8220
    d += elm.Label().label('2').at((op_in1[0]-0.2, op_in1[1]))
    d += elm.Label().label('3').at((op_in2[0]-0.2, op_in2[1]))
    d += elm.Label().label('6').at((op_out[0]-0.6, op_out[1]))
    d += elm.Label().label('1').at((op_in2[0]-0.2, op_in2[1]-0.7))
    d += elm.Label().label('7').at((op_out[0]-1.3, op_out[1]-0.7))
    d += elm.Label().label('8').at((op_out[0], op_out[1]+0.3))
    
    # Output connections and R4/R5
    d += elm.Line().right(1).at(op_out)
    d += elm.Label().label('OUTPUT').at((op_out[0]+0.6, op_out[1]+0.3))
    
    # R4 and R5 resistors to GND
    r4_pos = (op_out[0]+1, op_out[1]-1.5)
    r4 = d.add(elm.Resistor().right(1.5).label('R4\n10kΩ').at(r4_pos))
    r5 = d.add(elm.Resistor().right(1.5).label('R5\n10kΩ').at((r4.get_bbox()[2], r4_pos[1])))
    
    # Connect R5 to GND
    r5_right = r5.get_bbox()[2]
    d += elm.Line().down(1).at((r5_right, r4_pos[1]))
    d += elm.Ground().at((r5_right, r4_pos[1]-1))
    
    # Connect R4 start to AD8220 pin 5
    d += elm.Line().up(0.5).at(r4_pos)
    d += elm.Line().left(4).at((r4_pos[0], r4_pos[1]+0.5))
    
    # Add AD8220 label
    d += elm.Label().label('AD8220').at((ad8220_pos[0], ad8220_pos[1]-2))
    
    d.save('schematics/stage1_instrumentation_amplifier.png')

print("Stage 1 schematic has been generated and saved to schematics/stage1_instrumentation_amplifier.png") 