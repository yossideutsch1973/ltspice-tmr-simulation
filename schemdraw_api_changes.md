# SchemaDraw API Changes and Compatibility Notes

## Overview

This document outlines the key API changes between older versions of SchemaDraw and version 0.19 (current), and how we've adapted our code to maintain compatibility.

## Key API Changes

### Opamp Element Anchors

In SchemaDraw 0.19, the Opamp element has the following anchors:

- `out`: Output pin
- `in1`: Non-inverting input (positive)
- `in2`: Inverting input (negative)
- `center`: Center of the opamp
- `vd`: Positive power supply
- `vs`: Negative power supply
- `n1`, `n2`, `n1a`, `n2a`: Various points on the opamp body

**Important Change**: Older code using `anchor('in')` needs to be updated to use `anchor('in1')` or `anchor('in2')` depending on which input is needed.

### Element Positioning

SchemaDraw 0.19 may have slightly different default sizes and positions compared to older versions. When precise positioning is required:

- Use explicit coordinates with `.at((x, y))` 
- Use relative positioning with `.up()`, `.down()`, `.left()`, `.right()` with specific distances
- Adjust scaling with `.scale()` if needed

## Code Changes Made

The following changes were made to ensure compatibility with SchemaDraw 0.19:

1. Updated all instances of `anchor('in')` to `anchor('in1')` in the `tmr_schematic_drawer.py` file
2. Fixed the `draw_input_filter` function to properly receive the drawing object as a parameter
3. Created test scripts to verify anchor points and element behavior

## Testing

To verify SchemaDraw functionality:

```bash
./run_script.sh check_opamp_anchors.py  # Shows available anchors
./run_script.sh simple_test.py          # Basic circuit test
./run_script.sh opamp_test.py           # Tests opamp element
```

## Future Considerations

When updating or extending the schematic code:

1. Always check element anchor names before using them
2. Test positioning with simple examples before implementing complex circuits
3. Refer to the official SchemaDraw documentation: https://schemdraw.readthedocs.io/
4. For complex elements, print their attributes to verify available properties:
   ```python
   import schemdraw.elements as elm
   element = elm.ElementName()
   print(dir(element))
   print(element.anchors)
   ``` 