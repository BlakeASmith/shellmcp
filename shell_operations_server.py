"""Generated FastMCP server from YAML configuration."""

import os
import subprocess
import tempfile
import shlex
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP
from jinja2 import Template, Environment

def execute_command(cmd: str, env_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Execute a shell command and return the result."""
    try:
        # Prepare environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        # Execute command
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env=env,
            timeout=300  # 5 minute timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 5 minutes",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def render_template(template_str: str, **kwargs) -> str:
    """Render Jinja2 template with provided variables."""
    try:
        # Add built-in functions
        context = {
            'now': datetime.now,
            **kwargs
        }
        
        template = Template(template_str)
        return template.render(**context)
    except Exception as e:
        raise ValueError(f"Template rendering error: {e}")

# Initialize FastMCP server
mcp = FastMCP(name="shell-operations")

# Server configuration
SERVER_NAME = "shell-operations"
SERVER_DESC = "Common shell operations for file management, system info, and text processing"
SERVER_VERSION = "1.0.0"


@mcp.tool()
def list_files(path: str = ".") -> Dict[str, Any]:
    """
    List files and directories with detailed information
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""ls -la {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in list_files: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def find_files(pattern: str, path: str = ".") -> Dict[str, Any]:
    """
    Find files matching a pattern
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    - pattern (string): Search pattern or regex
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""find {{path}} -name '{{pattern}}' -type f""", path=path, pattern=pattern)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in find_files: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def find_directories(pattern: str, path: str = ".") -> Dict[str, Any]:
    """
    Find directories matching a pattern
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    - pattern (string): Search pattern or regex
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""find {{path}} -name '{{pattern}}' -type d""", path=path, pattern=pattern)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in find_directories: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def grep_text(pattern: str, path: str = ".", recursive: bool = False) -> Dict[str, Any]:
    """
    Search for text patterns in files
    
    Parameters:
    - pattern (string): Search pattern or regex
    - path (string): Directory or file path
      Default: .
    - recursive (boolean): Perform operation recursively
      Default: False
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""grep -r{{ 'n' if recursive else '' }} '{{pattern}}' {{path}}""", pattern=pattern, path=path, recursive=recursive)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in grep_text: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def count_lines(path: str = ".") -> Dict[str, Any]:
    """
    Count lines in a file
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""wc -l {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in count_lines: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def file_size(path: str = ".") -> Dict[str, Any]:
    """
    Get file or directory size
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""du -h {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in file_size: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def disk_usage() -> Dict[str, Any]:
    """
    Show disk usage information
    
    Help:
    Usage: df [OPTION]... [FILE]...
    Show information about the file system on which each FILE resides,
    or all file systems by default.

    Mandatory arguments to long options are mandatory for short options too.
      -a, --all             include pseudo, duplicate, inaccessible file systems
      -B, --block-size=SIZE  scale sizes by SIZE before printing them; e.g.,
                               '-BM' prints sizes in units of 1,048,576 bytes;
                               see SIZE format below
      -h, --human-readable  print sizes in powers of 1024 (e.g., 1023M)
      -H, --si              print sizes in powers of 1000 (e.g., 1.1G)
      -i, --inodes          list inode information instead of block usage
      -k                    like --block-size=1K
      -l, --local           limit listing to local file systems
          --no-sync         do not invoke sync before getting usage info (default)
          --output[=FIELD_LIST]  use the output format defined by FIELD_LIST,
                                   or print all fields if FIELD_LIST is omitted.
      -P, --portability     use the POSIX output format
          --sync            invoke sync before getting usage info
          --total           elide all entries insignificant to available space,
                              and produce a grand total
      -t, --type=TYPE       limit listing to file systems of type TYPE
      -T, --print-type      print file system type
      -x, --exclude-type=TYPE   limit listing to file systems not of type TYPE
      -v                    (ignored)
          --help     display this help and exit
          --version  output version information and exit

    Display values are in units of the first available SIZE from --block-size,
    and the DF_BLOCK_SIZE, BLOCK_SIZE and BLOCKSIZE environment variables.
    Otherwise, units default to 1024 bytes (or 512 if POSIXLY_CORRECT is set).

    The SIZE argument is an integer and optional unit (example: 10K is 10*1024).
    Units are K,M,G,T,P,E,Z,Y (powers of 1024) or KB,MB,... (powers of 1000).
    Binary prefixes can be used, too: KiB=K, MiB=M, and so on.

    FIELD_LIST is a comma-separated list of columns to be included.  Valid
    field names are: 'source', 'fstype', 'itotal', 'iused', 'iavail', 'ipcent',
    'size', 'used', 'avail', 'pcent', 'file' and 'target' (see info page).

    GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
    Report any translation bugs to <https://translationproject.org/team/>
    Full documentation <https://www.gnu.org/software/coreutils/df>
    or available locally via: info '(coreutils) df invocation'
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""df -h""", )
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in disk_usage: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def memory_info() -> Dict[str, Any]:
    """
    Show memory usage information
    
    Help:
    Usage:
     free [options]

    Options:
     -b, --bytes         show output in bytes
         --kilo          show output in kilobytes
         --mega          show output in megabytes
         --giga          show output in gigabytes
         --tera          show output in terabytes
         --peta          show output in petabytes
     -k, --kibi          show output in kibibytes
     -m, --mebi          show output in mebibytes
     -g, --gibi          show output in gibibytes
         --tebi          show output in tebibytes
         --pebi          show output in pebibytes
     -h, --human         show human-readable output
         --si            use powers of 1000 not 1024
     -l, --lohi          show detailed low and high memory statistics
     -t, --total         show total for RAM + swap
     -s N, --seconds N   repeat printing every N seconds
     -c N, --count N     repeat printing N times, then exit
     -w, --wide          wide output

         --help     display this help and exit
     -V, --version  output version information and exit

    For more details see free(1).
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""free -h""", )
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in memory_info: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def process_list() -> Dict[str, Any]:
    """
    List running processes
    
    Help:
    Usage:
     ps [options]

     Try 'ps --help <simple|list|output|threads|misc|all>'
      or 'ps --help <s|l|o|t|m|a>'
     for additional help text.

    For more details see ps(1).
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""ps aux""", )
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in process_list: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def system_info() -> Dict[str, Any]:
    """
    Show system information
    
    Help:
    Usage: uname [OPTION]...
    Print certain system information.  With no OPTION, same as -s.

      -a, --all                print all information, in the following order,
                                 except omit -p and -i if unknown:
      -s, --kernel-name        print the kernel name
      -n, --nodename           print the network node hostname
      -r, --kernel-release     print the kernel release
      -v, --kernel-version     print the kernel version
      -m, --machine            print the machine hardware name
      -p, --processor          print the processor type (non-portable)
      -i, --hardware-platform  print the hardware platform (non-portable)
      -o, --operating-system   print the operating system
          --help     display this help and exit
          --version  output version information and exit

    GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
    Report any translation bugs to <https://translationproject.org/team/>
    Full documentation <https://www.gnu.org/software/coreutils/uname>
    or available locally via: info '(coreutils) uname invocation'
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""uname -a""", )
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in system_info: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def current_user() -> Dict[str, Any]:
    """
    Show current user
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""whoami""", )
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in current_user: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def current_directory() -> Dict[str, Any]:
    """
    Show current working directory
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""pwd""", )
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in current_directory: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def create_directory(path: str = ".") -> Dict[str, Any]:
    """
    Create directory (with parent directories if needed)
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""mkdir -p {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in create_directory: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def copy_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Copy file or directory
    
    Parameters:
    - source (string): Source file or directory path
    - destination (string): Destination file or directory path
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""cp {{source}} {{destination}}""", source=source, destination=destination)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in copy_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def move_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Move or rename file or directory
    
    Parameters:
    - source (string): Source file or directory path
    - destination (string): Destination file or directory path
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""mv {{source}} {{destination}}""", source=source, destination=destination)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in move_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def remove_file(path: str = ".") -> Dict[str, Any]:
    """
    Remove file (force, no error if not found)
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""rm -f {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in remove_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def remove_directory(path: str = ".") -> Dict[str, Any]:
    """
    Remove directory and all contents (force, recursive)
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""rm -rf {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in remove_directory: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def cat_file(path: str = ".") -> Dict[str, Any]:
    """
    Display file contents
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""cat {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in cat_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def head_file(path: str = ".", lines: float = 10) -> Dict[str, Any]:
    """
    Show first N lines of a file
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    - lines (number): Number of lines to show
      Default: 10
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""head -n {{lines}} {{path}}""", path=path, lines=lines)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in head_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def tail_file(path: str = ".", lines: float = 10) -> Dict[str, Any]:
    """
    Show last N lines of a file
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    - lines (number): Number of lines to show
      Default: 10
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""tail -n {{lines}} {{path}}""", path=path, lines=lines)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in tail_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def sort_file(path: str = ".") -> Dict[str, Any]:
    """
    Sort lines in a file
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""sort {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in sort_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def unique_lines(path: str = ".") -> Dict[str, Any]:
    """
    Get unique lines from a file
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""sort {{path}} | uniq""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in unique_lines: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def word_count(path: str = ".") -> Dict[str, Any]:
    """
    Count words in a file
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""wc -w {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in word_count: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def character_count(path: str = ".") -> Dict[str, Any]:
    """
    Count characters in a file
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""wc -c {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in character_count: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def compress_file(path: str = ".") -> Dict[str, Any]:
    """
    Compress file using gzip
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""gzip {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in compress_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def decompress_file(path: str = ".") -> Dict[str, Any]:
    """
    Decompress gzip file
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""gunzip {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in decompress_file: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def archive_directory(output: str, path: str = ".") -> Dict[str, Any]:
    """
    Create compressed tar archive of directory
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    - output (string): Output file path
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""tar -czf {{output}} {{path}}""", path=path, output=output)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in archive_directory: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def extract_archive(path: str = ".") -> Dict[str, Any]:
    """
    Extract compressed tar archive
    
    Parameters:
    - path (string): Directory or file path
      Default: .
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""tar -xzf {{path}}""", path=path)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in extract_archive: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def network_connections() -> Dict[str, Any]:
    """
    Show network connections
    
    Help:
    
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""netstat -tuln""", )
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in network_connections: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def ping_host(host: str) -> Dict[str, Any]:
    """
    Ping a host 4 times
    
    Parameters:
    - host (string): Hostname or IP address to ping
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""ping -c 4 {{host}}""", host=host)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in ping_host: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def environment_vars() -> Dict[str, Any]:
    """
    Show environment variables
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""env""", )
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in environment_vars: {str(e)}",
            "returncode": -1
        }


