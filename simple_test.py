#!/usr/bin/env python3
"""
A simple test of the schemdraw library to understand its API
"""

import schemdraw
import schemdraw.elements as elm
import os

# Create output directory if it doesn't exist
if not os.path.exists('schematics'):
    os.makedirs('schematics')

with schemdraw.Drawing() as d:
    d.config(unit=2)
    d += elm.Label().label('SIMPLE TEST CIRCUIT', loc='top')
    
    # Draw resistor
    d += elm.Resistor().label('100Ω')
    
    # Draw capacitor
    d += elm.Capacitor().right().label('10nF')
    
    # Add ground
    d += elm.Ground()
    
    d.save('schematics/simple_test.png')

print("Simple test drawing created in schematics/simple_test.png") 