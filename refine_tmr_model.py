#!/usr/bin/env python3
"""
Refined TMR Sensor Array Simulation
This script provides a more realistic simulation of the TMR sensor array including
analog front-end behavior, component tolerances, and temperature effects.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class RefinedTMRSensorModel:
    """
    Enhanced TMR sensor array model for hardware design validation
    Includes realistic sensor and circuit behaviors
    """
    
    def __init__(self, num_sensors=8, pole_pairs=7):
        """Initialize the TMR sensor model"""
        self.num_sensors = num_sensors
        self.pole_pairs = pole_pairs
        self.golden_angle = 137.5  # Golden angle in degrees
        
        # Default parameters
        self.params = {
            "A1": 0.2,          # Fundamental amplitude
            "A7": 1.0,          # 7th harmonic amplitude
            "noise_level": 0.01, # Noise level (1%)
            "theta": 0.0,        # Mechanical angle (degrees)
            "temperature": 25.0, # Temperature in °C
            "supply_voltage": 5.0, # Supply voltage in V
            "op_amp_bandwidth": 100e3, # Op-amp bandwidth in Hz
            "adc_resolution": 16,  # ADC resolution in bits
            "adc_sampling_rate": 10e3, # ADC sampling rate in Hz
            "tmr_sensitivity": 45.0,   # TMR sensitivity in %/mT
            "magnet_strength": 20.0,   # Magnet field strength in mT
            "position_tolerance": 0.2,  # Position tolerance in degrees
            "air_gap": 0.8,      # Air gap between sensor and magnet in mm
            "processing_delay": 100e-6  # Processing delay in seconds
        }
        
        # Sensor positions based on golden angle
        self.sensor_positions = self._calculate_sensor_positions()
        
        # Apply position tolerances to simulate manufacturing variations
        self._apply_position_tolerances()
        
        # Failed sensors list
        self.failed_sensors = []
        
        # For storing simulation results
        self.signals = {}
        self.conditioned_signals = {}
        self.digitized_signals = {}
        self.results = {}
        
        # Initialize analog front-end parameters
        self.analog_front_end = {
            "gain": 10.0,              # Amplifier gain
            "filter_cutoff": 20e3,     # Low-pass filter cutoff frequency in Hz
            "common_mode_rejection": 80.0,  # CMRR in dB
            "offset_voltage": 1.0e-3,  # Input offset voltage in V
            "input_impedance": 1.0e6,  # Input impedance in ohms
            "noise_density": 10.0e-9,  # Noise density in V/√Hz
            "nonlinearity": 0.01       # Nonlinearity in %
        }
    
    def _calculate_sensor_positions(self):
        """Calculate ideal sensor positions using golden angle spacing"""
        positions = []
        for i in range(self.num_sensors):
            # This creates the golden angle distribution
            angle = (i * self.golden_angle) % 360
            positions.append(angle)
        return positions
    
    def _apply_position_tolerances(self):
        """Apply manufacturing tolerances to sensor positions"""
        # Apply random position errors within tolerance
        position_tolerance = self.params["position_tolerance"]
        for i in range(len(self.sensor_positions)):
            # Apply random error within tolerance
            error = np.random.uniform(-position_tolerance, position_tolerance)
            self.sensor_positions[i] += error
            # Ensure position is within [0, 360)
            self.sensor_positions[i] %= 360
    
    def set_failed_sensors(self, num_failures):
        """Set specific sensors as failed"""
        # Reset failed sensors
        self.failed_sensors = []
        
        if num_failures > 0:
            # Randomly select sensors to fail
            available_sensors = list(range(self.num_sensors))
            self.failed_sensors = np.random.choice(available_sensors, num_failures, replace=False).tolist()
            
            print(f"Set {num_failures} sensors as failed: {self.failed_sensors}")
    
    def _apply_temperature_effects(self, signals):
        """Apply temperature effects to sensor signals"""
        # TMR sensors typically have temperature coefficient of ~0.1%/°C
        temp_coeff = 0.001  # 0.1% per °C
        temp_deviation = self.params["temperature"] - 25.0  # Deviation from 25°C
        
        # Calculate temperature scaling factor
        temp_scale = 1.0 + (temp_deviation * temp_coeff)
        
        # Apply temperature scaling to all signals
        for key in signals:
            signals[key] *= temp_scale
        
        return signals
    
    def _apply_supply_voltage_effects(self, signals):
        """Apply supply voltage effects to signals"""
        # Normalize to nominal 5V supply
        voltage_factor = self.params["supply_voltage"] / 5.0
        
        # Apply voltage scaling - simplistic model
        for key in signals:
            signals[key] *= voltage_factor
        
        return signals
    
    def _apply_analog_front_end(self, signals):
        """Simulate analog front-end behavior"""
        conditioned_signals = {}
        
        for key, signal in signals.items():
            # Skip failed sensors
            if int(key[1:]) in self.failed_sensors:
                conditioned_signals[key] = 0
                continue
            
            # Apply gain
            amplified = signal * self.analog_front_end["gain"]
            
            # Add offset
            offset = self.analog_front_end["offset_voltage"] / self.params["supply_voltage"]
            amplified += offset
            
            # Add noise based on noise density and bandwidth
            noise_bandwidth = min(self.analog_front_end["filter_cutoff"], 
                                 self.params["op_amp_bandwidth"])
            noise_rms = self.analog_front_end["noise_density"] * np.sqrt(noise_bandwidth)
            noise = np.random.normal(0, noise_rms)
            amplified += noise
            
            # Apply nonlinearity (simple polynomial model)
            nonlin = self.analog_front_end["nonlinearity"]
            amplified += nonlin * amplified * amplified
            
            # Store conditioned signal
            conditioned_signals[key] = amplified
        
        return conditioned_signals
    
    def _apply_adc_conversion(self, conditioned_signals):
        """Simulate ADC conversion process"""
        digitized_signals = {}
        
        # Calculate ADC parameters
        adc_range = self.params["supply_voltage"]
        adc_steps = 2 ** self.params["adc_resolution"]
        lsb_size = adc_range / adc_steps
        
        for key, signal in conditioned_signals.items():
            # Skip failed sensors
            if int(key[1:]) in self.failed_sensors:
                digitized_signals[key] = 0
                continue
            
            # Clamp to ADC range
            clamped = max(0, min(signal, adc_range))
            
            # Quantize to ADC steps
            quantized = round(clamped / lsb_size) * lsb_size
            
            # Normalize back to original range
            normalized = quantized / self.analog_front_end["gain"]
            
            # Store digitized signal
            digitized_signals[key] = normalized
        
        return digitized_signals
    
    def generate_sensor_signals(self, theta, rpm=0):
        """Generate the TMR sensor signals at a given mechanical angle and speed"""
        self.params["theta"] = theta
        signals = {}
        
        # Calculate angular velocity in rad/s
        angular_velocity = rpm * 2 * np.pi / 60
        
        for i in range(self.num_sensors):
            # Skip if sensor has failed
            if i in self.failed_sensors:
                signals[f"S{i}"] = 0
                continue
                
            sensor_name = f"S{i}"
            phi = self.sensor_positions[i]
            
            # Calculate the sensor signal with fundamental and harmonic components
            # S_i(θ) = A₁sin(θ + φᵢ) + A₇sin(7θ + 7φᵢ) + noise
            fundamental = self.params["A1"] * np.sin(np.radians(theta + phi))
            harmonic = self.params["A7"] * np.sin(np.radians(self.pole_pairs * theta + self.pole_pairs * phi))
            
            # Calculate air gap effect on signal strength
            # Field strength decreases with square of distance
            nominal_gap = 0.8  # mm
            actual_gap = self.params["air_gap"]
            gap_factor = (nominal_gap / actual_gap) ** 2
            
            # Apply air gap effects
            fundamental *= gap_factor
            harmonic *= gap_factor
            
            # Add speed-dependent noise (mechanical vibration, etc.)
            speed_noise = 0
            if rpm > 0:
                # Noise increases with speed
                speed_factor = rpm / 10000  # Normalized to 10,000 RPM
                speed_noise = speed_factor * self.params["noise_level"] * np.random.normal(0, 1)
            
            # Add basic electrical noise
            if self.params["noise_level"] > 0:
                electrical_noise = self.params["noise_level"] * np.random.normal(0, 1)
            else:
                electrical_noise = 0
            
            # Sum the components
            signal = fundamental + harmonic + electrical_noise + speed_noise
            signals[sensor_name] = signal
        
        # Apply temperature effects
        signals = self._apply_temperature_effects(signals)
        
        # Apply supply voltage effects
        signals = self._apply_supply_voltage_effects(signals)
        
        # Store raw signals
        self.signals = signals
        
        # Apply analog front-end effects
        self.conditioned_signals = self._apply_analog_front_end(signals)
        
        # Apply ADC conversion
        self.digitized_signals = self._apply_adc_conversion(self.conditioned_signals)
        
        return self.digitized_signals
    
    def extract_harmonics(self, use_digitized=True):
        """Extract fundamental and 7th harmonic components from sensor signals"""
        # Choose which signal set to use
        if use_digitized and self.digitized_signals:
            signals_to_use = self.digitized_signals
        else:
            signals_to_use = self.signals
        
        if not signals_to_use:
            raise ValueError("No sensor signals available. Generate signals first.")
        
        fund_sin = 0
        fund_cos = 0
        harm_sin = 0
        harm_cos = 0
        
        for i, sensor_name in enumerate(signals_to_use):
            if i in self.failed_sensors:
                continue
                
            phi = self.sensor_positions[i]
            signal = signals_to_use[sensor_name]
            
            # Extract fundamental components
            fund_sin += signal * np.sin(np.radians(phi))
            fund_cos += signal * np.cos(np.radians(phi))
            
            # Extract 7th harmonic components
            harm_sin += signal * np.sin(np.radians(self.pole_pairs * phi))
            harm_cos += signal * np.cos(np.radians(self.pole_pairs * phi))
        
        # Normalize by active sensors (not failed)
        active_sensor_count = self.num_sensors - len(self.failed_sensors)
        if active_sensor_count > 0:
            fund_sin /= active_sensor_count
            fund_cos /= active_sensor_count
            harm_sin /= active_sensor_count
            harm_cos /= active_sensor_count
        
        # Calculate phases
        fund_phase = np.degrees(np.arctan2(fund_sin, fund_cos))
        if fund_phase < 0:
            fund_phase += 360
        
        harm_phase = np.degrees(np.arctan2(harm_sin, harm_cos))
        if harm_phase < 0:
            harm_phase += 360
        
        # Calculate sector
        sector = int(np.floor(fund_phase / (360 / self.pole_pairs)))
        
        # Calculate unwrapped angle
        phase_diff = harm_phase - self.pole_pairs * fund_phase
        # Normalize to [0, 360)
        phase_diff %= 360
        
        # Unwrapped angle calculation
        unwrapped = sector * (360 / self.pole_pairs) + phase_diff / self.pole_pairs
        
        # Make sure unwrapped is in [0, 360)
        unwrapped %= 360
        
        # Calculate error
        theta = self.params["theta"]
        raw_error = theta - unwrapped
        # Normalize error to [-180, 180)
        error = ((raw_error + 180) % 360) - 180
        
        # Store results
        self.results = {
            "fund_sin": fund_sin,
            "fund_cos": fund_cos,
            "fund_phase": fund_phase,
            "harm_sin": harm_sin,
            "harm_cos": harm_cos,
            "harm_phase": harm_phase,
            "sector": sector,
            "unwrapped": unwrapped,
            "error": error
        }
        
        return self.results
    
    def simulate_full_rotation(self, steps=1000, start_angle=0, end_angle=360, rpm=0):
        """Simulate a full rotation of the sensor array"""
        angles = np.linspace(start_angle, end_angle, steps)
        
        # Initialize data structures for storing results
        time_data = angles 
        signals_data = {f"S{i}": np.zeros(steps) for i in range(self.num_sensors)}
        conditioned_data = {f"S{i}": np.zeros(steps) for i in range(self.num_sensors)}
        digitized_data = {f"S{i}": np.zeros(steps) for i in range(self.num_sensors)}
        results_data = {
            "fund_sin": np.zeros(steps),
            "fund_cos": np.zeros(steps),
            "fund_phase": np.zeros(steps),
            "harm_sin": np.zeros(steps),
            "harm_cos": np.zeros(steps),
            "harm_phase": np.zeros(steps),
            "sector": np.zeros(steps),
            "unwrapped": np.zeros(steps),
            "error": np.zeros(steps)
        }
        
        # Run simulation for each angle
        for i, angle in enumerate(angles):
            # Generate sensor signals
            self.generate_sensor_signals(angle, rpm)
            
            # Store sensor signals
            for s in range(self.num_sensors):
                signals_data[f"S{s}"][i] = self.signals[f"S{s}"]
                conditioned_data[f"S{s}"][i] = self.conditioned_signals[f"S{s}"]
                digitized_data[f"S{s}"][i] = self.digitized_signals[f"S{s}"]
            
            # Extract harmonics and calculate angles
            self.extract_harmonics(use_digitized=True)
            
            # Store results
            for key in results_data:
                results_data[key][i] = self.results[key]
        
        return {
            "angles": angles,
            "signals": signals_data,
            "conditioned": conditioned_data,
            "digitized": digitized_data,
            "results": results_data
        }
    
    def analyze_results(self, simulation_data, rpm=0):
        """Analyze simulation results and calculate performance metrics"""
        error_data = simulation_data["results"]["error"]
        
        # Calculate error statistics
        error_mean = np.mean(error_data)
        error_std = np.std(error_data)
        error_max = np.max(np.abs(error_data))
        error_p99 = np.percentile(np.abs(error_data), 99)
        
        # Calculate resolution metrics
        resolution_bits_max = np.log2(360 / (2 * error_max))
        resolution_bits_p99 = np.log2(360 / (2 * error_p99))
        
        # For high-speed simulations, add latency metrics
        latency_metrics = {}
        if rpm > 0:
            # Angular velocity in degrees per second
            angular_velocity = rpm * 6  # 6 = 360/60
            
            # Processing delay in degrees at this speed
            processing_delay_deg = angular_velocity * self.params["processing_delay"]
            
            # Sampling period in seconds
            sampling_period = 1.0 / self.params["adc_sampling_rate"]
            
            # Sampling delay in degrees at this speed
            sampling_delay_deg = angular_velocity * sampling_period / 2  # Average delay is half period
            
            # Total latency in degrees
            total_latency_deg = processing_delay_deg + sampling_delay_deg
            
            # Store latency metrics
            latency_metrics = {
                "processing_delay_deg": processing_delay_deg,
                "sampling_delay_deg": sampling_delay_deg,
                "total_latency_deg": total_latency_deg
            }
        
        # Combine all metrics
        metrics = {
            "error_mean": error_mean,
            "error_std": error_std,
            "error_max": error_max,
            "error_p99": error_p99,
            "resolution_bits_max": resolution_bits_max,
            "resolution_bits_p99": resolution_bits_p99,
            **latency_metrics
        }
        
        return metrics
    
    def plot_results(self, simulation_data, output_dir=None):
        """Plot simulation results"""
        angles = simulation_data["angles"]
        
        # 1. Plot raw, conditioned, and digitized signals for one sensor
        plt.figure(figsize=(12, 8))
        plt.subplot(3, 1, 1)
        for s in range(min(3, self.num_sensors)):  # Plot first 3 sensors only
            plt.plot(angles, simulation_data["signals"][f"S{s}"], label=f"Sensor {s}")
        plt.title("Raw TMR Sensor Signals")
        plt.ylabel("Signal Amplitude")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(3, 1, 2)
        for s in range(min(3, self.num_sensors)):
            plt.plot(angles, simulation_data["conditioned"][f"S{s}"], label=f"Sensor {s}")
        plt.title("Conditioned Signals (After Analog Front-End)")
        plt.ylabel("Amplitude")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.subplot(3, 1, 3)
        for s in range(min(3, self.num_sensors)):
            plt.plot(angles, simulation_data["digitized"][f"S{s}"], label=f"Sensor {s}")
        plt.title("Digitized Signals (After ADC)")
        plt.xlabel("Mechanical Angle (degrees)")
        plt.ylabel("Amplitude")
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        if output_dir:
            plt.savefig(os.path.join(output_dir, "signal_processing_stages.png"))
        plt.close()
        
        # 2. Plot extracted components
        plt.figure(figsize=(12, 6))
        plt.plot(angles, simulation_data["results"]["fund_sin"], label="Fund Sin")
        plt.plot(angles, simulation_data["results"]["fund_cos"], label="Fund Cos")
        plt.plot(angles, simulation_data["results"]["harm_sin"], label="7th Harm Sin")
        plt.plot(angles, simulation_data["results"]["harm_cos"], label="7th Harm Cos")
        plt.title("Extracted Harmonic Components")
        plt.xlabel("Mechanical Angle (degrees)")
        plt.ylabel("Amplitude")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        if output_dir:
            plt.savefig(os.path.join(output_dir, "extracted_harmonics.png"))
        plt.close()
        
        # 3. Plot phase and unwrapped angle
        plt.figure(figsize=(12, 6))
        plt.plot(angles, simulation_data["results"]["fund_phase"], label="Fundamental Phase")
        plt.plot(angles, simulation_data["results"]["harm_phase"], label="7th Harmonic Phase")
        plt.plot(angles, simulation_data["results"]["unwrapped"], label="Unwrapped Angle")
        plt.plot(angles, angles, 'k--', label="Actual Angle")
        plt.title("Phase and Angle Reconstruction")
        plt.xlabel("Mechanical Angle (degrees)")
        plt.ylabel("Angle (degrees)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        if output_dir:
            plt.savefig(os.path.join(output_dir, "angle_reconstruction.png"))
        plt.close()
        
        # 4. Plot error
        plt.figure(figsize=(12, 6))
        plt.plot(angles, simulation_data["results"]["error"])
        plt.title("Angular Error")
        plt.xlabel("Mechanical Angle (degrees)")
        plt.ylabel("Error (degrees)")
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='r', linestyle='--')
        
        # Add error statistics
        error_data = simulation_data["results"]["error"]
        error_max = np.max(np.abs(error_data))
        error_p99 = np.percentile(np.abs(error_data), 99)
        resolution_bits = np.log2(360 / (2 * error_p99))
        
        plt.annotate(f"Max Error: ±{error_max:.6f}°\n"
                    f"99% Error: ±{error_p99:.6f}°\n"
                    f"Resolution: {resolution_bits:.2f} bits",
                    xy=(0.02, 0.95), xycoords='axes fraction',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
        
        plt.tight_layout()
        if output_dir:
            plt.savefig(os.path.join(output_dir, "angular_error.png"))
        plt.close()

def run_hardware_validation_test(configuration, rpm=0, output_dir="./hw_validation"):
    """Run a comprehensive hardware validation test for a specific configuration"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create refined TMR model
    model = RefinedTMRSensorModel(
        num_sensors=configuration["sensors"],
        pole_pairs=configuration["pole_pairs"]
    )
    
    # Set any failed sensors
    if configuration.get("failures", 0) > 0:
        model.set_failed_sensors(configuration["failures"])
    
    # Set environmental parameters
    model.params["temperature"] = configuration.get("temperature", 25.0)
    model.params["supply_voltage"] = configuration.get("supply_voltage", 5.0)
    model.params["air_gap"] = configuration.get("air_gap", 0.8)
    
    # Run simulation
    print(f"Running hardware validation for {configuration['name']} configuration...")
    print(f"  Sensors: {configuration['sensors']}, Pole Pairs: {configuration['pole_pairs']}")
    print(f"  Failed Sensors: {configuration.get('failures', 0)}")
    print(f"  Temperature: {model.params['temperature']}°C")
    print(f"  Speed: {rpm} RPM")
    
    # Run a full rotation simulation
    sim_data = model.simulate_full_rotation(steps=1000, rpm=rpm)
    
    # Analyze results
    metrics = model.analyze_results(sim_data, rpm)
    
    # Print key metrics
    print("\nSimulation Results:")
    print(f"  Maximum Error: ±{metrics['error_max']:.6f}°")
    print(f"  99% Error: ±{metrics['error_p99']:.6f}°")
    print(f"  Resolution: {metrics['resolution_bits_p99']:.2f} bits")
    
    if rpm > 0:
        print(f"  Processing Delay: {metrics['processing_delay_deg']:.3f}°")
        print(f"  Sampling Delay: {metrics['sampling_delay_deg']:.3f}°")
        print(f"  Total Latency: {metrics['total_latency_deg']:.3f}°")
    
    # Plot results
    config_dir = os.path.join(output_dir, f"{configuration['name']}_validation")
    os.makedirs(config_dir, exist_ok=True)
    model.plot_results(sim_data, config_dir)
    
    return metrics

