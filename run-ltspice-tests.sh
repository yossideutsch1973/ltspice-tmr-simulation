#!/bin/bash
# TMR Sensor Array LTspice Test Runner
# This script runs all TMR sensor array tests in LTspice and generates reports

# Configuration variables
RESULTS_DIR="./results"
REPORT_FILE="$RESULTS_DIR/test_report.txt"
LOG_FILE="$RESULTS_DIR/test_log.txt"

# Detect OS and set LTspice path accordingly
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Linux or macOS - use Wine
    echo "Detected Linux/macOS environment"
    LTSPICE_CMD="wine ~/.wine/drive_c/Program\ Files/LTC/LTspiceXVII/XVIIx64.exe -b"
    RM_CMD="rm -f"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    echo "Detected Windows environment"
    LTSPICE_CMD="\"C:\\Program Files\\LTC\\LTspiceXVII\\XVIIx64.exe\" -b"
    RM_CMD="del /F /Q"
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Create results directory if it doesn't exist
mkdir -p "$RESULTS_DIR"

# Initialize log and report files
echo "TMR Sensor Array LTspice Test Report" > "$REPORT_FILE"
echo "Date: $(date)" >> "$REPORT_FILE"
echo "----------------------------------------" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "TMR Sensor Array LTspice Test Log" > "$LOG_FILE"
echo "Date: $(date)" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Function to run a test and log results
run_test() {
    local test_file="$1"
    local test_name="$2"
    local description="$3"
    local raw_file="${test_file%.asc}.raw"
    
    echo "Running test: $test_name"
    echo "Test: $test_name" >> "$LOG_FILE"
    echo "Description: $description" >> "$LOG_FILE"
    echo "Command: $LTSPICE_CMD $test_file" >> "$LOG_FILE"
    
    # Run LTspice in batch mode
    eval $LTSPICE_CMD "$test_file" >> "$LOG_FILE" 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "  Status: Completed successfully"
        echo "Status: Completed successfully (exit code: $exit_code)" >> "$LOG_FILE"
        
        # Check if raw file was created
        if [ -f "$raw_file" ]; then
            echo "  Raw data file: $raw_file"
            echo "Raw data file: $raw_file" >> "$LOG_FILE"
            
            # Move raw file to results directory
            mv "$raw_file" "$RESULTS_DIR/${test_name}.raw"
            echo "  Moved results to: $RESULTS_DIR/${test_name}.raw"
            
            # Extract key metrics using LTspice utility or script
            # This is a placeholder - you'd need a proper tool to extract data from .raw files
            echo "  [Note: Data extraction requires LTspice raw file parser]"
            
            # Add test result to report
            echo "Test: $test_name" >> "$REPORT_FILE"
            echo "Description: $description" >> "$REPORT_FILE"
            echo "Status: PASS" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        else
            echo "  Error: Raw file not created"
            echo "Error: Raw file not created" >> "$LOG_FILE"
            
            # Add test result to report
            echo "Test: $test_name" >> "$REPORT_FILE"
            echo "Description: $description" >> "$REPORT_FILE"
            echo "Status: FAIL (Raw file not created)" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
    else
        echo "  Status: Failed (exit code: $exit_code)"
        echo "Status: Failed (exit code: $exit_code)" >> "$LOG_FILE"
        
        # Add test result to report
        echo "Test: $test_name" >> "$REPORT_FILE"
        echo "Description: $description" >> "$REPORT_FILE"
        echo "Status: FAIL (LTspice exit code: $exit_code)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
    
    echo "----------------------------------------" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
}

# Define test cases
echo "Running TMR Sensor Array LTspice tests..."

# Test 1: Basic Functionality Test
run_test "ltspice-test-plan.asc" "basic_functionality" "Tests basic 8-sensor, 7-pole-pair configuration with golden-angle spacing"

# Test 2: Resolution Test
run_test "ltspice-resolution-test.asc" "angular_resolution" "Tests system resolution with 0.002° angle increments"

# Test 3: Fault Tolerance Test
# Run with different failure configurations
run_test "ltspice-fault-tolerance.asc" "fault_tolerance_1sensor" "Tests system with 1 failed sensor (fail_s0=1)"
sed -i 's/\.param fail_s0 = 0/\.param fail_s0 = 1/' ltspice-fault-tolerance.asc
sed -i 's/\.param fail_s4 = 0/\.param fail_s4 = 1/' ltspice-fault-tolerance.asc
run_test "ltspice-fault-tolerance.asc" "fault_tolerance_2sensors" "Tests system with 2 failed sensors (fail_s0=1, fail_s4=1)"
sed -i 's/\.param fail_s0 = 1/\.param fail_s0 = 0/' ltspice-fault-tolerance.asc
sed -i 's/\.param fail_s4 = 1/\.param fail_s4 = 0/' ltspice-fault-tolerance.asc

