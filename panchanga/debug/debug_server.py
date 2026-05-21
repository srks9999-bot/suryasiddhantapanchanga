"""
Debug server script for Panchanga Service.

This script enables debugging with debugpy and starts the FastAPI application.
Use this when you want to attach a debugger to the running service.

Usage:
    python debug_server.py

Or with VS Code launch configuration (recommended).
"""

import sys
import uvicorn
from api.main import app

# Configure debugpy
# Default port 5678 is the standard debugpy port
DEBUG_PORT = 5678

if __name__ == "__main__":
    # Check if a debugger is already attached (e.g. PyCharm)
    # PyCharm sets a trace function when debugging, so we skip debugpy to avoid conflicts
    if sys.gettrace() is None:
        try:
            import debugpy
            # Enable debugpy and wait for debugger to attach
            print(f"Starting debug server on port {DEBUG_PORT}...")
            print("Waiting for debugger to attach...")
            print("(In VS Code, start the 'Panchanga Service: Start with Debugger' configuration)")
            
            debugpy.listen(("0.0.0.0", DEBUG_PORT))
            debugpy.wait_for_client()  # Optional: wait for debugger to attach before continuing
            
            print("Debugger attached! Starting uvicorn...")
        except ImportError:
            print("debugpy not installed. Skipping remote debug setup.")
        except Exception as e:
            print(f"Failed to initialize debugpy: {e}")
            print("Continuing without debugpy...")
    else:
        print("Debugger already attached (PyCharm/IDE). Skipping debugpy initialization.")
    
    # Start uvicorn with the FastAPI app
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in debug mode to avoid conflicts
        log_level="info"
    )
