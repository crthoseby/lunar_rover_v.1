"""
Transmission Log Manager for Lunar Rover
Saves console logs to files with rotation and export capabilities
"""

import os
import time
from datetime import datetime, timedelta
import config


class LogManager:
    """Manages transmission logs with file saving and rotation"""
    
    def __init__(self, log_dir=None):
        """Initialize log manager"""
        self.log_dir = log_dir or config.LOG_DIRECTORY
        self.max_size = config.MAX_LOG_SIZE
        self.retention_days = config.LOG_RETENTION_DAYS
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"✓ Created log directory: {self.log_dir}")
        
        # Current log file
        self.current_log = None
        self.log_entries = []
        self._create_new_log()
        
        print(f"✓ Log manager initialized: {self.log_dir}")
    
    def _create_new_log(self):
        """Create a new log file"""
        timestamp = datetime.now().strftime(config.LOG_FILENAME_FORMAT)
        self.current_log = os.path.join(self.log_dir, timestamp)
        
        # Write header
        with open(self.current_log, 'w') as f:
            f.write("="*80 + "\n")
            f.write("LUNAR ROVER TRANSMISSION LOG\n")
            f.write(f"Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
        
        print(f"📝 New log file created: {self.current_log}")
    
    def _check_rotation(self):
        """Check if log file needs rotation"""
        if not os.path.exists(self.current_log):
            return
        
        file_size = os.path.getsize(self.current_log)
        if file_size >= self.max_size:
            print(f"📝 Log file size limit reached ({file_size} bytes), rotating...")
            self._create_new_log()
    
    def log(self, message, log_type='info'):
        """
        Add entry to transmission log
        
        Args:
            message: Log message
            log_type: Type of log (info, command, success, error, warning)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Format log entry
        type_prefix = {
            'info': '[INFO]',
            'command': '[CMD]',
            'success': '[OK]',
            'error': '[ERROR]',
            'warning': '[WARN]'
        }.get(log_type, '[INFO]')
        
        log_entry = f"{timestamp} {type_prefix} {message}"
        
        # Store in memory
        self.log_entries.append({
            'timestamp': timestamp,
            'type': log_type,
            'message': message,
            'full_entry': log_entry
        })
        
        # Keep only last 1000 entries in memory
        if len(self.log_entries) > 1000:
            self.log_entries = self.log_entries[-1000:]
        
        # Write to file
        try:
            with open(self.current_log, 'a') as f:
                f.write(log_entry + '\n')
            
            # Check if rotation is needed
            self._check_rotation()
        except Exception as e:
            print(f"⚠ Failed to write log: {e}")
    
    def get_recent_logs(self, count=50):
        """Get most recent log entries"""
        return self.log_entries[-count:]
    
    def export_log(self, filename=None):
        """
        Export current session log
        
        Args:
            filename: Output filename (optional)
        
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exported_log_{timestamp}.txt"
        
        export_path = os.path.join(self.log_dir, filename)
        
        try:
            # Copy current log
            if os.path.exists(self.current_log):
                with open(self.current_log, 'r') as src:
                    with open(export_path, 'w') as dst:
                        dst.write(src.read())
                
                print(f"✓ Log exported: {export_path}")
                return export_path
            else:
                print("⚠ No current log file to export")
                return None
        except Exception as e:
            print(f"✗ Export failed: {e}")
            return None
    
    def get_log_files(self):
        """Get list of all log files"""
        try:
            files = []
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.log_dir, filename)
                    stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'path': filepath,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            return files
        except Exception as e:
            print(f"⚠ Failed to list log files: {e}")
            return []
    
    def cleanup_old_logs(self):
        """Remove log files older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        removed_count = 0
        
        try:
            for filename in os.listdir(self.log_dir):
                if not filename.endswith('.txt'):
                    continue
                
                filepath = os.path.join(self.log_dir, filename)
                
                # Skip current log
                if filepath == self.current_log:
                    continue
                
                # Check file age
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_date:
                    os.remove(filepath)
                    removed_count += 1
                    print(f"🗑️ Removed old log: {filename}")
            
            if removed_count > 0:
                print(f"✓ Cleaned up {removed_count} old log file(s)")
            
        except Exception as e:
            print(f"⚠ Cleanup failed: {e}")
    
    def get_stats(self):
        """Get logging statistics"""
        total_size = 0
        file_count = 0
        
        try:
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.log_dir, filename)
                    total_size += os.path.getsize(filepath)
                    file_count += 1
        except:
            pass
        
        return {
            'total_files': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'current_log': os.path.basename(self.current_log) if self.current_log else None,
            'entries_in_memory': len(self.log_entries)
        }
    
    def clear_session(self):
        """Clear current session log entries from memory"""
        self.log_entries = []
        print("✓ Session log cleared from memory")


# Test log manager
if __name__ == '__main__':
    print("Testing Log Manager...")
    logger = LogManager()
    
    # Add some test entries
    logger.log("Rover system initialized", "info")
    logger.log("Moving forward", "command")
    logger.log("Command executed successfully", "success")
    logger.log("Low battery warning", "warning")
    logger.log("Connection lost", "error")
    
    # Export log
    export_path = logger.export_log()
    
    # Get stats
    stats = logger.get_stats()
    print(f"\nLog Statistics:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total size: {stats['total_size_mb']} MB")
    print(f"  Current log: {stats['current_log']}")
    print(f"  Entries in memory: {stats['entries_in_memory']}")
    
    # List files
    print("\nLog Files:")
    for file in logger.get_log_files():
        print(f"  {file['filename']} - {file['size']} bytes - {file['modified']}")
    
    print("\nTest complete!")
