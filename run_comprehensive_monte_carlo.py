#!/usr/bin/env python3
"""
Comprehensive Monte Carlo Simulation for TMR Sensor Array
This script runs extensive Monte Carlo simulations on the TMR sensor array using the Python model.
"""

import os
import sys
import time
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from multiprocessing import Pool, cpu_count
from ltspice_to_python import TMRSensorModel

# Configuration
OUTPUT_DIR = "./mc_comprehensive"
NUM_RUNS = 50  # Total Monte Carlo runs
ANGLE_STEPS = 360  # Steps for a full rotation
CONFIGS_TO_TEST = [
    {"name": "Standard", "sensors": 8, "pole_pairs": 7},
    {"name": "Medium", "sensors": 12, "pole_pairs": 11},
    {"name": "High", "sensors": 16, "pole_pairs": 17},
    {"name": "Fault-Tolerant", "sensors": 16, "pole_pairs": 13}
]
PARAM_TOLERANCES = {
    "A1": 0.1,        # 10% tolerance for fundamental amplitude
    "A7": 0.1,        # 10% tolerance for 7th harmonic amplitude
    "noise_level": 0.2  # 20% tolerance for noise level
}
FAULT_SCENARIOS = [
    {"name": "No Failures", "num_failures": 0},
    {"name": "One Failure", "num_failures": 1},
    {"name": "Two Failures", "num_failures": 2},
    {"name": "Three Failures", "num_failures": 3}
]

