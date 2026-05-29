"""
Command-line interface for NoseCheck.

Usage:
    nosecheck                  # Show help
    nosecheck run              # Start Flask web server
    nosecheck calibrate        # Run calibration workflow
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


def main():
    """Main CLI entry point."""
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print("NoseCheck - DNS Screening Tool")
        print()
        print("Commands:")
        print("  run         Start the web server (Flask)")
        print("  calibrate   Run calibration workflow")
        print("  validate    Run calibration validation")
        print()
        print("Examples:")
        print("  nosecheck run")
        print("  python -m flask --app src.app run")
        return 0

    cmd = args[0].lower()
    if cmd == "run":
        from src.app import app
        import config
        cfg = getattr(config, "FLASK_CONFIG", {})
        app.run(
            host=cfg.get("host", "0.0.0.0"),
            port=cfg.get("port", 5000),
            debug=cfg.get("debug", True),
        )
        return 0
    if cmd == "calibrate":
        from scripts.calibration_workflow import main as calibrate_main
        calibrate_main()
        return 0
    if cmd == "validate":
        from scripts.validate_calibration import main as validate_main
        validate_main()
        return 0

    print(f"Unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
