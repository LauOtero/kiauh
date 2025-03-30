# Run a shell command via gcode
#
# Copyright (C) 2019  Eric Callahan <arksine.code@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import os
import shlex
import subprocess
import logging
import sys
import re
import time
from typing import Optional, List, Tuple, Any, Dict


class ShellCommand:
    """Execute shell commands via G-Code in Klipper.
    
    This class allows running shell commands from the 3D printer interface
    through G-Code commands, with configurable timeout and verbosity.
    
    Features:
    - Command execution with timeout protection
    - Verbose output mode for debugging
    - Command history logging
    - Security restrictions for command execution
    - Support for complex command arguments
    - Cross-platform encoding handling
    """
    def __init__(self, config):
        self.name = config.get_name().split()[-1]
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object("gcode")
        
        # Parse and prepare command
        cmd = config.get("command")
        cmd = os.path.expanduser(cmd)
        self.command = shlex.split(cmd)
        
        # Configuration parameters
        self.timeout = config.getfloat("timeout", 2.0, above=0.0)
        self.verbose = config.getboolean("verbose", True)
        self.proc_fd = None
        self.partial_output = ""
        
        # Security options
        self.allow_any_params = config.getboolean("allow_any_params", False)
        self.allowed_params_pattern = config.get("allowed_params_pattern", "")
        if self.allowed_params_pattern:
            try:
                self.allowed_params_regex = re.compile(self.allowed_params_pattern)
            except re.error as e:
                raise config.error(f"Invalid regex pattern for allowed_params_pattern: {str(e)}")
        else:
            self.allowed_params_regex = None
            
        # Command history logging
        self.enable_logging = config.getboolean("enable_logging", False)
        self.max_history = config.getint("max_history", 10, minval=0, maxval=100)
        self.command_history = []
        
        # Working directory option
        self.working_dir = config.get("working_dir", "")
        if self.working_dir:
            self.working_dir = os.path.expanduser(self.working_dir)
            if not os.path.isdir(self.working_dir):
                raise config.error(f"Working directory does not exist: {self.working_dir}")
        
        # Environment variables
        self.env_vars = {}
        env_vars_str = config.get("env_vars", "")
        if env_vars_str:
            try:
                for var_def in shlex.split(env_vars_str):
                    if '=' in var_def:
                        key, value = var_def.split('=', 1)
                        self.env_vars[key] = value
            except ValueError as e:
                raise config.error(f"Invalid environment variables format: {str(e)}")
        
        # Register the G-Code commands
        self.gcode.register_mux_command(
            "RUN_SHELL_COMMAND",
            "CMD",
            self.name,
            self.cmd_RUN_SHELL_COMMAND,
            desc=self.cmd_RUN_SHELL_COMMAND_help,
        )
        
        if self.enable_logging:
            self.gcode.register_mux_command(
                "SHELL_COMMAND_HISTORY",
                "CMD",
                self.name,
                self.cmd_SHELL_COMMAND_HISTORY,
                desc=self.cmd_SHELL_COMMAND_HISTORY_help,
            )

    def _process_output(self, eventime) -> None:
        """Process output from the running command.
        
        Args:
            eventime: Event time from the reactor
            
        Returns:
            None
        """
        if self.proc_fd is None:
            return
            
        try:
            data = os.read(self.proc_fd, 4096)
        except (OSError, IOError) as e:
            logging.warning("Error reading command output: %s", str(e))
            return
        except Exception as e:
            logging.exception("Unexpected error processing command output: %s", str(e))
            return
            
        try:
            # Handle different encoding scenarios
            try:
                decoded_data = data.decode('utf-8')
            except UnicodeDecodeError:
                # Fall back to system default encoding or latin-1 if utf-8 fails
                decoded_data = data.decode(sys.getdefaultencoding(), errors='replace')
                
            data = self.partial_output + decoded_data
            
            # Process the output line by line
            if "\n" not in data:
                self.partial_output = data
                return
            elif data[-1] != "\n":
                split = data.rfind("\n") + 1
                self.partial_output = data[split:]
                data = data[:split]
            else:
                self.partial_output = ""
                
            # Send the processed output
            self.gcode.respond_info(data)
        except Exception as e:
            logging.exception("Error processing command output: %s", str(e))

    cmd_RUN_SHELL_COMMAND_help = "Run a shell command from G-Code"
    
    cmd_SHELL_COMMAND_HISTORY_help = "Show history of executed shell commands"
    
    def cmd_SHELL_COMMAND_HISTORY(self, params) -> None:
        """G-Code command handler for SHELL_COMMAND_HISTORY.
        
        Shows the history of executed commands with their parameters,
        exit codes, and execution times.
        
        Args:
            params: Parameters from the G-Code command
            
        Returns:
            None
        """
        if not self.enable_logging:
            self.gcode.respond_info(f"Command history logging is not enabled for {self.name}")
            return
            
        if not self.command_history:
            self.gcode.respond_info(f"No command history available for {self.name}")
            return
            
        count = params.get_int("COUNT", len(self.command_history), minval=1, 
                               maxval=len(self.command_history))
        
        history = self.command_history[-count:]
        
        output = [f"Command history for {self.name} (last {count} entries):"]
        
        for i, entry in enumerate(history):
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", 
                                     time.localtime(entry["timestamp"]))
            params_str = " ".join(entry["params"]) if entry["params"] else "(none)"
            
            if entry["timed_out"]:
                status = "TIMEOUT"
            else:
                status = f"EXIT {entry['exit_code']}"
                
            output.append(f"{i+1}. [{timestamp}] Params: {params_str} | "
                         f"Status: {status} | Duration: {entry['duration']:.2f}s")
            
        self.gcode.respond_info("\n".join(output))

    def _validate_params(self, gcode_params: List[str]) -> None:
        """Validate command parameters against security restrictions.
        
        Args:
            gcode_params: List of command parameters to validate
            
        Raises:
            GCodeError: If parameters violate security restrictions
        """
        if self.allow_any_params:
            return
            
        if self.allowed_params_regex:
            for param in gcode_params:
                if not self.allowed_params_regex.match(param):
                    raise self.gcode.error(
                        f"Parameter '{param}' does not match allowed pattern '{self.allowed_params_pattern}'"
                    )
        elif gcode_params:
            raise self.gcode.error(
                f"Command {self.name} does not allow parameters. Set allow_any_params=True or configure allowed_params_pattern."
            )
    
    def _log_command(self, gcode_params: List[str], exit_code: Optional[int], duration: float) -> None:
        """Log command execution to history.
        
        Args:
            gcode_params: Parameters passed to the command
            exit_code: Exit code of the command, or None if timed out
            duration: Execution duration in seconds
        """
        if not self.enable_logging:
            return
            
        timestamp = time.time()
        log_entry = {
            "timestamp": timestamp,
            "params": gcode_params,
            "exit_code": exit_code,
            "duration": duration,
            "timed_out": exit_code is None
        }
        
        self.command_history.append(log_entry)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
    
    def cmd_RUN_SHELL_COMMAND(self, params) -> None:
        """G-Code command handler for RUN_SHELL_COMMAND.
        
        Executes the configured shell command with optional parameters
        passed from G-Code.
        
        Args:
            params: Parameters from the G-Code command
            
        Returns:
            None
            
        Raises:
            GCodeError: If the command fails to execute
        """
        # Parse parameters from G-Code
        gcode_params = params.get("PARAMS", "")
        raw_params = gcode_params
        
        try:
            gcode_params = shlex.split(gcode_params)
        except ValueError as e:
            raise self.gcode.error(f"Invalid parameters for command {self.name}: {str(e)}")
        
        # Validate parameters against security restrictions
        try:
            self._validate_params(gcode_params)
        except Exception as e:
            logging.error(f"Parameter validation failed: {str(e)}")
            raise
            
        reactor = self.printer.get_reactor()
        hdl = None
        proc = None
        start_time = time.time()
        
        try:
            # Prepare environment variables
            env = os.environ.copy()
            if self.env_vars:
                env.update(self.env_vars)
            
            # Start the subprocess with proper error handling
            try:
                proc = subprocess.Popen(
                    self.command + gcode_params,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=1,  # Line buffered
                    universal_newlines=False,  # We'll handle decoding ourselves
                    cwd=self.working_dir if self.working_dir else None,
                    env=env
                )
            except (OSError, subprocess.SubprocessError) as e:
                logging.exception(f"shell_command: Command {self.name} failed: {str(e)}")
                raise self.gcode.error(f"Error running command {self.name}: {str(e)}")
                
            # Set up output handling if verbose mode is enabled
            if self.verbose and proc.stdout:
                self.proc_fd = proc.stdout.fileno()
                cmd_info = f"Running Command {self.name}"
                if raw_params:
                    cmd_info += f" with params: {raw_params}"
                self.gcode.respond_info(f"{cmd_info}...")
                hdl = reactor.register_fd(self.proc_fd, self._process_output)
                
            # Wait for command completion with timeout
            eventtime = reactor.monotonic()
            endtime = eventtime + self.timeout
            complete = False
            
            while eventtime < endtime:
                eventtime = reactor.pause(eventtime + 0.05)
                if proc.poll() is not None:
                    complete = True
                    break
                    
            # Handle command timeout
            if not complete:
                proc.terminate()
                # Give it a moment to terminate gracefully
                try:
                    proc.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    proc.kill()
            
            # Calculate execution duration
            duration = time.time() - start_time
            
            # Log command execution
            exit_code = proc.returncode if complete else None
            self._log_command(gcode_params, exit_code, duration)
                    
            # Process any remaining output and clean up
            if self.verbose:
                if self.partial_output:
                    self.gcode.respond_info(self.partial_output)
                    self.partial_output = ""
                    
                # Report command status
                if complete:
                    exit_code = proc.returncode
                    status = "successfully" if exit_code == 0 else f"with error code {exit_code}"
                    msg = f"Command {self.name} finished {status} (duration: {duration:.2f}s)"
                else:
                    msg = f"Command {self.name} timed out after {self.timeout}s and was terminated"
                    
                self.gcode.respond_info(msg)
                
                # Clean up resources
                if hdl is not None:
                    reactor.unregister_fd(hdl)
                self.proc_fd = None
                
        except Exception as e:
            # Ensure cleanup in case of unexpected errors
            if hdl is not None:
                reactor.unregister_fd(hdl)
            self.proc_fd = None
            if proc is not None and proc.poll() is None:
                proc.terminate()
            logging.exception(f"Unexpected error in shell command {self.name}: {str(e)}")
            raise self.gcode.error(f"Error in command {self.name}: {str(e)}")


def load_config_prefix(config) -> ShellCommand:
    """Configuration hook for Klipper.
    
    Args:
        config: Klipper config object
        
    Returns:
        ShellCommand instance
    """
    return ShellCommand(config)