@mcp.tool()
def set_environment(name: str, value: str) -> Dict[str, Any]:
    """
    Set environment variable
    
    Parameters:
    - name (string): Environment variable name
    - value (string): Environment variable value
    
    Returns:
        Dict[str, Any]: Command execution result with 'success', 'stdout', 'stderr', and 'returncode' fields.
    """
    try:
        
        # Render command template
        cmd = render_template("""export {{name}}={{value}}""", name=name, value=value)
        
        # Execute command
        env_vars = {}
        result = execute_command(cmd, env_vars)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error in set_environment: {str(e)}",
            "returncode": -1
        }


# Resource handlers

@mcp.resource("file:///tmp/system-status.txt")
def system_status() -> str:
    """
    Current system status including disk, memory, and process information
    
    Returns:
        str: The resource content.
    """
    try:
        
        # Execute command
        cmd = render_template("""echo '=== DISK USAGE ===' && df -h && echo -e '
=== MEMORY USAGE ===' && free -h && echo -e '
=== LOAD AVERAGE ===' && uptime && echo -e '
=== RUNNING PROCESSES ===' && ps aux --sort=-%cpu | head -10""", )
        env_vars = {}
        result = execute_command(cmd, env_vars)
        if not result["success"]:
            raise ValueError(f"Command failed: {result['stderr']}")
        content = result["stdout"]
        
        return content
    except Exception as e:
        raise ValueError(f"Error in system_status: {str(e)}")


