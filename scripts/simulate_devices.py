#!/usr/bin/env python3
"""
IoT Device Simulator

This script simulates multiple IoT devices sending sensor data to the backend.
Each device has a different set of sensors with realistic data patterns.

Usage:
    python simulate_devices.py [--url URL] [--interval SECONDS]

Options:
    --url       Backend URL (default: http://localhost:8000)
    --interval  Data send interval in seconds (default: 60)
"""

import argparse
import math
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

import psycopg2
import requests

# ============================================================================
# Device Configuration
# ============================================================================

@dataclass
class SensorConfig:
    """Configuration for a sensor."""
    name: str
    type: str
    value_generator: Callable[[], tuple[int, int]]  # Returns (value, shift)


def temperature_generator(base: float = 22.0, variation: float = 5.0) -> Callable[[], tuple[int, int]]:
    """Generate temperature values (Celsius) with daily variation."""
    def generator() -> tuple[int, int]:
        hour = datetime.now().hour
        # Simulate daily temperature cycle (cooler at night, warmer during day)
        daily_offset = math.sin((hour - 6) * math.pi / 12) * variation
        temp = base + daily_offset + random.gauss(0, 0.5)
        # Use shift=8 for 8 fractional bits (0.00390625 precision)
        shift = 8
        value = int(temp * (1 << shift))
        return value, shift
    return generator


def humidity_generator(base: float = 50.0, variation: float = 20.0) -> Callable[[], tuple[int, int]]:
    """Generate humidity values (%) with some variation."""
    def generator() -> tuple[int, int]:
        humidity = base + random.gauss(0, variation / 3)
        humidity = max(20, min(95, humidity))  # Clamp to realistic range
        shift = 8
        value = int(humidity * (1 << shift))
        return value, shift
    return generator


def pressure_generator(base: float = 1013.25) -> Callable[[], tuple[int, int]]:
    """Generate atmospheric pressure values (hPa)."""
    def generator() -> tuple[int, int]:
        # Pressure varies slowly
        pressure = base + random.gauss(0, 5)
        shift = 4
        value = int(pressure * (1 << shift))
        return value, shift
    return generator


def light_generator() -> Callable[[], tuple[int, int]]:
    """Generate light intensity values (lux) based on time of day."""
    def generator() -> tuple[int, int]:
        hour = datetime.now().hour
        # Simulate daylight cycle
        if 6 <= hour < 20:
            base_light = 500 + math.sin((hour - 6) * math.pi / 14) * 800
        else:
            base_light = 10  # Night time
        light = max(0, base_light + random.gauss(0, 50))
        shift = 4
        value = int(light * (1 << shift))
        return value, shift
    return generator


def motion_generator(probability: float = 0.3) -> Callable[[], tuple[int, int]]:
    """Generate motion detection values (0 or 1)."""
    def generator() -> tuple[int, int]:
        hour = datetime.now().hour
        # Higher activity during work hours
        if 8 <= hour < 18:
            prob = probability * 1.5
        else:
            prob = probability * 0.5
        motion = 1 if random.random() < prob else 0
        return motion, 0  # No shift needed for binary
    return generator


def co2_generator(base: float = 400.0) -> Callable[[], tuple[int, int]]:
    """Generate CO2 values (ppm)."""
    def generator() -> tuple[int, int]:
        hour = datetime.now().hour
        # CO2 builds up during occupied hours
        if 9 <= hour < 17:
            co2 = base + random.gauss(200, 50)
        else:
            co2 = base + random.gauss(0, 20)
        co2 = max(350, co2)
        shift = 4
        value = int(co2 * (1 << shift))
        return value, shift
    return generator


def voltage_generator(nominal: float = 3.3, variation: float = 0.1) -> Callable[[], tuple[int, int]]:
    """Generate voltage values (V) for battery monitoring."""
    def generator() -> tuple[int, int]:
        voltage = nominal + random.gauss(0, variation)
        voltage = max(2.5, min(4.2, voltage))
        shift = 10
        value = int(voltage * (1 << shift))
        return value, shift
    return generator


