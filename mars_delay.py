"""
Mars Communication Delay Simulator
Simulates the light-speed delay between Earth and Mars
"""

import time
import random
from datetime import datetime
import config


class MarsDelaySimulator:
    """Simulates communication delay to Mars"""
    
    def __init__(self, delay_mode='average'):
        """
        Initialize delay simulator
        
        Args:
            delay_mode: 'min', 'max', 'average', or 'random'
        """
        self.delay_mode = delay_mode
        self.total_delay_time = 0
        self.command_count = 0
        
    def get_delay(self) -> float:
        """Calculate delay based on mode"""
        if self.delay_mode == 'min':
            return config.MARS_LAG_MIN
        elif self.delay_mode == 'max':
            return config.MARS_LAG_MAX
        elif self.delay_mode == 'average':
            return config.MARS_LAG_AVERAGE
        elif self.delay_mode == 'random':
            return random.uniform(config.MARS_LAG_MIN, config.MARS_LAG_MAX)
        else:
            return config.MARS_LAG_AVERAGE
    
    def apply_delay(self, command_name: str):
        """Apply communication delay before executing command"""
        delay = self.get_delay()
        self.total_delay_time += delay
        self.command_count += 1
        
        print(f"\n{'='*50}")
        print(f"[EARTH] Command sent: {command_name}")
        print(f"[TRANSMISSION] Delay: {delay:.2f}s")
        print(f"[WAITING] Signal traveling to Mars...")
        
        # Visual countdown
        steps = 10
        for i in range(steps):
            time.sleep(delay / steps)
            progress = int((i + 1) / steps * 20)
            bar = '█' * progress + '░' * (20 - progress)
            print(f"\r[{bar}] {((i+1)/steps*100):.0f}%", end='', flush=True)
        
        print(f"\n[MARS] Command received: {command_name}")
        print(f"{'='*50}\n")
    
    def set_mode(self, mode: str):
        """Change delay mode"""
        valid_modes = ['min', 'max', 'average', 'random']
        if mode in valid_modes:
            self.delay_mode = mode
            print(f"Delay mode set to: {mode}")
        else:
            print(f"Invalid mode. Choose from: {', '.join(valid_modes)}")
    
    def get_statistics(self):
        """Get delay statistics"""
        if self.command_count == 0:
            return "No commands sent yet"
        
        avg_delay = self.total_delay_time / self.command_count
        return (f"Commands sent: {self.command_count}\n"
                f"Total delay time: {self.total_delay_time:.2f}s\n"
                f"Average delay: {avg_delay:.2f}s")
