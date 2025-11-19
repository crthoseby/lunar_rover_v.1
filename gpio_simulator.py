"""
GPIO Simulator for testing on non-Raspberry Pi systems
"""

# Constants
BCM = 'BCM'
OUT = 'OUT'
IN = 'IN'
LOW = 0
HIGH = 1
RISING = 'RISING'
FALLING = 'FALLING'

# Internal state
_mode = None
_warnings = True
_pin_states = {}
_pwm_instances = {}


def setmode(mode):
    """Set GPIO mode"""
    global _mode
    _mode = mode
    print(f"[GPIO SIMULATOR] Mode set to {mode}")


def setwarnings(flag):
    """Set warnings flag"""
    global _warnings
    _warnings = flag


def setup(pin, mode, initial=LOW):
    """Setup a pin"""
    _pin_states[pin] = initial
    print(f"[GPIO SIMULATOR] Pin {pin} set to {mode}, initial={initial}")


def output(pin, value):
    """Set output value"""
    _pin_states[pin] = value


def input(pin):
    """Read input value"""
    return _pin_states.get(pin, LOW)


def cleanup(pins=None):
    """Cleanup GPIO"""
    global _pin_states, _pwm_instances
    if pins:
        for pin in pins if isinstance(pins, list) else [pins]:
            if pin in _pin_states:
                del _pin_states[pin]
    else:
        _pin_states = {}
        _pwm_instances = {}
    print("[GPIO SIMULATOR] GPIO cleanup complete")


class PWM:
    """PWM Simulator"""
    
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.duty_cycle = 0
        self.running = False
        _pwm_instances[pin] = self
        print(f"[GPIO SIMULATOR] PWM created on pin {pin} at {frequency}Hz")
    
    def start(self, duty_cycle):
        """Start PWM"""
        self.duty_cycle = duty_cycle
        self.running = True
        if duty_cycle > 0:
            print(f"[GPIO SIMULATOR] PWM pin {self.pin} started at {duty_cycle}% duty cycle")
    
    def ChangeDutyCycle(self, duty_cycle):
        """Change duty cycle"""
        old_duty = self.duty_cycle
        self.duty_cycle = duty_cycle
        if duty_cycle > 0 and old_duty == 0:
            print(f"[GPIO SIMULATOR] PWM pin {self.pin} → {duty_cycle}%")
        elif duty_cycle == 0 and old_duty > 0:
            print(f"[GPIO SIMULATOR] PWM pin {self.pin} → OFF")
    
    def stop(self):
        """Stop PWM"""
        self.running = False
        self.duty_cycle = 0
        print(f"[GPIO SIMULATOR] PWM pin {self.pin} stopped")