def soil_moisture_generator(base: float = 60.0) -> Callable[[], tuple[int, int]]:
    """Generate soil moisture values (%)."""
    def generator() -> tuple[int, int]:
        # Soil moisture decreases slowly over time with random watering events
        moisture = base + random.gauss(-2, 10)
        moisture = max(10, min(100, moisture))
        shift = 8
        value = int(moisture * (1 << shift))
        return value, shift
    return generator


def water_level_generator(max_level: float = 100.0) -> Callable[[], tuple[int, int]]:
    """Generate water level values (%)."""
    def generator() -> tuple[int, int]:
        level = random.uniform(20, max_level)
        shift = 8
        value = int(level * (1 << shift))
        return value, shift
    return generator


def noise_generator(base: float = 40.0) -> Callable[[], tuple[int, int]]:
    """Generate noise level values (dB)."""
    def generator() -> tuple[int, int]:
        hour = datetime.now().hour
        # Noisier during day
        if 7 <= hour < 22:
            noise = base + random.gauss(15, 10)
        else:
            noise = base + random.gauss(-10, 5)
        noise = max(20, min(100, noise))
        shift = 4
        value = int(noise * (1 << shift))
        return value, shift
    return generator


# ============================================================================
# Device Definitions
# ============================================================================

DEVICES = {
    "weather-station-01": [
        SensorConfig("temperature", "temperature", temperature_generator(22, 8)),
        SensorConfig("humidity", "humidity", humidity_generator(55, 15)),
        SensorConfig("pressure", "pressure", pressure_generator(1013)),
        SensorConfig("light", "light", light_generator()),
    ],
    "weather-station-02": [
        SensorConfig("temperature", "temperature", temperature_generator(20, 10)),
        SensorConfig("humidity", "humidity", humidity_generator(60, 20)),
        SensorConfig("pressure", "pressure", pressure_generator(1015)),
    ],
    "smart-home-living-room": [
        SensorConfig("temperature", "temperature", temperature_generator(23, 2)),
        SensorConfig("humidity", "humidity", humidity_generator(45, 10)),
        SensorConfig("motion", "motion", motion_generator(0.4)),
        SensorConfig("light", "light", light_generator()),
        SensorConfig("co2", "air_quality", co2_generator(450)),
        SensorConfig("noise", "noise", noise_generator(35)),
    ],
    "smart-home-bedroom": [
        SensorConfig("temperature", "temperature", temperature_generator(21, 2)),
        SensorConfig("humidity", "humidity", humidity_generator(50, 10)),
        SensorConfig("motion", "motion", motion_generator(0.2)),
        SensorConfig("light", "light", light_generator()),
    ],
    "greenhouse-monitor": [
        SensorConfig("temperature", "temperature", temperature_generator(25, 5)),
        SensorConfig("humidity", "humidity", humidity_generator(70, 15)),
        SensorConfig("soil_moisture", "moisture", soil_moisture_generator(65)),
        SensorConfig("light", "light", light_generator()),
    ],
    "industrial-sensor-01": [
        SensorConfig("temperature", "temperature", temperature_generator(30, 15)),
        SensorConfig("voltage", "voltage", voltage_generator(12.0, 0.5)),
        SensorConfig("noise", "noise", noise_generator(60)),
    ],
    "water-tank-monitor": [
        SensorConfig("water_level", "level", water_level_generator(100)),
        SensorConfig("temperature", "temperature", temperature_generator(18, 3)),
    ],
    "office-environment": [
        SensorConfig("temperature", "temperature", temperature_generator(22, 2)),
        SensorConfig("humidity", "humidity", humidity_generator(40, 10)),
        SensorConfig("co2", "air_quality", co2_generator(500)),
        SensorConfig("light", "light", light_generator()),
        SensorConfig("noise", "noise", noise_generator(45)),
        SensorConfig("motion", "motion", motion_generator(0.5)),
    ],
}


# ============================================================================
# Simulator
# ============================================================================

