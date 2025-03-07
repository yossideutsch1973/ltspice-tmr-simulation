#!/usr/bin/env python3
"""
Testing opamp anchors in schemdraw
"""

import schemdraw
import schemdraw.elements as elm
import os

# Create output directory if it doesn't exist
if not os.path.exists('schematics'):
    os.makedirs('schematics')

with schemdraw.Drawing() as d:
    d.config(unit=2)
    d += elm.Label().label('OPAMP ANCHORS TEST', loc='top')
    
    # Create opamp
    opamp = d.add(elm.Opamp(leads=True))
    
    # Print anchors
    print("Opamp anchors:", opamp.anchors)
    
    # Try to access in1, in2, etc.
    try:
        print("in1:", opamp.in1)
    except Exception as e:
        print("Error accessing in1:", e)
    
    d.save('schematics/opamp_anchors.png')

print("Opamp anchors test drawing created in schematics/opamp_anchors.png") 