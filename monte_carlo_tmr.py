#!/usr/bin/env python3
"""
Monte Carlo Simulation for TMR Sensor Array
This script runs Monte Carlo simulations on LTspice files for the TMR sensor array project.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from PyLTSpice import AscEditor, SimRunner, RawRead
from PyLTSpice.sim.tookit.montecarlo import Montecarlo

# Configuration
RESULTS_DIR = "./mc_results"
LT_CONFIG_FILE = "ltspice-config-optimization.asc"  # Change as needed
NUM_RUNS = 100  # Number of Monte Carlo runs
RUNS_PER_SIM = 10  # Runs per simulation batch
SENSOR_TOLERANCE = 0.05  # 5% tolerance for TMR sensors
HARMONIC_RATIO_TOLERANCE = 0.10  # 10% tolerance for harmonic ratio (A7/A1)
NOISE_LEVEL_TOLERANCE = 0.20  # 20% tolerance for noise level

def setup_directories():
    """Create necessary directories for simulation results."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print(f"Results will be stored in: {RESULTS_DIR}")

def run_monte_carlo_simulation(asc_file, num_runs=100, runs_per_sim=10):
    """
    Run Monte Carlo simulation on the TMR sensor array.
    
    Args:
        asc_file: Path to LTspice .asc file
        num_runs: Total number of Monte Carlo runs
        runs_per_sim: Runs per simulation batch
    
    Returns:
        Result data
    """
    print(f"Running Monte Carlo simulation on {asc_file} with {num_runs} runs")
    
    # Check if file exists
    if not os.path.exists(asc_file):
        print(f"Error: File {asc_file} not found")
        return None
    
    try:
        # Initialize AscEditor with the LTspice file
        ltspice_file = AscEditor(asc_file)
        
        # Initialize SimRunner with output folder
        runner = SimRunner(output_folder=RESULTS_DIR)
        
        # Create Montecarlo analysis object
        mc = Montecarlo(ltspice_file, runner)
        
        # Set tolerances for components and parameters
        mc.set_tolerance('R', SENSOR_TOLERANCE)  # Default resistor tolerance
        
        # Set parameter tolerances
        mc.set_parameter_deviation('A1', 0.2, HARMONIC_RATIO_TOLERANCE, 'uniform')  # Fundamental amplitude
        mc.set_parameter_deviation('A7', 1.0, HARMONIC_RATIO_TOLERANCE, 'uniform')  # 7th harmonic amplitude
        mc.set_parameter_deviation('noise_level', 0.01, NOISE_LEVEL_TOLERANCE, 'normal')  # Noise level
        
        # Prepare testbench for Monte Carlo simulation
        mc.prepare_testbench(num_runs=num_runs)
        
        # Save modified netlist
        modified_asc = os.path.join(RESULTS_DIR, f"{os.path.basename(asc_file).split('.')[0]}_mc.asc")
        mc.save_netlist(modified_asc)
        print(f"Modified netlist saved to: {modified_asc}")
        
        # Run simulations in batches
        print(f"Running {num_runs} simulations in batches of {runs_per_sim}...")
        mc.run_testbench(runs_per_sim=runs_per_sim)
        
        # Read and process log files
        print("Processing simulation results...")
        logs = mc.read_logfiles()
        
        # Export results to CSV
        csv_file = os.path.join(RESULTS_DIR, "monte_carlo_results.csv")
        logs.export_data(csv_file)
        print(f"Results exported to: {csv_file}")
        
        # Generate histograms for key measures
        for measure in logs.get_measure_names():
            print(f"Generating histogram for: {measure}")
            logs.plot_histogram(measure)
            plt.savefig(os.path.join(RESULTS_DIR, f"histogram_{measure}.png"))
            plt.close()
        
        # Clean up temporary files
        mc.cleanup_files()
        
        return logs
    
    except Exception as e:
        print(f"Error during Monte Carlo simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def analyze_results(logs):
    """
    Analyze Monte Carlo simulation results.
    
    Args:
        logs: Simulation log data
    """
    if logs is None:
        print("No data to analyze")
        return
    
    print("\n=== Monte Carlo Simulation Results ===")
    
    # Get measure names (metrics from simulation)
    measure_names = logs.get_measure_names()
    
    for measure in measure_names:
        values = logs.get_measure_values(measure)
        
        # Calculate statistics
        mean_val = np.mean(values)
        std_val = np.std(values)
        min_val = np.min(values)
        max_val = np.max(values)
        p99_val = np.percentile(values, 99)
        p01_val = np.percentile(values, 1)
        
        print(f"\nStatistics for {measure}:")
        print(f"  Mean: {mean_val:.6g}")
        print(f"  Std Dev: {std_val:.6g}")
        print(f"  Min: {min_val:.6g}")
        print(f"  Max: {max_val:.6g}")
        print(f"  99th percentile: {p99_val:.6g}")
        print(f"  1st percentile: {p01_val:.6g}")
        print(f"  Range (99% confidence): {p01_val:.6g} to {p99_val:.6g}")
        
        # Calculate equivalent bits of resolution if this is an error metric
        if "error" in measure.lower():
            if max_val - min_val > 0:
                resolution_bits = np.log2(360 / (max_val - min_val))
                print(f"  Equivalent Resolution: {resolution_bits:.2f} bits")

def main():
    """Main function to run TMR sensor array Monte Carlo simulation."""
    setup_directories()
    
    # Define the LTspice file to use
    ltspice_file = LT_CONFIG_FILE
    
    # Run the Monte Carlo simulation
    logs = run_monte_carlo_simulation(
        ltspice_file, 
        num_runs=NUM_RUNS,
        runs_per_sim=RUNS_PER_SIM
    )
    
    # Analyze results
    analyze_results(logs)
    
    print("\nMonte Carlo simulation completed!")
    print(f"Results are available in: {RESULTS_DIR}")

if __name__ == "__main__":
    main() 