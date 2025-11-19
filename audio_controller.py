"""
Audio Controller for Lunar Rover
Handles audio recording and playback
"""

import time
import wave
import threading
from datetime import datetime
import config

try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠ PyAudio not available - audio disabled")


class AudioController:
    """Audio recording and playback controller"""
    
    def __init__(self):
        """Initialize audio controller"""
        self.enabled = config.AUDIO_ENABLED and AUDIO_AVAILABLE
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.channels = config.AUDIO_CHANNELS
        self.chunk_size = config.AUDIO_CHUNK_SIZE
        
        self.recording = False
        self.playing = False
        self._record_thread = None
        self._play_thread = None
        self.audio = None
        
        if self.enabled:
            try:
                self.audio = pyaudio.PyAudio()
                print("✓ Audio controller initialized")
            except Exception as e:
                print(f"⚠ Audio initialization failed: {e}")
                self.enabled = False
                self.audio = None
        else:
            print("⚠ Audio controller in simulation mode")
    
    def start_recording(self, filename=None):
        """Start recording audio to file"""
        if not self.enabled:
            print("⚠ Audio recording not available")
            return False
        
        if self.recording:
            print("⚠ Already recording")
            return False
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_recording_{timestamp}.wav"
        
        self.recording = True
        self._record_thread = threading.Thread(
            target=self._record_audio,
            args=(filename,),
            daemon=True
        )
        self._record_thread.start()
        print(f"🎤 Recording started: {filename}")
        return True
    
    def stop_recording(self):
        """Stop recording audio"""
        if not self.recording:
            return False
        
        self.recording = False
        if self._record_thread:
            self._record_thread.join(timeout=2)
        print("🎤 Recording stopped")
        return True
    
    def _record_audio(self, filename):
        """Background recording thread"""
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            
            while self.recording:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"⚠ Recording error: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            
            # Save to WAV file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            print(f"✓ Audio saved: {filename}")
            
        except Exception as e:
            print(f"✗ Recording failed: {e}")
            self.recording = False
    
    def play_file(self, filename):
        """Play audio file"""
        if not self.enabled:
            print("⚠ Audio playback not available")
            return False
        
        if self.playing:
            print("⚠ Already playing audio")
            return False
        
        self.playing = True
        self._play_thread = threading.Thread(
            target=self._play_audio,
            args=(filename,),
            daemon=True
        )
        self._play_thread.start()
        return True
    
    def stop_playback(self):
        """Stop audio playback"""
        if not self.playing:
            return False
        
        self.playing = False
        if self._play_thread:
            self._play_thread.join(timeout=2)
        print("🔊 Playback stopped")
        return True
    
    def _play_audio(self, filename):
        """Background playback thread"""
        try:
            with wave.open(filename, 'rb') as wf:
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                data = wf.readframes(self.chunk_size)
                
                while data and self.playing:
                    stream.write(data)
                    data = wf.readframes(self.chunk_size)
                
                stream.stop_stream()
                stream.close()
            
            self.playing = False
            print(f"✓ Playback complete: {filename}")
            
        except Exception as e:
            print(f"✗ Playback failed: {e}")
            self.playing = False
    
    def get_status(self):
        """Get audio controller status"""
        return {
            'enabled': self.enabled,
            'recording': self.recording,
            'playing': self.playing,
            'sample_rate': self.sample_rate,
            'channels': self.channels
        }
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.recording:
            self.stop_recording()
        if self.playing:
            self.stop_playback()
        
        if self.audio:
            try:
                self.audio.terminate()
                print("✓ Audio controller cleaned up")
            except:
                pass


# Test audio controller
if __name__ == '__main__':
    print("Testing Audio Controller...")
    audio = AudioController()
    
    if not audio.enabled:
        print("Audio not available for testing")
        exit()
    
    try:
        print("\nRecording for 5 seconds...")
        audio.start_recording("test_recording.wav")
        time.sleep(5)
        audio.stop_recording()
        
        print("\nPlaying back recording...")
        time.sleep(1)
        audio.play_file("test_recording.wav")
        
        while audio.playing:
            time.sleep(0.1)
        
        print("\nTest complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        audio.cleanup()
