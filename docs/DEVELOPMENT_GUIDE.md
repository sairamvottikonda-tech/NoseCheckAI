# NoseCheck Development Guide

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (venv, conda, etc.)
- Git (for version control)

### Initial Setup

1. **Clone/Download the repository**

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (macOS/Linux)
   source venv/bin/activate
   
   # Activate (Windows)
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install package in development mode**:
   ```bash
   pip install -e .
   ```

## Project Structure

```
nosecheck/
├── src/                      # Source code
│   ├── image_processing/     # Image handling and preprocessing
│   ├── landmark_detection/   # MediaPipe facial landmark detection
│   ├── measurement/          # Asymmetry calculations
│   ├── scoring/              # Deviation scoring system
│   ├── questionnaire/        # Symptom assessment
│   ├── data_management/      # Database and data storage
│   └── analysis/             # Statistical analysis and visualization
├── data/                     # Data directory
├── notebooks/                # Jupyter notebooks for analysis
├── tests/                    # Test suite
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

## Development Workflow

### 1. Module Development Order

Follow this recommended order for implementation:

1. **Image Processing** (`src/image_processing/`)
   - Start with `image_loader.py` - basic image loading
   - Then `preprocessor.py` - image standardization
   - Add `quality_checker.py` - quality validation
   - Finally `calibration.py` - distance/scale calibration

2. **Landmark Detection** (`src/landmark_detection/`)
   - Implement `detector.py` - MediaPipe integration
   - Add `nose_landmarks.py` - extract nasal landmarks
   - Create `visualizer.py` - visualization for debugging

3. **Measurement** (`src/measurement/`)
   - Start with `geometry_utils.py` - basic geometry functions
   - Implement `asymmetry_calculator.py` - calculate metrics
   - Add `normalization.py` - normalize by face size

4. **Data Management** (`src/data_management/`)
   - Define `models.py` - data models
   - Implement `database.py` - SQLite operations
   - Add `export.py` - CSV/JSON export

5. **Scoring** (`src/scoring/`)
   - Create `score_calculator.py` - basic scoring
   - Implement `calibration_manager.py` - calibration data
   - Add `classifier.py` - severity classification

6. **Questionnaire** (`src/questionnaire/`)
   - Implement `questionnaire.py` - symptom questions
   - Add `symptom_analyzer.py` - symptom scoring
   - Create `combined_scorer.py` - combine visual + symptoms

7. **Analysis** (`src/analysis/`)
   - Implement `statistics.py` - descriptive statistics
   - Add `validation.py` - validation metrics
   - Create `visualizations.py` - plots and charts
   - Implement `report_generator.py` - analysis reports

### 2. Testing Strategy

Write tests as you develop each module:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_image_processing.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### 3. Code Style

Use Black for consistent formatting:

```bash
# Format all source code
black src/

# Check without modifying
black --check src/
```

Use flake8 for linting:

```bash
flake8 src/
```

## Common Development Tasks

### Running Jupyter Notebooks

```bash
# Start Jupyter
jupyter notebook

# Or Jupyter Lab
jupyter lab
```

### Database Management

```python
# Initialize database
from src.data_management import database

db = database.Database("data/nosecheck.db")
db.initialize()
```

### Processing an Image

```python
from src.image_processing import image_loader, preprocessor
from src.landmark_detection import detector

# Load and preprocess image
image = image_loader.load_image("data/images/test.jpg")
processed = preprocessor.preprocess(image)

# Detect landmarks
landmarks = detector.detect_landmarks(processed)
```

### Running Calibration

```bash
python scripts/calibration_workflow.py
```

## Debugging Tips

### Visualizing Landmarks

```python
from src.landmark_detection import visualizer

# Visualize detected landmarks on image
visualizer.draw_landmarks(image, landmarks, save_path="output.jpg")
```

### Checking Image Quality

```python
from src.image_processing import quality_checker

quality_score = quality_checker.check_quality(image)
print(f"Quality score: {quality_score}")
```

### Database Inspection

```bash
# Use SQLite command line
sqlite3 data/nosecheck.db

# Or use a GUI tool like DB Browser for SQLite
```

## Performance Optimization

### Image Processing
- Resize images to standard size (e.g., 640x480) before processing
- Use grayscale for operations that don't need color
- Cache preprocessed images when processing multiple times

### Landmark Detection
- MediaPipe is already optimized; use default settings initially
- Reduce model complexity if real-time performance is needed
- Process in batches for multiple images

## Troubleshooting

### MediaPipe Installation Issues

```bash
# If MediaPipe fails to install
pip install --upgrade pip
pip install mediapipe --no-cache-dir
```

### OpenCV Camera Access

```python
# Test camera access
import cv2
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot access camera")
```

### Memory Issues with Large Datasets

- Process images in batches
- Clear memory after each batch
- Use generators instead of loading all data at once

## Contributing Guidelines

1. Create a feature branch for each new feature/fix
2. Write tests for new functionality
3. Ensure all tests pass before committing
4. Format code with Black
5. Update documentation as needed
6. Commit with clear, descriptive messages

## Useful Resources

### MediaPipe Documentation
- [MediaPipe Face Mesh](https://google.github.io/mediapipe/solutions/face_mesh)
- [Landmark indices](https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png)

### OpenCV Tutorials
- [Official OpenCV Python Tutorials](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html)

### Python Best Practices
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## Getting Help

- Check documentation in `docs/` folder
- Review example notebooks in `notebooks/`
- Inspect test files for usage examples
- Contact research team for specific questions