class DeviceSimulator:
    """Simulates IoT devices sending data to the backend."""
    
    def __init__(self, base_url: str, db_url: str = None):
        self.base_url = base_url.rstrip("/")
        self.db_url = db_url
        self.session = requests.Session()
    
    def approve_device(self, device_id: str) -> bool:
        """Approve a device directly in the database."""
        if not self.db_url:
            print(f"[{device_id}] No database URL configured, cannot approve")
            return False
        
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            cur.execute(
                "UPDATE devices SET approved = true WHERE id = %s",
                (device_id,)
            )
            conn.commit()
            cur.close()
            conn.close()
            print(f"[{device_id}] Approved in database")
            return True
        except Exception as e:
            print(f"[{device_id}] Failed to approve: {e}")
            return False
    
    def register_device(self, device_id: str) -> bool:
        """Register a device with the backend."""
        url = f"{self.base_url}/devices/register"
        try:
            response = self.session.post(
                url,
                data=device_id,
                headers={"Content-Type": "text/plain"}
            )
            if response.status_code == 200:
                print(f"[{device_id}] Already registered")
                return True
            elif response.status_code == 401:
                detail = response.json().get("detail", "")
                if "not registered" in detail.lower():
                    print(f"[{device_id}] Registered, waiting for approval")
                    return False
                else:
                    print(f"[{device_id}] {detail}")
                    return False
            else:
                print(f"[{device_id}] Registration failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"[{device_id}] Connection error: {e}")
            return False
    
    def send_data(self, device_id: str, sensors: list[SensorConfig]) -> bool:
        """Send sensor data for a device."""
        url = f"{self.base_url}/devices/send_data"
        
        # Generate sensor values
        sensor_values = []
        for sensor in sensors:
            value, shift = sensor.value_generator()
            sensor_values.append({
                "sensor": sensor.name,
                "type": sensor.type,
                "value": value,
                "shift": shift
            })
        
        try:
            response = self.session.post(
                url,
                json=sensor_values,
                headers={"X-SENSOR-ID": device_id}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"[{device_id}] Sent {result.get('count', len(sensor_values))} readings")
                return True
            elif response.status_code == 401:
                print(f"[{device_id}] Not approved yet, skipping data send")
                return False
            else:
                print(f"[{device_id}] Send failed: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"[{device_id}] Connection error: {e}")
            return False
    
    def run(self, devices: dict, interval: int = 60, auto_approve: bool = False):
        """Run the simulator continuously."""
        print(f"Starting IoT Device Simulator")
        print(f"Backend URL: {self.base_url}")
        print(f"Devices: {len(devices)}")
        print(f"Interval: {interval} seconds")
        print(f"Auto-approve: {auto_approve}")
        print("-" * 50)
        
        # Register all devices first
        print("\n=== Registering devices ===")
        for device_id in devices:
            self.register_device(device_id)
        
        # Auto-approve if enabled
        if auto_approve:
            print("\n=== Approving devices ===")
            for device_id in devices:
                self.approve_device(device_id)
        
        print("\n=== Starting data simulation ===")
        print("(Press Ctrl+C to stop)\n")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}] Sending data batch...")
                
                for device_id, sensors in devices.items():
                    self.send_data(device_id, sensors)
                
                print(f"Waiting {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nSimulator stopped.")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="IoT Device Simulator - generates fake sensor data"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Data send interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Send data once and exit (useful for testing)"
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Auto-approve devices in the database"
    )
    parser.add_argument(
        "--db-url",
        default=os.environ.get("DATABASE_URL", "postgresql://postgres:yourpassword@localhost:5432/iot_data"),
        help="Database URL for device approval (default: from DATABASE_URL env or localhost)"
    )
    
    args = parser.parse_args()
    
    simulator = DeviceSimulator(args.url, db_url=args.db_url if args.approve else None)
    
    if args.once:
        # Register and send once
        print("=== Registering devices ===")
        for device_id in DEVICES:
            simulator.register_device(device_id)
        if args.approve:
            print("\n=== Approving devices ===")
            for device_id in DEVICES:
                simulator.approve_device(device_id)
        print("\n=== Sending data ===")
        for device_id, sensors in DEVICES.items():
            simulator.send_data(device_id, sensors)
    else:
        simulator.run(DEVICES, args.interval, auto_approve=args.approve)


if __name__ == "__main__":
    main()
