from mcp.server.fastmcp import FastMCP
import os
import pathlib
import sys

mcp = FastMCP("DesktopFileSystem")

BASE_DIR = pathlib.Path(os.path.expanduser("~/Desktop")).resolve()

def _validate_path(rel_path: str) -> pathlib.Path:
    """Validate and return a safe path within the desktop directory."""
    # Convert relative path to Path object and resolve it
    rel_path_obj = pathlib.Path(rel_path)
    target = BASE_DIR / rel_path_obj
    
    # Ensure the target path is within the base directory
    try:
        target = target.resolve()
        if not str(target).startswith(str(BASE_DIR)):
            raise ValueError(f"Access denied: {rel_path} - path outside desktop directory")
        return target
    except (RuntimeError, OSError) as e:
        raise ValueError(f"Invalid path: {rel_path} - {str(e)}")

@mcp.tool()
def list_items() -> list[dict]:
    """List all items in the desktop directory"""
    items = []
    for p in BASE_DIR.iterdir():
        items.append({
            "name": p.name,
            "is_dir": p.is_dir()
        })
    return items

@mcp.tool()
def create(path: str, is_dir: bool = False) -> str:
    """Create a folder or file on the desktop."""
    target = _validate_path(path)
    if is_dir:
        target.mkdir(parents=True, exist_ok=True)
        return f"Directory created: {target}"
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch(exist_ok=True)
        return f"File created: {target}"

@mcp.tool()
def append_to_file(path: str, content: str) -> str:
    """Append content to a file on the desktop."""
    target = _validate_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if target.is_dir():
        raise IsADirectoryError(f"Path is a directory: {path}")
    with open(target, "a", encoding="utf-8") as f:
        f.write(content)
    return f"Content appended to {path}"

@mcp.tool()
def read_file(path: str) -> str:
    """Read the content of a file on the desktop."""
    target = _validate_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if target.is_dir():
        raise IsADirectoryError(f"Path is a directory: {path}")
    with open(target, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()