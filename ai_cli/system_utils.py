"""
System utilities for AI CLI.
"""

import shutil
import subprocess
from typing import Optional

from .config import CLIPBOARD_COMMANDS
from .exceptions import ClipboardError, SystemInfoError


class SystemUtils:
    """Utilities for system operations."""
    
    def get_system_info(self) -> str:
        """
        Get system information using uname -a to help the AI target the correct platform.
        
        Returns:
            System information string.
            
        Raises:
            SystemInfoError: If system information cannot be retrieved.
        """
        try:
            result = subprocess.run(
                ['uname', '-a'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise SystemInfoError("uname command failed")
        except subprocess.TimeoutExpired:
            raise SystemInfoError("uname command timed out")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise SystemInfoError(f"Failed to get system info: {e}")
    
    def copy_to_clipboard(self, text: str) -> None:
        """
        Copy text to system clipboard using available tools.
        
        Args:
            text: The text to copy to clipboard.
            
        Raises:
            ClipboardError: If copying to clipboard fails.
        """
        for tool, command in CLIPBOARD_COMMANDS.items():
            if shutil.which(tool):
                try:
                    subprocess.run(
                        command, 
                        input=text, 
                        text=True, 
                        check=True,
                        timeout=5
                    )
                    return  # Success
                except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
                    # Try next tool
                    continue
        
        # If we get here, no clipboard tool worked
        raise ClipboardError("No suitable clipboard tool found or all failed")
    
    def is_clipboard_available(self) -> bool:
        """
        Check if clipboard functionality is available on this system.
        
        Returns:
            True if clipboard is available, False otherwise.
        """
        return any(shutil.which(tool) for tool in CLIPBOARD_COMMANDS.keys()) 