#!/usr/bin/env python3
"""
Script to check available anchors in SchemaDraw 0.19 Opamp element
"""

import schemdraw
import schemdraw.elements as elm

print(f"SchemDraw version: {schemdraw.__version__}")
print("Checking opamp anchors...")

# Create an opamp
opamp = elm.Opamp()

# Print all available anchors
print("Available anchors in Opamp element:")
for anchor_name in opamp.anchors:
    print(f"  - {anchor_name}: {opamp.anchors[anchor_name]}")

print("\nChecking different opamp variants...")
opamp_leads = elm.Opamp(leads=True)
print("Opamp with leads, anchors:")
for anchor_name in opamp_leads.anchors:
    print(f"  - {anchor_name}: {opamp_leads.anchors[anchor_name]}") 