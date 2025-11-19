#!/usr/bin/env python3
"""
Lunar Rover Main Control Script
Control your rover with Mars communication delay simulation
"""

import sys
import time
from motor_control import MotorController
from mars_delay import MarsDelaySimulator
import config


class LunarRover:
    """Main lunar rover controller"""
    
    def __init__(self, delay_enabled=True, delay_mode='average'):
        """
        Initialize the lunar rover
        
        Args:
            delay_enabled: Enable Mars communication delay simulation
            delay_mode: 'min', 'max', 'average', or 'random'
        """
        print("Initializing Lunar Rover...")
        self.motors = MotorController()
        self.delay_sim = MarsDelaySimulator(delay_mode) if delay_enabled else None
        self.delay_enabled = delay_enabled
        print("Lunar Rover ready!")
        
    def execute_command(self, command_func, command_name, *args, **kwargs):
        """Execute a command with optional Mars delay"""
        if self.delay_enabled and self.delay_sim:
            self.delay_sim.apply_delay(command_name)
        
        command_func(*args, **kwargs)
    
    def forward(self, duration=None):
        """Move forward"""
        duration = duration or config.DEFAULT_MOVE_DURATION
        self.execute_command(self.motors.forward, "FORWARD", duration)
    
    def backward(self, duration=None):
        """Move backward"""
        duration = duration or config.DEFAULT_MOVE_DURATION
        self.execute_command(self.motors.backward, "BACKWARD", duration)
    
    def left(self, duration=None):
        """Turn left"""
        duration = duration or config.DEFAULT_MOVE_DURATION
        self.execute_command(self.motors.left, "TURN LEFT", duration)
    
    def right(self, duration=None):
        """Turn right"""
        duration = duration or config.DEFAULT_MOVE_DURATION
        self.execute_command(self.motors.right, "TURN RIGHT", duration)
    
    def stop(self):
        """Stop the rover"""
        self.execute_command(self.motors.stop, "STOP")
    
    def set_speed(self, speed):
        """Set motor speed (0-100)"""
        self.motors.set_speed(speed)
    
    def toggle_delay(self):
        """Toggle Mars delay simulation"""
        self.delay_enabled = not self.delay_enabled
        status = "enabled" if self.delay_enabled else "disabled"
        print(f"Mars delay simulation {status}")
    
    def set_delay_mode(self, mode):
        """Set delay mode"""
        if self.delay_sim:
            self.delay_sim.set_mode(mode)
    
    def show_statistics(self):
        """Show delay statistics"""
        if self.delay_sim:
            print("\n" + self.delay_sim.get_statistics())
        else:
            print("Delay simulation is disabled")
    
    def cleanup(self):
        """Clean up resources"""
        print("\nShutting down rover...")
        self.motors.cleanup()
        print("Rover shutdown complete")


def print_help():
    """Print help menu"""
    print("\n" + "="*60)
    print("LUNAR ROVER COMMAND CENTER")
    print("="*60)
    print("\nMovement Commands:")
    print("  w / forward  - Move forward")
    print("  s / backward - Move backward")
    print("  a / left     - Turn left")
    print("  d / right    - Turn right")
    print("  x / stop     - Stop all motors")
    print("\nConfiguration:")
    print("  speed <0-100> - Set motor speed")
    print("  delay <on/off> - Toggle Mars delay")
    print("  mode <min/max/average/random> - Set delay mode")
    print("\nInformation:")
    print("  stats - Show delay statistics")
    print("  help  - Show this help menu")
    print("  quit  - Exit program")
    print("="*60 + "\n")


def interactive_mode(rover):
    """Run rover in interactive mode"""
    print_help()
    
    try:
        while True:
            try:
                cmd = input("Rover> ").strip().lower()
                
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0]
                
                # Movement commands
                if command in ['w', 'forward']:
                    rover.forward()
                elif command in ['s', 'backward']:
                    rover.backward()
                elif command in ['a', 'left']:
                    rover.left()
                elif command in ['d', 'right']:
                    rover.right()
                elif command in ['x', 'stop']:
                    rover.stop()
                
                # Configuration commands
                elif command == 'speed':
                    if len(parts) > 1:
                        try:
                            speed = int(parts[1])
                            rover.set_speed(speed)
                        except ValueError:
                            print("Invalid speed value")
                    else:
                        print("Usage: speed <0-100>")
                
                elif command == 'delay':
                    if len(parts) > 1:
                        if parts[1] in ['on', 'off']:
                            if (parts[1] == 'on' and not rover.delay_enabled) or \
                               (parts[1] == 'off' and rover.delay_enabled):
                                rover.toggle_delay()
                        else:
                            print("Usage: delay <on/off>")
                    else:
                        rover.toggle_delay()
                
                elif command == 'mode':
                    if len(parts) > 1:
                        rover.set_delay_mode(parts[1])
                    else:
                        print("Usage: mode <min/max/average/random>")
                
                # Information commands
                elif command == 'stats':
                    rover.show_statistics()
                elif command == 'help':
                    print_help()
                elif command in ['quit', 'exit', 'q']:
                    break
                else:
                    print(f"Unknown command: {command}. Type 'help' for commands.")
            
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
                continue
    
    finally:
        rover.cleanup()


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("LUNAR ROVER CONTROL SYSTEM")
    print("Simulating Mars Communication Delay")
    print("="*60 + "\n")
    
    # Parse command line arguments
    delay_enabled = True
    delay_mode = 'average'
    
    if len(sys.argv) > 1:
        if '--no-delay' in sys.argv:
            delay_enabled = False
        for arg in sys.argv:
            if arg.startswith('--mode='):
                delay_mode = arg.split('=')[1]
    
    try:
        rover = LunarRover(delay_enabled=delay_enabled, delay_mode=delay_mode)
        interactive_mode(rover)
    except KeyboardInterrupt:
        print("\n\nEmergency shutdown initiated...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nMission complete!")


if __name__ == "__main__":
    main()
