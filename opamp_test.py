#!/usr/bin/env python3
"""
Testing opamp and element connections in schemdraw
"""

import schemdraw
import schemdraw.elements as elm
import os

# Create output directory if it doesn't exist
if not os.path.exists('schematics'):
    os.makedirs('schematics')

with schemdraw.Drawing() as d:
    d.config(unit=2)
    d += elm.Label().label('OPAMP TEST', loc='top')
    
    # Check what attributes are available on boxes and elements
    rect = d.add(elm.Rect(w=2, h=3).label('BOX'))
    print("Rect attributes:", dir(rect))
    
    # Create opamp
    opamp = d.add(elm.Opamp(leads=True))
    print("Opamp attributes:", dir(opamp))
    
    # Try to connect to opamp terminals
    d += elm.Resistor().at(opamp.in1).left()
    
    d.save('schematics/opamp_test.png')

print("Opamp test drawing created in schematics/opamp_test.png") 