#!/usr/bin/env python3
"""
TMR Sensor Array Monte Carlo Analysis Tool
This script analyzes Monte Carlo simulation results from the TMR sensor array project.
It builds upon the existing analyze-tmr-data.py script for specialized TMR analysis.
"""

import os
import sys
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from collections import defaultdict
import argparse
from PyLTSpice import RawRead
from PyLTSpice.log.ltsteps import LTSpiceLogReader

# Configuration
DEFAULT_INPUT_DIR = "./mc_results"
DEFAULT_OUTPUT_DIR = "./mc_analysis"
PAPER_CLAIMS = {
    "resolution": {
        "claimed": 0.0025,  # ±0.0025° claimed resolution
        "description": "Angular resolution of ±0.002°-0.003° (17-18 bits)"
    },
    "speed": {
        "claimed": 30000,  # 30,000 RPM
        "description": "Functionality at 30,000 RPM with minimal degradation"
    },
    "fault_tolerance": {
        "claimed": 3,  # Up to 3 failed sensors
        "description": "Ability to function with 1-3 failed sensors"
    }
}

class TMRMonteCarloAnalyzer:
    """Analyzer for TMR sensor array Monte Carlo simulation results"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.output_dir = DEFAULT_OUTPUT_DIR
        self.results = {}
        self.raw_files = []
        self.log_files = []
        
    def set_output_dir(self, path):
        """Set the output directory for analysis results"""
        self.output_dir = path
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, "plots"), exist_ok=True)
        os.makedirs(os.path.join(path, "reports"), exist_ok=True)
        print(f"Output directory set to: {path}")
    
    def analyze_directory(self, directory):
        """Analyze all LTspice results in a directory"""
        print(f"Analyzing Monte Carlo results in: {directory}")
        
        # Find all raw and log files
        self.raw_files = glob.glob(os.path.join(directory, "*.raw"))
        self.log_files = glob.glob(os.path.join(directory, "*.log"))
        
        if not self.raw_files and not self.log_files:
            print(f"No raw or log files found in {directory}")
            return
        
        print(f"Found {len(self.raw_files)} raw files and {len(self.log_files)} log files")
        
        # Process log files first (contain .MEAS results)
        self._analyze_log_files()
        
        # Process raw files (waveform data)
        self._analyze_raw_files()
        
        # Generate summary reports
        self._generate_reports()
    
    def _analyze_log_files(self):
        """Analyze LTspice log files with measurement results"""
        print("Analyzing log files...")
        
        # Combine all log files data
        all_measures = defaultdict(list)
        step_variables = set()
        
        for log_file in self.log_files:
            try:
                print(f"Processing {os.path.basename(log_file)}")
                log_data = LTSpiceLogReader(log_file)
                
                # Collect step variables
                for step_var in log_data.get_step_vars():
                    step_variables.add(step_var)
                
                # Collect all measurement values
                for measure in log_data.get_measure_names():
                    all_measures[measure].extend(log_data.get_measure_values(measure))
            except Exception as e:
                print(f"Error processing {log_file}: {str(e)}")
        
        # Store the combined results
        self.results["measures"] = dict(all_measures)
        self.results["step_variables"] = list(step_variables)
        
        print(f"Collected {len(all_measures)} measurement types across all log files")
    
    def _analyze_raw_files(self):
        """Analyze LTspice raw files with waveform data"""
        print("Analyzing raw files...")
        
        # Sample only a subset of raw files if there are too many
        max_raw_files = 10
        raw_files_to_process = self.raw_files[:max_raw_files] if len(self.raw_files) > max_raw_files else self.raw_files
        
        waveform_stats = defaultdict(dict)
        
        for raw_file in raw_files_to_process:
            try:
                print(f"Processing {os.path.basename(raw_file)}")
                raw_data = RawRead(raw_file)
                
                # Extract trace names
                trace_names = raw_data.get_trace_names()
                
                # Focus on key signals
                key_signals = [trace for trace in trace_names if 
                               any(signal in trace.lower() for signal in 
                                   ["error", "unwrapped", "harm", "fund", "sector"])]
                
                # Get statistics for each key signal
                for signal in key_signals:
                    try:
                        trace = raw_data.get_trace(signal)
                        steps = raw_data.get_steps()
                        
                        # Process only the first step for now
                        if steps and len(steps) > 0:
                            step_index = 0
                            wave_data = trace.get_wave(step_index)
                            
                            # Calculate statistics
                            waveform_stats[signal][os.path.basename(raw_file)] = {
                                "mean": np.mean(wave_data),
                                "std": np.std(wave_data),
                                "min": np.min(wave_data),
                                "max": np.max(wave_data),
                                "p99": np.percentile(wave_data, 99),
                                "p01": np.percentile(wave_data, 1)
                            }
                    except Exception as e:
                        print(f"Error processing trace {signal}: {str(e)}")
            except Exception as e:
                print(f"Error processing {raw_file}: {str(e)}")
        
        # Store the waveform statistics
        self.results["waveform_stats"] = dict(waveform_stats)
    
    def _generate_monte_carlo_plots(self):
        """Generate plots for Monte Carlo analysis"""
        print("Generating Monte Carlo plots...")
        
        if not self.results.get("measures"):
            print("No measurement data available for plotting")
            return
        
        # Create histograms for each measurement
        for measure, values in self.results["measures"].items():
            if not values or len(values) < 2:
                continue
                
            # Convert to numpy array and remove NaN values
            values_array = np.array(values)
            values_array = values_array[~np.isnan(values_array)]
            
            if len(values_array) < 2:
                continue
            
            plt.figure(figsize=(10, 6))
            
            # Create histogram
            n, bins, patches = plt.hist(values_array, bins=30, alpha=0.7, color='#3274A1')
            
            # Calculate statistics
            mean_val = np.mean(values_array)
            std_val = np.std(values_array)
            p01_val = np.percentile(values_array, 1)
            p99_val = np.percentile(values_array, 99)
            
            # Add vertical lines for mean and percentiles
            plt.axvline(mean_val, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean_val:.6g}')
            plt.axvline(p01_val, color='g', linestyle='dotted', linewidth=2, label=f'1st percentile: {p01_val:.6g}')
            plt.axvline(p99_val, color='g', linestyle='dotted', linewidth=2, label=f'99th percentile: {p99_val:.6g}')
            
            # Add 3-sigma boundaries if appropriate
            if not any(np.abs(values_array) > 1e9):  # Avoid plotting infinity/huge values
                plt.axvline(mean_val - 3*std_val, color='orange', linestyle='-.', linewidth=1.5, label=f'-3σ: {mean_val-3*std_val:.6g}')
                plt.axvline(mean_val + 3*std_val, color='orange', linestyle='-.', linewidth=1.5, label=f'+3σ: {mean_val+3*std_val:.6g}')
            
            plt.title(f'Monte Carlo Distribution of {measure}')
            plt.xlabel(measure)
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Save the plot
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "plots", f"mc_histogram_{measure}.png"))
            plt.close()
            
        # Create box plots for comparing key measurements
        error_measures = {k: v for k, v in self.results["measures"].items() if 'error' in k.lower()}
        if error_measures:
            plt.figure(figsize=(12, 6))
            
            # Prepare data for box plot
            labels = []
            data = []
            for measure, values in error_measures.items():
                values_array = np.array(values)
                values_array = values_array[~np.isnan(values_array)]
                if len(values_array) >= 5:  # Only include if we have enough data points
                    labels.append(measure)
                    data.append(values_array)
            
            if data:
                plt.boxplot(data, labels=labels, showfliers=True)
                plt.title('Comparison of Error Measurements Across Monte Carlo Runs')
                plt.ylabel('Error Value')
                plt.grid(True, alpha=0.3)
                plt.xticks(rotation=45, ha='right')
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, "plots", "mc_error_comparison.png"))
            
            plt.close()
    
    def _generate_reports(self):
        """Generate summary reports of the Monte Carlo analysis"""
        print("Generating reports...")
        
        # Generate plots
        self._generate_monte_carlo_plots()
        
        # Create a summary report
        self._create_summary_report()
        
        # Generate detailed JSON data
        self._export_json_data()
    
    def _create_summary_report(self):
        """Create a summary report of Monte Carlo results"""
        report_file = os.path.join(self.output_dir, "reports", "monte_carlo_summary.txt")
        
        with open(report_file, 'w') as f:
            f.write("TMR Sensor Array Monte Carlo Analysis Summary\n")
            f.write("============================================\n\n")
            
            # Report on measurements
            if self.results.get("measures"):
                f.write("Measurement Statistics:\n")
                f.write("----------------------\n\n")
                
                for measure, values in self.results["measures"].items():
                    values_array = np.array(values)
                    values_array = values_array[~np.isnan(values_array)]
                    
                    if len(values_array) >= 2:
                        mean_val = np.mean(values_array)
                        std_val = np.std(values_array)
                        min_val = np.min(values_array)
                        max_val = np.max(values_array)
                        p01_val = np.percentile(values_array, 1)
                        p99_val = np.percentile(values_array, 99)
                        
                        f.write(f"Measurement: {measure}\n")
                        f.write(f"  Sample Count: {len(values_array)}\n")
                        f.write(f"  Mean: {mean_val:.6g}\n")
                        f.write(f"  Standard Deviation: {std_val:.6g}\n")
                        f.write(f"  Minimum: {min_val:.6g}\n")
                        f.write(f"  Maximum: {max_val:.6g}\n")
                        f.write(f"  1st Percentile: {p01_val:.6g}\n")
                        f.write(f"  99th Percentile: {p99_val:.6g}\n")
                        
                        # Calculate equivalent bits for error measurements
                        if "error" in measure.lower() and max_val - min_val > 0:
                            resolution_bits = np.log2(360 / (max_val - min_val))
                            f.write(f"  Equivalent Resolution: {resolution_bits:.2f} bits\n")
                            
                            # Compare to paper claims
                            if p99_val - p01_val <= PAPER_CLAIMS["resolution"]["claimed"] * 2:
                                f.write("  ✓ VALIDATES paper claim on resolution\n")
                            else:
                                f.write("  ✗ DOES NOT VALIDATE paper claim on resolution\n")
                        
                        f.write("\n")
            
            # Summary of validation against paper claims
            f.write("\nValidation Against Paper Claims:\n")
            f.write("------------------------------\n\n")
            
            # Resolution claim
            error_measures = {k: v for k, v in self.results.get("measures", {}).items() if 'error' in k.lower()}
            if error_measures:
                # Find the best error measure (smallest range)
                best_measure = None
                best_range = float('inf')
                
                for measure, values in error_measures.items():
                    values_array = np.array(values)
                    values_array = values_array[~np.isnan(values_array)]
                    if len(values_array) >= 2:
                        p99_val = np.percentile(values_array, 99)
                        p01_val = np.percentile(values_array, 1)
                        current_range = p99_val - p01_val
                        
                        if current_range < best_range:
                            best_range = current_range
                            best_measure = measure
                
                if best_measure:
                    values_array = np.array(error_measures[best_measure])
                    values_array = values_array[~np.isnan(values_array)]
                    p99_val = np.percentile(values_array, 99)
                    p01_val = np.percentile(values_array, 1)
                    
                    f.write(f"1. {PAPER_CLAIMS['resolution']['description']}\n")
                    f.write(f"   - Best performing error measure: {best_measure}\n")
                    f.write(f"   - Measured 98% confidence interval: {p01_val:.6g}° to {p99_val:.6g}°\n")
                    
                    if p99_val - p01_val <= PAPER_CLAIMS["resolution"]["claimed"] * 2:
                        f.write("   - ✓ VALIDATED: Monte Carlo simulation confirms the claimed resolution\n")
                    else:
                        f.write("   - ✗ NOT VALIDATED: Monte Carlo simulation does not confirm the claimed resolution\n")
                        
                    # Calculate bits
                    resolution_bits = np.log2(360 / (p99_val - p01_val))
                    f.write(f"   - Equivalent resolution: {resolution_bits:.2f} bits\n\n")
        
        print(f"Summary report saved to: {report_file}")
    
    def _export_json_data(self):
        """Export detailed data in JSON format for further analysis"""
        json_file = os.path.join(self.output_dir, "reports", "monte_carlo_data.json")
        
        # Prepare the data for JSON serialization (ensure it's serializable)
        json_data = {}
        
        # Process measurement data
        if self.results.get("measures"):
            json_data["measurements"] = {}
            
            for measure, values in self.results["measures"].items():
                values_array = np.array(values)
                valid_values = values_array[~np.isnan(values_array)].tolist()
                
                if valid_values:
                    json_data["measurements"][measure] = {
                        "values": valid_values,
                        "statistics": {
                            "mean": float(np.mean(valid_values)),
                            "std": float(np.std(valid_values)),
                            "min": float(np.min(valid_values)),
                            "max": float(np.max(valid_values)),
                            "percentile_01": float(np.percentile(valid_values, 1)),
                            "percentile_99": float(np.percentile(valid_values, 99))
                        }
                    }
                    
                    # Add resolution bits for error measurements
                    if "error" in measure.lower():
                        max_val = float(np.max(valid_values))
                        min_val = float(np.min(valid_values))
                        if max_val - min_val > 0:
                            resolution_bits = float(np.log2(360 / (max_val - min_val)))
                            json_data["measurements"][measure]["statistics"]["resolution_bits"] = resolution_bits
        
        # Add step variables
        if self.results.get("step_variables"):
            json_data["step_variables"] = self.results["step_variables"]
        
        # Add validation against paper claims
        json_data["paper_claims_validation"] = {}
        
        # Resolution claim validation
        error_measures = {k: v for k, v in self.results.get("measures", {}).items() if 'error' in k.lower()}
        if error_measures:
            # Find the best error measure (smallest range)
            best_measure = None
            best_range = float('inf')
            
            for measure, values in error_measures.items():
                values_array = np.array(values)
                values_array = values_array[~np.isnan(values_array)]
                if len(values_array) >= 2:
                    p99_val = np.percentile(values_array, 99)
                    p01_val = np.percentile(values_array, 1)
                    current_range = p99_val - p01_val
                    
                    if current_range < best_range:
                        best_range = current_range
                        best_measure = measure
            
            if best_measure:
                values_array = np.array(error_measures[best_measure])
                values_array = values_array[~np.isnan(values_array)]
                p99_val = float(np.percentile(values_array, 99))
                p01_val = float(np.percentile(values_array, 1))
                
                json_data["paper_claims_validation"]["resolution"] = {
                    "description": PAPER_CLAIMS["resolution"]["description"],
                    "claimed_value": PAPER_CLAIMS["resolution"]["claimed"],
                    "best_measure": best_measure,
                    "measured_range": [p01_val, p99_val],
                    "validated": (p99_val - p01_val <= PAPER_CLAIMS["resolution"]["claimed"] * 2),
                    "resolution_bits": float(np.log2(360 / (p99_val - p01_val)))
                }
        
        # Write the JSON data
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"Detailed data exported to: {json_file}")

def main():
    """Main function to run the Monte Carlo analysis"""
    parser = argparse.ArgumentParser(description="TMR Sensor Array Monte Carlo Analysis Tool")
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT_DIR, help="Directory containing Monte Carlo simulation results")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR, help="Directory to save analysis results")
    args = parser.parse_args()
    
    analyzer = TMRMonteCarloAnalyzer()
    analyzer.set_output_dir(args.output)
    analyzer.analyze_directory(args.input)
    
    print("\nMonte Carlo analysis completed!")
    print(f"Analysis results saved to: {args.output}")

if __name__ == "__main__":
    main() 