def main():
    """Main function to run hardware validation tests"""
    # Define configurations to test
    configurations = [
        {
            "name": "Standard",
            "sensors": 8,
            "pole_pairs": 7,
            "failures": 0,
            "temperature": 25.0,
            "supply_voltage": 5.0,
            "air_gap": 0.8
        },
        {
            "name": "Optimal",
            "sensors": 16,
            "pole_pairs": 17,
            "failures": 0,
            "temperature": 25.0,
            "supply_voltage": 5.0,
            "air_gap": 0.8
        },
        {
            "name": "FaultTolerant",
            "sensors": 16,
            "pole_pairs": 13,
            "failures": 2,
            "temperature": 25.0,
            "supply_voltage": 5.0,
            "air_gap": 0.8
        }
    ]
    
    # Define RPM values to test
    rpm_values = [0, 1000, 10000, 30000]
    
    # Run tests for each configuration and RPM
    all_results = {}
    
    for config in configurations:
        config_results = {}
        for rpm in rpm_values:
            # Create specific output directory
            output_dir = f"./hw_validation/{config['name']}"
            if rpm > 0:
                output_dir += f"_{rpm}RPM"
            
            # Run test
            metrics = run_hardware_validation_test(config, rpm, output_dir)
            
            # Store results
            config_results[rpm] = metrics
        
        all_results[config["name"]] = config_results
    
    # Generate summary report
    with open("./hw_validation/validation_summary.txt", "w") as f:
        f.write("Hardware Validation Summary\n")
        f.write("=========================\n\n")
        
        for config_name, config_results in all_results.items():
            f.write(f"Configuration: {config_name}\n")
            f.write("-" * 50 + "\n")
            
            for rpm, metrics in config_results.items():
                f.write(f"  Speed: {rpm} RPM\n")
                f.write(f"    Resolution: {metrics['resolution_bits_p99']:.2f} bits\n")
                f.write(f"    Error (99%): ±{metrics['error_p99']:.6f}°\n")
                
                if rpm > 0:
                    f.write(f"    Total Latency: {metrics['total_latency_deg']:.3f}°\n")
                
                f.write("\n")
    
    print("\nHardware validation completed!")
    print("Results are available in: ./hw_validation/")

if __name__ == "__main__":
    main() 