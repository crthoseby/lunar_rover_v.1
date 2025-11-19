"""
Ground Conditions Simulator for Lunar/Mars Rover
Simulates terrain effects: rocks, dust, reduced gravity
"""

import random
import time
from datetime import datetime


class GroundConditions:
    """Simulate ground conditions and terrain effects on rover"""
    
    # Gravity constants (m/s²)
    EARTH_GRAVITY = 9.81
    MOON_GRAVITY = 1.62  # ~16.6% of Earth
    MARS_GRAVITY = 3.71  # ~37.8% of Earth
    
    # Terrain types with characteristics
    TERRAIN_TYPES = {
        'flat_rock': {
            'name': 'Flat Rock',
            'resistance': 0.1,
            'dust_level': 0.0,
            'risk_stuck': 0.01,
            'speed_modifier': 1.0,
            'energy_cost': 1.0
        },
        'dusty_plain': {
            'name': 'Dusty Plain',
            'resistance': 0.3,
            'dust_level': 0.7,
            'risk_stuck': 0.15,
            'speed_modifier': 0.8,
            'energy_cost': 1.3
        },
        'rocky_field': {
            'name': 'Rocky Field',
            'resistance': 0.5,
            'dust_level': 0.2,
            'risk_stuck': 0.25,
            'speed_modifier': 0.6,
            'energy_cost': 1.5
        },
        'soft_sand': {
            'name': 'Soft Sand/Dust',
            'resistance': 0.8,
            'dust_level': 0.9,
            'risk_stuck': 0.40,
            'speed_modifier': 0.4,
            'energy_cost': 2.0
        },
        'crater_rim': {
            'name': 'Crater Rim',
            'resistance': 0.6,
            'dust_level': 0.3,
            'risk_stuck': 0.20,
            'speed_modifier': 0.5,
            'energy_cost': 1.7
        },
        'regolith': {
            'name': 'Regolith',
            'resistance': 0.4,
            'dust_level': 0.6,
            'risk_stuck': 0.18,
            'speed_modifier': 0.7,
            'energy_cost': 1.4
        }
    }
    
    def __init__(self, environment='moon'):
        """
        Initialize ground conditions simulator
        
        Args:
            environment: 'moon', 'mars', or 'earth'
        """
        self.environment = environment
        self.gravity = self._get_gravity()
        self.current_terrain = 'dusty_plain'
        self.terrain_changes = 0
        
        # Rover status
        self.is_stuck = False
        self.wheel_slip = 0.0  # 0.0 to 1.0
        self.dust_accumulation = 0.0  # 0.0 to 1.0
        self.energy_consumed = 0.0
        self.total_distance = 0.0
        
        # Hazards
        self.rock_encounters = 0
        self.stuck_count = 0
        self.slip_events = 0
        
        print(f"✓ Ground conditions initialized: {environment.upper()}")
        print(f"   Gravity: {self.gravity:.2f} m/s² ({self.gravity/self.EARTH_GRAVITY*100:.1f}% of Earth)")
    
    def _get_gravity(self):
        """Get gravity constant for environment"""
        gravity_map = {
            'moon': self.MOON_GRAVITY,
            'mars': self.MARS_GRAVITY,
            'earth': self.EARTH_GRAVITY
        }
        return gravity_map.get(self.environment, self.MOON_GRAVITY)
    
    def set_environment(self, environment):
        """Change environment (moon/mars/earth)"""
        self.environment = environment
        self.gravity = self._get_gravity()
        print(f"🌍 Environment changed to: {environment.upper()}")
    
    def change_terrain(self, terrain_type=None):
        """
        Change terrain type (random if not specified)
        
        Args:
            terrain_type: One of TERRAIN_TYPES keys, or None for random
        """
        if terrain_type and terrain_type in self.TERRAIN_TYPES:
            self.current_terrain = terrain_type
        else:
            # Random terrain change
            self.current_terrain = random.choice(list(self.TERRAIN_TYPES.keys()))
        
        self.terrain_changes += 1
        terrain = self.TERRAIN_TYPES[self.current_terrain]
        print(f"⛰️ Terrain changed to: {terrain['name']}")
    
    def simulate_movement(self, distance_m, speed_percent):
        """
        Simulate movement and calculate effects
        
        Args:
            distance_m: Distance to travel in meters
            speed_percent: Motor speed (0-100)
        
        Returns:
            dict with movement results
        """
        terrain = self.TERRAIN_TYPES[self.current_terrain]
        
        # Calculate actual distance with terrain modifier
        actual_distance = distance_m * terrain['speed_modifier']
        
        # Calculate wheel slip based on terrain resistance and gravity
        # Lower gravity = more slip in soft terrain
        gravity_factor = self.gravity / self.EARTH_GRAVITY
        base_slip = terrain['resistance'] * (1.0 - gravity_factor * 0.5)
        self.wheel_slip = min(0.95, base_slip + random.uniform(-0.1, 0.1))
        
        # Adjust distance for wheel slip
        actual_distance *= (1.0 - self.wheel_slip * 0.5)
        
        # Check if rover gets stuck
        stuck_threshold = terrain['risk_stuck'] * (1.2 - gravity_factor)
        if random.random() < stuck_threshold and speed_percent < 50:
            self.is_stuck = True
            self.stuck_count += 1
            actual_distance = 0
            print("⚠️ ROVER STUCK! Soft terrain detected.")
        else:
            self.is_stuck = False
        
        # Track slip events
        if self.wheel_slip > 0.3:
            self.slip_events += 1
        
        # Dust accumulation (higher in dusty terrain, slower in low gravity)
        dust_rate = terrain['dust_level'] * 0.1 * (1.0 - gravity_factor * 0.3)
        self.dust_accumulation = min(1.0, self.dust_accumulation + dust_rate)
        
        # Energy consumption (higher resistance = more energy)
        energy_base = terrain['energy_cost'] * distance_m
        energy_gravity_factor = 1.0 / gravity_factor  # Less gravity = more energy for traction
        self.energy_consumed += energy_base * energy_gravity_factor
        
        # Random rock encounters
        if random.random() < 0.15:
            self.rock_encounters += 1
            print("🪨 Rock detected! Navigating around...")
        
        # Update total distance
        self.total_distance += actual_distance
        
        # Occasionally change terrain
        if random.random() < 0.1:
            self.change_terrain()
        
        return {
            'planned_distance': distance_m,
            'actual_distance': round(actual_distance, 2),
            'wheel_slip': round(self.wheel_slip * 100, 1),
            'stuck': self.is_stuck,
            'terrain': terrain['name'],
            'dust_level': round(self.dust_accumulation * 100, 1),
            'energy_used': round(energy_base * energy_gravity_factor, 2),
            'gravity': self.gravity
        }
    
    def attempt_unstuck(self):
        """Attempt to free rover from stuck condition"""
        if not self.is_stuck:
            return {'success': True, 'message': 'Rover is not stuck'}
        
        # Success chance depends on gravity (easier in low gravity)
        gravity_factor = self.gravity / self.EARTH_GRAVITY
        success_chance = 0.6 + (1.0 - gravity_factor) * 0.3
        
        if random.random() < success_chance:
            self.is_stuck = False
            print("✓ Rover freed from stuck condition!")
            return {'success': True, 'message': 'Rover successfully freed'}
        else:
            print("✗ Unstuck attempt failed. Try again.")
            return {'success': False, 'message': 'Unstuck attempt failed'}
    
    def clean_dust(self):
        """Clean dust from rover (manual cleaning)"""
        before = self.dust_accumulation
        self.dust_accumulation = max(0, self.dust_accumulation - 0.5)
        print(f"🧹 Dust cleaned: {before*100:.1f}% → {self.dust_accumulation*100:.1f}%")
    
    def get_status(self):
        """Get current ground conditions status"""
        terrain = self.TERRAIN_TYPES[self.current_terrain]
        
        return {
            'environment': self.environment,
            'gravity': round(self.gravity, 2),
            'gravity_percent': round(self.gravity / self.EARTH_GRAVITY * 100, 1),
            'terrain': terrain['name'],
            'terrain_type': self.current_terrain,
            'resistance': terrain['resistance'],
            'dust_level': terrain['dust_level'],
            'speed_modifier': terrain['speed_modifier'],
            'stuck': self.is_stuck,
            'wheel_slip': round(self.wheel_slip * 100, 1),
            'dust_accumulation': round(self.dust_accumulation * 100, 1),
            'energy_consumed': round(self.energy_consumed, 2),
            'total_distance': round(self.total_distance, 2),
            'rock_encounters': self.rock_encounters,
            'stuck_count': self.stuck_count,
            'slip_events': self.slip_events,
            'terrain_changes': self.terrain_changes
        }
    
    def get_warnings(self):
        """Get active warnings based on conditions"""
        warnings = []
        
        if self.is_stuck:
            warnings.append({'level': 'error', 'message': 'ROVER STUCK - Reverse or increase power'})
        
        if self.wheel_slip > 0.5:
            warnings.append({'level': 'warning', 'message': f'High wheel slip: {self.wheel_slip*100:.0f}%'})
        
        if self.dust_accumulation > 0.7:
            warnings.append({'level': 'warning', 'message': 'High dust accumulation - cleaning recommended'})
        
        terrain = self.TERRAIN_TYPES[self.current_terrain]
        if terrain['risk_stuck'] > 0.3:
            warnings.append({'level': 'caution', 'message': f'Hazardous terrain: {terrain["name"]}'})
        
        return warnings
    
    def reset_stats(self):
        """Reset statistics"""
        self.energy_consumed = 0.0
        self.total_distance = 0.0
        self.rock_encounters = 0
        self.stuck_count = 0
        self.slip_events = 0
        self.terrain_changes = 0
        print("📊 Ground conditions statistics reset")


# Test ground conditions
if __name__ == '__main__':
    print("Testing Ground Conditions Simulator...\n")
    
    # Moon simulation
    ground = GroundConditions(environment='moon')
    
    print("\n--- Simulating 5 movements on Moon ---")
    for i in range(5):
        result = ground.simulate_movement(distance_m=5.0, speed_percent=75)
        print(f"\nMovement {i+1}:")
        print(f"  Terrain: {result['terrain']}")
        print(f"  Distance: {result['actual_distance']}m / {result['planned_distance']}m")
        print(f"  Wheel Slip: {result['wheel_slip']}%")
        print(f"  Stuck: {result['stuck']}")
        print(f"  Energy: {result['energy_used']} units")
        time.sleep(0.5)
    
    print("\n--- Current Status ---")
    status = ground.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n--- Warnings ---")
    warnings = ground.get_warnings()
    for warning in warnings:
        print(f"  [{warning['level'].upper()}] {warning['message']}")
    
    # Test unstuck
    if ground.is_stuck:
        print("\n--- Attempting to free rover ---")
        result = ground.attempt_unstuck()
        print(f"  Result: {result['message']}")
    
    print("\nTest complete!")
