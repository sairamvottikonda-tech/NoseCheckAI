#!/usr/bin/env python3
"""
Prepare and validate 3D model calibration dataset.

This script helps you prepare a calibration dataset using 3D printed models
with known internal septal deviations (straight, C-curve, S-curve).

Usage:
    python scripts/prepare_3d_calibration.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    """Interactive preparation of calibration dataset."""
    print("=" * 80)
    print("3D MODEL CALIBRATION DATASET PREPARATION")
    print("=" * 80)
    print()
    print("This tool helps you organize 3D printed calibration models.")
    print()
    
    # Check for calibration directory
    from config import CALIBRATION_DIR
    
    if not CALIBRATION_DIR.exists():
        print(f"✗ Calibration directory not found: {CALIBRATION_DIR}")
        CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {CALIBRATION_DIR}")
    
    # List existing images
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        image_files.extend(CALIBRATION_DIR.glob(f'*{ext}'))
    
    print(f"\n✓ Found {len(image_files)} image(s) in calibration folder")
    
    if len(image_files) == 0:
        print("\n📝 NEXT STEPS:")
        print("  1. 3D print nasal models (straight, C-curve, S-curve)")
        print("  2. Photograph each model (3-5 photos per model)")
        print("  3. Copy photos to:", CALIBRATION_DIR)
        print("  4. Run this script again to create metadata")
        return
    
    print("\nImages found:")
    for img in sorted(image_files):
        print(f"  • {img.name}")
    
    # Template metadata
    print("\n" + "=" * 80)
    print("TEMPLATE METADATA.CSV")
    print("=" * 80)
    print("\nCreate this file:", CALIBRATION_DIR / "metadata.csv")
    print("\nFormat:")
    print("filename,known_deviation_mm,model_type,septum_shape,expected_classification")
    print()
    print("Example entries:")
    print("straight_0mm_001.jpg,0,normal,straight,normal")
    print("c_curve_2mm_001.jpg,2,mild,c-curve,mild")
    print("c_curve_5mm_001.jpg,5,moderate,c-curve,moderate")
    print("s_curve_8mm_001.jpg,8,severe,s-curve,severe")
    print("s_curve_10mm_001.jpg,10,severe,s-curve,severe")
    print()
    
    # Check if metadata exists
    metadata_path = CALIBRATION_DIR / "metadata.csv"
    if metadata_path.exists():
        print(f"✓ Metadata file exists: {metadata_path}")
        print("\nTo run calibration:")
        print("  python scripts/calibration_workflow.py")
        print("\nTo validate results:")
        print("  python scripts/validate_calibration.py")
    else:
        print(f"✗ Metadata file not found: {metadata_path}")
        print("\nCreate metadata.csv with the format shown above")
        print("Each row should correspond to one image file")
    
    print("\n" + "=" * 80)
    print("CALIBRATION CHECKLIST")
    print("=" * 80)
    print("\n□ 3D print models (straight, C-curve, S-curve)")
    print("□ Set up photo station (tripod, consistent lighting)")
    print("□ Photograph each model (3-5 frontal views)")
    print("□ Copy photos to calibration_models/")
    print("□ Create metadata.csv with known deviations")
    print("□ Run calibration_workflow.py")
    print("□ Review correlation and adjust scaling if needed")
    print("□ Run validate_calibration.py")
    print("□ Document final scaling factors")
    print()
    print("See docs/3D_MODEL_CALIBRATION_PROTOCOL.md for details")
    print()


if __name__ == "__main__":
    main()
