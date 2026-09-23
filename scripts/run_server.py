"""
NEXUS-NOWCAST: Local Development & Pitch Demonstration Server
Launches FastAPI backend and serves Meteorological C2 Mission Control HUD.
"""

import uvicorn
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")



def main():
    print("\n" + "="*70)
    print(" 🌪️ NEXUS-NOWCAST: STGAT-PIE METEOROLOGICAL ENGINE")
    print(" Smart India Hackathon 2026 | PS26072 | Ministry of Earth Sciences")
    print("="*70)
    print(" Starting Mission Control Server at: http://127.0.0.1:8000")
    print(" Press Ctrl+C to stop.\n")

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