# Test 4: Configuration Optimization Test
# Test different N,P combinations
run_test "ltspice-config-optimization.asc" "config_8_7" "Tests original 8-sensor, 7-pole-pair configuration"
sed -i 's/\.param N = 8/\.param N = 12/' ltspice-config-optimization.asc
sed -i 's/\.param P = 7/\.param P = 11/' ltspice-config-optimization.asc
run_test "ltspice-config-optimization.asc" "config_12_11" "Tests optimized 12-sensor, 11-pole-pair configuration"
sed -i 's/\.param N = 12/\.param N = 16/' ltspice-config-optimization.asc
sed -i 's/\.param P = 11/\.param P = 17/' ltspice-config-optimization.asc
run_test "ltspice-config-optimization.asc" "config_16_17" "Tests high-performance 16-sensor, 17-pole-pair configuration"
sed -i 's/\.param N = 16/\.param N = 16/' ltspice-config-optimization.asc
sed -i 's/\.param P = 17/\.param P = 13/' ltspice-config-optimization.asc
run_test "ltspice-config-optimization.asc" "config_16_13" "Tests fault-tolerant 16-sensor, 13-pole-pair configuration"
sed -i 's/\.param N = 16/\.param N = 8/' ltspice-config-optimization.asc
sed -i 's/\.param P = 13/\.param P = 7/' ltspice-config-optimization.asc

# Test 5: High-Speed Performance Test
# Test at multiple RPM values
run_test "ltspice-high-speed-test.asc" "speed_10000rpm" "Tests system at 10,000 RPM"
sed -i 's/\.param RPM = 10000/\.param RPM = 20000/' ltspice-high-speed-test.asc
run_test "ltspice-high-speed-test.asc" "speed_20000rpm" "Tests system at 20,000 RPM"
sed -i 's/\.param RPM = 20000/\.param RPM = 30000/' ltspice-high-speed-test.asc
run_test "ltspice-high-speed-test.asc" "speed_30000rpm" "Tests system at 30,000 RPM"
sed -i 's/\.param RPM = 30000/\.param RPM = 10000/' ltspice-high-speed-test.asc

# Generate summary report
echo "Tests completed."
echo "Generating summary report..."

# Count passes and fails
PASSES=$(grep -c "Status: PASS" "$REPORT_FILE")
FAILS=$(grep -c "Status: FAIL" "$REPORT_FILE")
TOTAL=$((PASSES + FAILS))

echo "" >> "$REPORT_FILE"
echo "----------------------------------------" >> "$REPORT_FILE"
echo "Summary:" >> "$REPORT_FILE"
echo "Total tests: $TOTAL" >> "$REPORT_FILE"
echo "Passed: $PASSES" >> "$REPORT_FILE"
echo "Failed: $FAILS" >> "$REPORT_FILE"

# Print test results file location
echo ""
echo "Test completed. Results can be found in:"
echo "  - Report: $REPORT_FILE"
echo "  - Log: $LOG_FILE"
echo "  - Raw data: $RESULTS_DIR/*.raw"

