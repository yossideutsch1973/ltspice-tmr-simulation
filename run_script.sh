#!/bin/bash

# Unset PYTHONHOME and PYTHONPATH to prevent environment issues
unset PYTHONHOME
unset PYTHONPATH

# Use system Python directly
PYTHON_EXE="/usr/bin/python3.10"

# First check if schemdraw is installed
$PYTHON_EXE -c "
try:
    import schemdraw
    print(f'SchemDraw version: {schemdraw.__version__}')
except ImportError:
    print('Installing SchemDraw...')
    import sys
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'schemdraw', 'matplotlib'])
    import schemdraw
    print(f'SchemDraw installed, version: {schemdraw.__version__}')
"

# Run the specified script
if [ "$1" != "" ]; then
    echo "Running $1..."
    $PYTHON_EXE "$1"
else
    echo "Please specify a script to run, e.g. ./run_script.sh simple_test.py"
    exit 1
fi 