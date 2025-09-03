"""
System utilities for AI CLI.
"""

import os
import shutil
import subprocess
from typing import Optional

from .config import CLIPBOARD_COMMANDS
from .exceptions import ClipboardError, SystemInfoError


class SystemUtils:
    """Utilities for system operations."""
    
    def get_system_info(self) -> str:
        """
        Get comprehensive system information including OS details, shell, and available tools.
        
        Returns:
            System information string with OS details, shell, and tool availability.
            
        Raises:
            SystemInfoError: If system information cannot be retrieved.
        """
        try:
            # Get base system info
            result = subprocess.run(
                ['uname', '-a'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode != 0:
                raise SystemInfoError("uname command failed")
            
            system_info = result.stdout.strip()
            
            # Get shell information
            shell = os.environ.get('SHELL', 'unknown')
            
            # Check for available tools and their versions
            tools_info = []
            
            # Check Node.js
            node_info = self._get_tool_version('node', ['--version'])
            tools_info.append(f"Node: {node_info}")
            
            # Check Python (try python3 first, then python)
            python_info = self._get_tool_version('python3', ['--version'])
            if python_info == 'not installed':
                python_info = self._get_tool_version('python', ['--version'])
                if python_info != 'not installed':
                    python_info = f"python {python_info.split(' ', 1)[1]}"  # Remove 'Python' prefix
            else:
                python_info = f"python3 {python_info.split(' ', 1)[1]}"  # Remove 'Python' prefix
            tools_info.append(f"Python: {python_info}")
            
            # Check Lua
            lua_info = self._get_tool_version('lua', ['-v'])
            tools_info.append(f"Lua: {lua_info}")
            
            # Format the complete system information
            return f"""System: {system_info}
Shell: {shell}
{chr(10).join(tools_info)}"""
            
        except subprocess.TimeoutExpired:
            raise SystemInfoError("uname command timed out")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise SystemInfoError(f"Failed to get system info: {e}")
    
    def _get_tool_version(self, tool: str, version_args: list) -> str:
        """
        Get version information for a specific tool.
        
        Args:
            tool: The command name to check.
            version_args: Arguments to get version (e.g., ['--version']).
            
        Returns:
            Version string if available, 'not installed' otherwise.
        """
        if not shutil.which(tool):
            return 'not installed'
        
        try:
            result = subprocess.run(
                [tool] + version_args,
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                # Get first line and clean it up
                version_line = result.stdout.strip().split('\n')[0]
                return version_line
            else:
                # Some tools output version to stderr (like lua -v)
                version_line = result.stderr.strip().split('\n')[0] if result.stderr else 'version unknown'
                return version_line
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return f'{tool} installed (version unknown)'
    
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