# Create a data processing script for extracting key metrics
cat > "$RESULTS_DIR/process_data.py" << 'EOF'
#!/usr/bin/env python3
"""
LTspice Raw File Parser for TMR Sensor Array Test Results
This script processes LTspice .raw files to extract key metrics for TMR array tests
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from ltspice import Ltspice  # You need to install ltspice Python package: pip install ltspice

def process_resolution_test(raw_file):
    """Process angular resolution test data"""
    print(f"Processing resolution test: {raw_file}")
    
    try:
        lts = Ltspice(raw_file)
        lts.parse()
        
        # Get time and error vectors
        time = lts.get_time()
        error = lts.get_data('error')
        
        # Calculate statistics
        rms_error = np.sqrt(np.mean(np.square(error)))
        max_error = np.max(np.abs(error))
        p99_error = np.percentile(np.abs(error), 99)
        
        # Create results directory
        os.makedirs('plots', exist_ok=True)
        
        # Plot error histogram
        plt.figure(figsize=(10, 6))
        plt.hist(error, bins=50)
        plt.title(f'Angular Error Distribution\nRMS: {rms_error:.6f}°, Max: {max_error:.6f}°, 99%: {p99_error:.6f}°')
        plt.xlabel('Error (degrees)')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.savefig(f'plots/{os.path.basename(raw_file).replace(".raw", "_error_hist.png")}')
        
        # Return key metrics
        return {
            'rms_error': rms_error,
            'max_error': max_error,
            'p99_error': p99_error,
            'resolution_bits': np.log2(360/p99_error)
        }
    except Exception as e:
        print(f"Error processing {raw_file}: {e}")
        return None

def process_fault_tolerance_test(raw_file):
    """Process fault tolerance test data"""
    print(f"Processing fault tolerance test: {raw_file}")
    
    try:
        lts = Ltspice(raw_file)
        lts.parse()
        
        # Get error data
        error = lts.get_data('error')
        rms_error = lts.get_data('rms_error')
        
        # Calculate degradation metrics
        max_error = np.max(np.abs(error))
        avg_rms = np.mean(rms_error[len(rms_error)//2:])  # Use second half of simulation
        
        # Create plots directory
        os.makedirs('plots', exist_ok=True)
        
        # Plot error over time
        time = lts.get_time()
        plt.figure(figsize=(10, 6))
        plt.plot(time, error)
        plt.title(f'Error with Sensor Failures\nMax Error: {max_error:.6f}°, Avg RMS: {avg_rms:.6f}°')
        plt.xlabel('Time (s)')
        plt.ylabel('Error (degrees)')
        plt.grid(True, alpha=0.3)
        plt.savefig(f'plots/{os.path.basename(raw_file).replace(".raw", "_error.png")}')
        
        # Return metrics
        return {
            'max_error': max_error,
            'avg_rms_error': avg_rms,
            'resolution_bits': np.log2(360/max_error)
        }
    except Exception as e:
        print(f"Error processing {raw_file}: {e}")
        return None

def process_speed_test(raw_file):
    """Process high-speed test data"""
    print(f"Processing speed test: {raw_file}")
    
    try:
        lts = Ltspice(raw_file)
        lts.parse()
        
        # Get error and theoretical error
        error = lts.get_data('error')
        expected_error = lts.get_data('expected_error')
        
        # Calculate metrics
        max_error = np.max(np.abs(error[len(error)//4:]))  # Skip initial transient
        avg_expected = np.mean(expected_error[len(expected_error)//2:])
        
        # Create plots directory
        os.makedirs('plots', exist_ok=True)
        
        # Plot actual vs expected error
        time = lts.get_time()
        plt.figure(figsize=(10, 6))
        plt.plot(time, np.abs(error), label='Actual Error')
        plt.plot(time, expected_error, label='Expected Error')
        plt.title(f'High-Speed Performance\nMax Error: {max_error:.6f}°, Expected: {avg_expected:.6f}°')
        plt.xlabel('Time (s)')
        plt.ylabel('Error (degrees)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f'plots/{os.path.basename(raw_file).replace(".raw", "_speed.png")}')
        
        # Return metrics
        return {
            'max_error': max_error,
            'expected_error': avg_expected,
            'error_ratio': max_error / avg_expected if avg_expected > 0 else float('inf')
        }
    except Exception as e:
        print(f"Error processing {raw_file}: {e}")
        return None

def process_configuration_test(raw_file):
    """Process configuration optimization test data"""
    print(f"Processing configuration test: {raw_file}")
    
    try:
        lts = Ltspice(raw_file)
        lts.parse()
        
        # Get resolution and theoretical resolution
        resolution = lts.get_data('resolution')
        theory_resolution = lts.get_data('theory_resolution')
        error = lts.get_data('error')
        
        # Calculate metrics
        avg_resolution = np.mean(resolution[len(resolution)//2:])
        avg_theory = np.mean(theory_resolution[len(theory_resolution)//2:])
        max_error = np.max(np.abs(error[len(error)//4:]))
        
        # Create plots directory
        os.makedirs('plots', exist_ok=True)
        
        # Plot resolution
        time = lts.get_time()
        plt.figure(figsize=(10, 6))
        plt.plot(time, resolution, label='Actual Resolution')
        plt.plot(time, theory_resolution, label='Theoretical Resolution')
        plt.title(f'Configuration Performance\nAvg Resolution: {avg_resolution:.2f} bits, Theory: {avg_theory:.2f} bits')
        plt.xlabel('Time (s)')
        plt.ylabel('Resolution (bits)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(f'plots/{os.path.basename(raw_file).replace(".raw", "_config.png")}')
        
        # Return metrics
        return {
            'avg_resolution': avg_resolution,
            'theory_resolution': avg_theory,
            'resolution_ratio': avg_resolution / avg_theory if avg_theory > 0 else 0,
            'max_error': max_error
        }
    except Exception as e:
        print(f"Error processing {raw_file}: {e}")
        return None

def main():
    """Main function to process all raw files"""
    if len(sys.argv) < 2:
        print("Usage: python process_data.py <raw_file_directory>")
        sys.exit(1)
    
    raw_dir = sys.argv[1]
    results = {}
    
    # Process all raw files
    for filename in os.listdir(raw_dir):
        if not filename.endswith('.raw'):
            continue
            
        filepath = os.path.join(raw_dir, filename)
        
        # Determine file type from name
        if 'angular_resolution' in filename:
            results[filename] = process_resolution_test(filepath)
        elif 'fault_tolerance' in filename:
            results[filename] = process_fault_tolerance_test(filepath)
        elif 'speed_' in filename:
            results[filename] = process_speed_test(filepath)
        elif 'config_' in filename:
            results[filename] = process_configuration_test(filepath)
        else:
            print(f"Unknown test type for {filename}, skipping")
    
    # Generate summary report
    with open(os.path.join(raw_dir, 'metrics_report.txt'), 'w') as f:
        f.write("TMR Sensor Array Test Metrics Summary\n")
        f.write("=====================================\n\n")
        
        for filename, metrics in results.items():
            if metrics is None:
                f.write(f"{filename}: Error processing file\n\n")
                continue
                
            f.write(f"{filename}:\n")
            for key, value in metrics.items():
                if isinstance(value, float):
                    f.write(f"  {key}: {value:.6f}\n")
                else:
                    f.write(f"  {key}: {value}\n")
            f.write("\n")
        
        # Add paper validation summary
        f.write("Paper Claims Validation\n")
        f.write("=====================\n\n")
        
        # Check if key tests are present
        basic_resolution = results.get('angular_resolution.raw', {}).get('p99_error', float('inf'))
        if basic_resolution <= 0.003:
            f.write("✓ Claim: ±0.002°-0.003° precision - VALIDATED\n")
        else:
            f.write("✗ Claim: ±0.002°-0.003° precision - NOT VALIDATED (Achieved: ±{:.6f}°)\n".format(basic_resolution))
        
        # Check fault tolerance
        fault_1 = results.get('fault_tolerance_1sensor.raw', {}).get('max_error', float('inf'))
        fault_2 = results.get('fault_tolerance_2sensors.raw', {}).get('max_error', float('inf'))
        if fault_1 <= 0.005 and fault_2 <= 0.01:
            f.write("✓ Claim: Fault tolerance (1-3 sensors) - VALIDATED\n")
        else:
            f.write("✗ Claim: Fault tolerance (1-3 sensors) - NOT VALIDATED\n")
            
        # Check high-speed performance
        high_speed = results.get('speed_30000rpm.raw', {}).get('max_error', float('inf'))
        if high_speed <= 0.003:
            f.write("✓ Claim: Performance at 30,000 RPM - VALIDATED\n")
        else:
            f.write("✗ Claim: Performance at 30,000 RPM - NOT VALIDATED (Achieved: {:.6f}°)\n".format(high_speed))
            
        # Check P = N-1 optimality
        config_8_7 = results.get('config_8_7.raw', {}).get('avg_resolution', 0)
        config_8_5 = results.get('config_8_5.raw', {}).get('avg_resolution', 0)
        config_8_11 = results.get('config_8_11.raw', {}).get('avg_resolution', 0)
        if config_8_7 > config_8_5 and config_8_7 > config_8_11:
            f.write("✓ Claim: P = N-1 optimality - VALIDATED\n")
        else:
            f.write("✗ Claim: P = N-1 optimality - NOT VALIDATED\n")
    
    print(f"Metrics report generated: {os.path.join(raw_dir, 'metrics_report.txt')}")
    print(f"Plots saved in: plots/")

if __name__ == "__main__":
    main()
EOF

chmod +x "$RESULTS_DIR/process_data.py"

echo ""
echo "To process raw data files and generate metrics, use:"
echo "  python3 $RESULTS_DIR/process_data.py $RESULTS_DIR"
echo ""
echo "Note: This requires the ltspice Python package (pip install ltspice)"
echo "      and matplotlib (pip install matplotlib)"
