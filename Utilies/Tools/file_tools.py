"""
Atulya AI - File Tools (v0.1.0)
Full production file I/O tools
"""

import os
import json
import csv
import yaml
import shutil
import zipfile
import hashlib
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import mimetypes
from datetime import datetime

from .tool_registry import tool

@tool(description="Read text content from a file", category="file_io")
def read_file(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Read content from a text file"""
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {path}",
                "content": None
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {path}",
                "content": None
            }
        
        # Get file info
        stat = path.stat()
        mime_type, _ = mimetypes.guess_type(str(path))
        
        # Read content based on file type
        if mime_type and mime_type.startswith('text/'):
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
        else:
            # For binary files, return hex representation
            with open(file_path, 'rb') as f:
                content = f.read().hex()
        
        return {
            "success": True,
            "content": content,
            "file_path": str(file_path),
            "file_size": stat.st_size,
            "mime_type": mime_type,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "encoding": encoding
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "content": None
        }

@tool(description="Write content to a file", category="file_io")
def write_file(file_path: str, content: str, encoding: str = "utf-8", 
               mode: str = "w") -> Dict[str, Any]:
    """Write content to a file"""
    try:
        file_path = Path(file_path)
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        
        # Get file info
        stat = file_path.stat()
        
        return {
            "success": True,
            "file_path": str(file_path),
            "bytes_written": len(content.encode(encoding)),
            "file_size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool(description="List files and directories", category="file_io")
def list_directory(directory_path: str = ".", pattern: str = "*", 
                  recursive: bool = False) -> Dict[str, Any]:
    """List files and directories in a path"""
    try:
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}",
                "items": []
            }
        
        if not directory_path.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {directory_path}",
                "items": []
            }
        
        # Get items
        if recursive:
            items = list(directory_path.rglob(pattern))
        else:
            items = list(directory_path.glob(pattern))
        
        # Convert to list of dictionaries
        file_list = []
        for item in items:
            try:
                stat = item.stat()
                file_list.append({
                    "name": item.name,
                    "path": str(item),
                    "is_file": item.is_file(),
                    "is_dir": item.is_dir(),
                    "size": stat.st_size if item.is_file() else None,
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "mime_type": mimetypes.guess_type(str(item))[0] if item.is_file() else None
                })
            except Exception:
                # Skip items we can't access
                continue
        
        return {
            "success": True,
            "directory": str(directory_path),
            "pattern": pattern,
            "recursive": recursive,
            "total_items": len(file_list),
            "items": file_list
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "items": []
        }

@tool(description="Create a new directory", category="file_io")
def create_directory(directory_path: str, parents: bool = True) -> Dict[str, Any]:
    """Create a new directory"""
    try:
        directory_path = Path(directory_path)
        
        if directory_path.exists():
            return {
                "success": False,
                "error": f"Directory already exists: {directory_path}",
                "directory_path": str(directory_path)
            }
        
        directory_path.mkdir(parents=parents, exist_ok=False)
        
        return {
            "success": True,
            "directory_path": str(directory_path),
            "created_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool(description="Delete a file or directory", category="file_io")
def delete_path(path: str, recursive: bool = False) -> Dict[str, Any]:
    """Delete a file or directory"""
    try:
        path = Path(path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"Path not found: {path}",
                "path": str(path)
            }
        
        if path.is_file():
            path.unlink()
            action = "file_deleted"
        elif path.is_dir():
            if recursive:
                shutil.rmtree(path)
                action = "directory_deleted_recursive"
            else:
                path.rmdir()
                action = "directory_deleted"
        else:
            return {
                "success": False,
                "error": f"Path is neither file nor directory: {path}",
                "path": str(path)
            }
        
        return {
            "success": True,
            "path": str(path),
            "action": action,
            "deleted_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool(description="Copy a file or directory", category="file_io")
def copy_path(source: str, destination: str, overwrite: bool = False) -> Dict[str, Any]:
    """Copy a file or directory"""
    try:
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            return {
                "success": False,
                "error": f"Source not found: {source}",
                "source": str(source),
                "destination": str(destination)
            }
        
        if destination.exists() and not overwrite:
            return {
                "success": False,
                "error": f"Destination already exists: {destination}",
                "source": str(source),
                "destination": str(destination)
            }
        
        if source.is_file():
            shutil.copy2(source, destination)
            action = "file_copied"
        elif source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=overwrite)
            action = "directory_copied"
        else:
            return {
                "success": False,
                "error": f"Source is neither file nor directory: {source}",
                "source": str(source),
                "destination": str(destination)
            }
        
        return {
            "success": True,
            "source": str(source),
            "destination": str(destination),
            "action": action,
            "copied_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool(description="Move or rename a file or directory", category="file_io")
def move_path(source: str, destination: str, overwrite: bool = False) -> Dict[str, Any]:
    """Move or rename a file or directory"""
    try:
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            return {
                "success": False,
                "error": f"Source not found: {source}",
                "source": str(source),
                "destination": str(destination)
            }
        
        if destination.exists() and not overwrite:
            return {
                "success": False,
                "error": f"Destination already exists: {destination}",
                "source": str(source),
                "destination": str(destination)
            }
        
        shutil.move(str(source), str(destination))
        
        return {
            "success": True,
            "source": str(source),
            "destination": str(destination),
            "action": "moved",
            "moved_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool(description="Get file or directory information", category="file_io")
def get_path_info(path: str) -> Dict[str, Any]:
    """Get detailed information about a file or directory"""
    try:
        path = Path(path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"Path not found: {path}",
                "path": str(path)
            }
        
        stat = path.stat()
        mime_type, encoding = mimetypes.guess_type(str(path))
        
        info = {
            "path": str(path),
            "name": path.name,
            "parent": str(path.parent),
            "exists": True,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "is_symlink": path.is_symlink(),
            "size": stat.st_size,
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "mime_type": mime_type,
            "encoding": encoding,
            "permissions": oct(stat.st_mode)[-3:],
            "owner": stat.st_uid,
            "group": stat.st_gid
        }
        
        # Add directory-specific info
        if path.is_dir():
            try:
                items = list(path.iterdir())
                info["item_count"] = len(items)
                info["subdirectories"] = len([item for item in items if item.is_dir()])
                info["files"] = len([item for item in items if item.is_file()])
            except Exception:
                info["item_count"] = None
                info["subdirectories"] = None
                info["files"] = None
        
        return {
            "success": True,
            "info": info
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool(description="Calculate file hash (MD5, SHA1, SHA256)", category="file_io")
def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> Dict[str, Any]:
    """Calculate hash of a file"""
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "file_path": str(file_path)
            }
        
        if not file_path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {file_path}",
                "file_path": str(file_path)
            }
        
        # Validate algorithm
        valid_algorithms = ["md5", "sha1", "sha256", "sha512"]
        if algorithm.lower() not in valid_algorithms:
            return {
                "success": False,
                "error": f"Invalid algorithm. Must be one of: {valid_algorithms}",
                "file_path": str(file_path)
            }
        
        # Calculate hash
        hash_obj = hashlib.new(algorithm.lower())
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return {
            "success": True,
            "file_path": str(file_path),
            "algorithm": algorithm.lower(),
            "hash": hash_obj.hexdigest(),
            "file_size": file_path.stat().st_size
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool(description="Search for files by content", category="file_io")
def search_files(directory: str, search_text: str, file_pattern: str = "*.txt", 
                case_sensitive: bool = False, recursive: bool = True) -> Dict[str, Any]:
    """Search for files containing specific text"""
    try:
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return {
                "success": False,
                "error": f"Directory not found: {directory}",
                "results": []
            }
        
        # Prepare search text
        if not case_sensitive:
            search_text = search_text.lower()
        
        results = []
        
        # Search files
        if recursive:
            files = directory.rglob(file_pattern)
        else:
            files = directory.glob(file_pattern)
        
        for file_path in files:
            if not file_path.is_file():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if not case_sensitive:
                        content = content.lower()
                    
                    if search_text in content:
                        # Find line numbers
                        lines = content.split('\n')
                        matching_lines = []
                        for i, line in enumerate(lines, 1):
                            if search_text in line:
                                matching_lines.append(i)
                        
                        results.append({
                            "file_path": str(file_path),
                            "file_name": file_path.name,
                            "matching_lines": matching_lines,
                            "total_lines": len(lines),
                            "file_size": file_path.stat().st_size
                        })
                        
            except Exception:
                # Skip files we can't read
                continue
        
        return {
            "success": True,
            "directory": str(directory),
            "search_text": search_text,
            "file_pattern": file_pattern,
            "case_sensitive": case_sensitive,
            "recursive": recursive,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        } 