@mcp.resource("file:///tmp/file-info.txt")
def file_info() -> str:
    """
    Detailed information about files in current directory
    
    Returns:
        str: The resource content.
    """
    try:
        
        # Execute command
        cmd = render_template("""ls -la && echo -e '
=== FILE TYPES ===' && file * 2>/dev/null || echo 'No files to analyze'""", )
        env_vars = {}
        result = execute_command(cmd, env_vars)
        if not result["success"]:
            raise ValueError(f"Command failed: {result['stderr']}")
        content = result["stdout"]
        
        return content
    except Exception as e:
        raise ValueError(f"Error in file_info: {str(e)}")


# Prompt handlers

@mcp.prompt()
def file_analysis(file_list: str, path: str = ".") -> str:
    """
    Helps analyze file system contents and structure
    
    Parameters:
    - path (string): Directory path to analyze
      Default: .
    - file_list (string): List of files to analyze (from ls command output)
    
    Returns:
        str: The generated prompt content.
    """
    try:
        
        # Use direct template content
        content = render_template("""Analyze the following file system information:

Current directory: {{path}}
Files and directories: {{file_list}}

Please provide insights about:
1. File structure and organization
2. File types and sizes
3. Potential organization improvements
4. Security considerations (permissions, sensitive files)
5. Recommendations for cleanup or optimization

If you notice any unusual patterns or potential issues, please highlight them.
""", path=path, file_list=file_list)
        
        return content
    except Exception as e:
        raise ValueError(f"Error in file_analysis: {str(e)}")


@mcp.prompt()
def system_diagnosis(system_info: str, memory_info: str, disk_usage: str, load_average: str, top_processes: str) -> str:
    """
    Helps diagnose system performance and health issues
    
    Parameters:
    - system_info (string): System information from uname command
    - memory_info (string): Memory usage information from free command
    - disk_usage (string): Disk usage information from df command
    - load_average (string): System load average from uptime command
    - top_processes (string): Top processes by CPU usage
    
    Returns:
        str: The generated prompt content.
    """
    try:
        
        # Use direct template content
        content = render_template("""Based on the following system information, please provide a diagnosis:

System Info: {{system_info}}
Memory Usage: {{memory_info}}
Disk Usage: {{disk_usage}}
Load Average: {{load_average}}
Top Processes: {{top_processes}}

Please analyze:
1. Overall system health
2. Performance bottlenecks
3. Resource utilization
4. Potential issues or concerns
5. Recommendations for optimization

If you identify any critical issues, please prioritize them and suggest immediate actions.
""", system_info=system_info, memory_info=memory_info, disk_usage=disk_usage, load_average=load_average, top_processes=top_processes)
        
        return content
    except Exception as e:
        raise ValueError(f"Error in system_diagnosis: {str(e)}")


if __name__ == "__main__":
    print(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    print(f"Description: {SERVER_DESC}")
    mcp.run()