def setup_directories():
    """Create necessary directories for simulation results."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for config in CONFIGS_TO_TEST:
        config_dir = os.path.join(OUTPUT_DIR, f"{config['name']}_{config['sensors']}_{config['pole_pairs']}")
        os.makedirs(config_dir, exist_ok=True)
        
        # Create directories for fault scenarios
        for scenario in FAULT_SCENARIOS:
            scenario_dir = os.path.join(config_dir, f"failures_{scenario['num_failures']}")
            os.makedirs(scenario_dir, exist_ok=True)
    
    print(f"Results will be stored in: {OUTPUT_DIR}")

def run_single_monte_carlo(config_name, num_sensors, pole_pairs, num_failures, run_id, num_runs, steps):
    """Run a single Monte Carlo simulation with specified parameters."""
    # Create the model
    model = TMRSensorModel(num_sensors=num_sensors, pole_pairs=pole_pairs)
    
    # Apply failures if needed
    if num_failures > 0:
        # Randomly select sensors to fail
        available_sensors = list(range(num_sensors))
        failed_sensors = np.random.choice(available_sensors, num_failures, replace=False)
        
        # Mark failed sensors by setting their signals to 0 in signal generation
        original_generate_signals = model.generate_sensor_signals
        
        def generate_signals_with_failures(theta):
            signals = original_generate_signals(theta)
            for sensor_idx in failed_sensors:
                signals[f"S{sensor_idx}"] = 0
            return signals
        
        model.generate_sensor_signals = generate_signals_with_failures
    
    # Create parameter set with random variations
    run_params = {}
    for param, value in model.params.items():
        if param in PARAM_TOLERANCES:
            # Apply tolerance as a uniform distribution
            tolerance = PARAM_TOLERANCES[param]
            variation = np.random.uniform(-tolerance, tolerance)
            run_params[param] = value * (1 + variation)
        else:
            run_params[param] = value
    
    # Apply parameters
    model.params = run_params
    
    # Run a simulation for this parameter set
    sim_data = model.simulate_full_rotation(steps=steps)
    
    # Analyze results
    metrics = model.analyze_results(sim_data)
    
    # Return results with metadata
    return {
        "run_id": run_id,
        "config_name": config_name,
        "num_sensors": num_sensors,
        "pole_pairs": pole_pairs,
        "num_failures": num_failures,
        "parameters": run_params,
        "error_mean": metrics["error_mean"],
        "error_std": metrics["error_std"],
        "error_max": metrics["error_max"],
        "error_p99": metrics["error_p99"],
        "resolution_bits_max": metrics["resolution_bits_max"],
        "resolution_bits_p99": metrics["resolution_bits_p99"]
    }

def run_monte_carlo_batch(params):
    """Run a batch of Monte Carlo simulations with specified parameters."""
    config_name, num_sensors, pole_pairs, num_failures, batch_size, batch_id, steps = params
    results = []
    
    start_run_id = batch_id * batch_size
    end_run_id = start_run_id + batch_size
    
    for run_id in range(start_run_id, end_run_id):
        result = run_single_monte_carlo(
            config_name, num_sensors, pole_pairs, num_failures, run_id, batch_size, steps
        )
        results.append(result)
    
    return results

def run_parallel_monte_carlo(config_name, num_sensors, pole_pairs, num_failures, num_runs, steps, workers=None):
    """Run Monte Carlo simulations in parallel."""
    if workers is None:
        workers = cpu_count()
    
    print(f"Running {num_runs} Monte Carlo simulations for {config_name} ({num_sensors} sensors, {pole_pairs} pole pairs) with {num_failures} failures using {workers} workers")
    
    # Determine batch size
    batch_size = max(1, num_runs // workers)
    num_batches = (num_runs + batch_size - 1) // batch_size  # Ceiling division
    
    # Create parameter sets for each batch
    param_sets = [
        (config_name, num_sensors, pole_pairs, num_failures, batch_size, batch_id, steps)
        for batch_id in range(num_batches)
    ]
    
    # Run batches in parallel
    all_results = []
    with Pool(processes=workers) as pool:
        batch_results = pool.map(run_monte_carlo_batch, param_sets)
        
        # Flatten results
        for batch in batch_results:
            all_results.extend(batch)
    
    return all_results

def analyze_monte_carlo_results(results, output_dir):
    """Analyze Monte Carlo simulation results."""
    # Extract metric arrays
    metrics = {
        "error_mean": [r["error_mean"] for r in results],
        "error_std": [r["error_std"] for r in results],
        "error_max": [r["error_max"] for r in results],
        "error_p99": [r["error_p99"] for r in results],
        "resolution_bits_max": [r["resolution_bits_max"] for r in results],
        "resolution_bits_p99": [r["resolution_bits_p99"] for r in results]
    }
    
    # Calculate statistics for each metric
    stats = {}
    for metric_name, values in metrics.items():
        values_array = np.array(values)
        stats[metric_name] = {
            "mean": float(np.mean(values_array)),
            "std": float(np.std(values_array)),
            "min": float(np.min(values_array)),
            "max": float(np.max(values_array)),
            "p01": float(np.percentile(values_array, 1)),
            "p99": float(np.percentile(values_array, 99))
        }
    
    # Create histograms
    for metric_name, values in metrics.items():
        plt.figure(figsize=(10, 6))
        plt.hist(values, bins=30, alpha=0.7)
        
        # Add mean and percentile lines
        mean_val = stats[metric_name]["mean"]
        p01_val = stats[metric_name]["p01"]
        p99_val = stats[metric_name]["p99"]
        
        plt.axvline(mean_val, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean_val:.6g}')
        plt.axvline(p01_val, color='g', linestyle='dotted', linewidth=2, label=f'1st percentile: {p01_val:.6g}')
        plt.axvline(p99_val, color='g', linestyle='dotted', linewidth=2, label=f'99th percentile: {p99_val:.6g}')
        
        plt.title(f'Distribution of {metric_name}')
        plt.xlabel(metric_name)
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, f"histogram_{metric_name}.png"))
        plt.close()
    
    # Save raw results and statistics
    with open(os.path.join(output_dir, "mc_results.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    with open(os.path.join(output_dir, "mc_stats.json"), 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Create a summary report
    with open(os.path.join(output_dir, "mc_summary.txt"), 'w') as f:
        config_info = results[0]
        f.write(f"Monte Carlo Simulation Summary\n")
        f.write(f"=============================\n\n")
        f.write(f"Configuration: {config_info['config_name']}\n")
        f.write(f"Number of Sensors: {config_info['num_sensors']}\n")
        f.write(f"Number of Pole Pairs: {config_info['pole_pairs']}\n")
        f.write(f"Failed Sensors: {config_info['num_failures']}\n")
        f.write(f"Number of Runs: {len(results)}\n\n")
        
        f.write(f"Results Summary:\n")
        f.write(f"--------------\n\n")
        
        for metric_name, metric_stats in stats.items():
            f.write(f"{metric_name}:\n")
            f.write(f"  Mean: {metric_stats['mean']:.6g}\n")
            f.write(f"  Standard Deviation: {metric_stats['std']:.6g}\n")
            f.write(f"  Range (99% confidence): {metric_stats['p01']:.6g} to {metric_stats['p99']:.6g}\n")
            f.write(f"  Min: {metric_stats['min']:.6g}\n")
            f.write(f"  Max: {metric_stats['max']:.6g}\n\n")
        
        if stats["resolution_bits_p99"]["mean"] >= 17:
            f.write(f"✓ VALIDATES paper claim of 17-18 bits resolution\n")
        else:
            f.write(f"✗ DOES NOT VALIDATE paper claim of 17-18 bits resolution\n")
        
        # For fault tolerance, check if resolution still acceptable
        if config_info['num_failures'] > 0:
            min_acceptable_bits = 14  # Adjust based on project requirements
            if stats["resolution_bits_p99"]["mean"] >= min_acceptable_bits:
                f.write(f"✓ VALIDATES fault tolerance claim with {config_info['num_failures']} failed sensors\n")
            else:
                f.write(f"✗ DOES NOT VALIDATE fault tolerance claim with {config_info['num_failures']} failed sensors\n")
    
    return stats

def run_comprehensive_monte_carlo():
    """Run comprehensive Monte Carlo simulations for all configurations and fault scenarios."""
    setup_directories()
    
    # Store overall results for all configurations
    overall_results = {}
    
    # Run simulations for each configuration
    for config in CONFIGS_TO_TEST:
        config_dir = os.path.join(OUTPUT_DIR, f"{config['name']}_{config['sensors']}_{config['pole_pairs']}")
        config_results = {}
        
        # Run simulations for each fault scenario
        for scenario in FAULT_SCENARIOS:
            # Skip high failure counts for smaller sensor arrays
            if scenario['num_failures'] > 0 and config['sensors'] <= scenario['num_failures'] + 3:
                print(f"Skipping {scenario['name']} for {config['name']} (insufficient sensors)")
                continue
            
            scenario_dir = os.path.join(config_dir, f"failures_{scenario['num_failures']}")
            
            # Run the Monte Carlo simulations
            results = run_parallel_monte_carlo(
                config['name'],
                config['sensors'],
                config['pole_pairs'],
                scenario['num_failures'],
                NUM_RUNS,
                ANGLE_STEPS
            )
            
            # Analyze the results
            stats = analyze_monte_carlo_results(results, scenario_dir)
            
            # Store stats for this scenario
            config_results[scenario['name']] = stats
        
        # Store results for this configuration
        overall_results[config['name']] = config_results
    
    # Generate comparative analysis
    generate_comparative_analysis(overall_results)
    
    print(f"\nComprehensive Monte Carlo simulation completed!")
    print(f"Results are available in: {OUTPUT_DIR}")

def generate_comparative_analysis(overall_results):
    """Generate comparative analysis across all configurations and fault scenarios."""
    print("Generating comparative analysis...")
    
    # Create comparative plots directory
    comparative_dir = os.path.join(OUTPUT_DIR, "comparative_analysis")
    os.makedirs(comparative_dir, exist_ok=True)
    
    # Extract key metrics for comparison
    configs = list(overall_results.keys())
    metrics_to_compare = ["error_p99", "resolution_bits_p99"]
    
    for metric in metrics_to_compare:
        # Compare configurations with no failures
        plt.figure(figsize=(12, 6))
        
        # Extract data for each configuration
        labels = []
        values = []
        
        for config in configs:
            if "No Failures" in overall_results[config]:
                labels.append(config)
                values.append(overall_results[config]["No Failures"][metric]["mean"])
        
        # Create bar chart
        plt.bar(labels, values, alpha=0.7)
        plt.title(f'Comparison of {metric} Across Configurations (No Failures)')
        plt.ylabel(metric)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(os.path.join(comparative_dir, f"config_comparison_{metric}.png"))
        plt.close()
        
        # Compare fault tolerance for each configuration
        for config in configs:
            scenarios = list(overall_results[config].keys())
            if len(scenarios) > 1:  # Only if we have fault scenarios
                plt.figure(figsize=(12, 6))
                
                # Extract data for each fault scenario
                labels = []
                values = []
                
                for scenario in scenarios:
                    labels.append(scenario)
                    values.append(overall_results[config][scenario][metric]["mean"])
                
                # Create bar chart
                plt.bar(labels, values, alpha=0.7)
                plt.title(f'Fault Tolerance: {metric} for {config}')
                plt.ylabel(metric)
                plt.grid(True, alpha=0.3, axis='y')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                # Save the plot
                plt.savefig(os.path.join(comparative_dir, f"fault_tolerance_{config}_{metric}.png"))
                plt.close()
    
    # Create summary table
    with open(os.path.join(comparative_dir, "comparative_summary.txt"), 'w') as f:
        f.write("Comparative Analysis Summary\n")
        f.write("===========================\n\n")
        
        # Table header
        f.write(f"{'Configuration':<20} {'Failures':<15} {'Resolution (bits)':<20} {'Error (degrees)':<20}\n")
        f.write(f"{'-'*20} {'-'*15} {'-'*20} {'-'*20}\n")
        
        # Table data
        for config in configs:
            for scenario in overall_results[config]:
                resolution = overall_results[config][scenario]["resolution_bits_p99"]["mean"]
                error = overall_results[config][scenario]["error_p99"]["mean"]
                
                f.write(f"{config:<20} {scenario:<15} {resolution:<20.2f} {error:<20.6f}\n")
        
        # Paper claims
        f.write("\nPaper Claims:\n")
        f.write("------------\n")
        f.write("Resolution: 17-18 bits (±0.002°-0.003°)\n")
        f.write("Functionality with 1-3 failed sensors\n")
        
        # Add validation summary
        f.write("\nValidation Summary:\n")
        f.write("-----------------\n")
        
        # Check each configuration against claims
        for config in configs:
            # Resolution claim
            if "No Failures" in overall_results[config]:
                resolution = overall_results[config]["No Failures"]["resolution_bits_p99"]["mean"]
                if resolution >= 17:
                    f.write(f"✓ {config}: VALIDATES resolution claim with {resolution:.2f} bits\n")
                else:
                    f.write(f"✗ {config}: DOES NOT VALIDATE resolution claim with {resolution:.2f} bits\n")
            
            # Fault tolerance claim
            max_failures = 0
            for scenario in overall_results[config]:
                if scenario != "No Failures":
                    # Extract number of failures from scenario name
                    for fault_scenario in FAULT_SCENARIOS:
                        if fault_scenario["name"] == scenario:
                            num_failures = fault_scenario["num_failures"]
                            resolution = overall_results[config][scenario]["resolution_bits_p99"]["mean"]
                            
                            # Check if still acceptable resolution (e.g., >14 bits)
                            if resolution >= 14:
                                if num_failures > max_failures:
                                    max_failures = num_failures
            
            if max_failures > 0:
                f.write(f"✓ {config}: VALIDATES fault tolerance claim with up to {max_failures} failed sensors\n")
            else:
                f.write(f"✗ {config}: DOES NOT VALIDATE fault tolerance claim\n")

def main():
    """Main function to run comprehensive Monte Carlo simulation."""
    start_time = time.time()
    
    run_comprehensive_monte_carlo()
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"Total execution time: {duration:.2f} seconds ({duration/60:.2f} minutes)")

if __name__ == "__main__":
    main() 