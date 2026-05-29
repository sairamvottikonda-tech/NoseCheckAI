# NoseCheck - DNS Screening Tool

A Python-based system for detecting nasal asymmetry using smartphone photos and symptom assessment.

## Project Overview

NoseCheck is a research project that aims to detect Deviated Nasal Septum (DNS) using:
1. **Computer Vision Analysis**: Automated facial landmark detection and nasal asymmetry measurements
2. **Symptom Assessment**: Self-reported symptom questionnaire
3. **Calibration System**: Validated against 3D-printed models with known deviations

## Features

- Automated facial landmark detection using MediaPipe
- Quantitative nasal asymmetry measurements
- Multi-metric deviation scoring system
- Symptom questionnaire integration
- Calibration with 3D-printed reference models
- Statistical analysis and visualization
- Mobile-friendly web interface

## Project Structure

```
nosecheck/
├── src/
│   ├── image_processing/      # Photo capture and preprocessing
│   ├── landmark_detection/    # Facial landmark detection using MediaPipe
│   ├── measurement/           # Nasal asymmetry calculations
│   ├── scoring/              # Deviation score algorithm
│   ├── questionnaire/        # Symptom checklist module
│   ├── data_management/      # Data storage and retrieval
│   └── analysis/             # Statistical analysis and visualization
├── data/
│   ├── calibration_models/   # Known deviations of 3D models
│   ├── images/               # Captured photos
│   └── results/              # Measurement data and scores
├── models/                   # MediaPipe model files (face_landmarker.task)
├── notebooks/                # Jupyter notebooks for analysis
├── tests/                    # Unit tests
├── docs/                     # Documentation and research notes
└── scripts/                  # Utility scripts
```

## Installation

### Prerequisites

- Python 3.8+ (Python 3.9.6+ recommended)
- pip (Python package manager)

### Step-by-Step Setup

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/lakshman1213/nosecheck.git
   cd nosecheck
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   
   For full development (includes pandas, matplotlib, scikit-learn for analysis):
   ```bash
   pip install -r requirements.txt
   ```
   
   For minimal web app only (production-like):
   ```bash
   pip install -r requirements-production.txt
   ```

4. **Download the MediaPipe Face Landmarker model**
   
   The model will auto-download on first run, but you can download it manually:
   ```bash
   mkdir -p models
   curl -L -o models/face_landmarker.task \
     "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
   ```

## Running Locally

After installation, start the Flask web server:

**Option 1: Using the convenience script**
```bash
python run_server.py
```

**Option 2: Using Python module**
```bash
python -m src.app
```

**Option 3: Using Flask CLI**
```bash
python -m flask --app src.app run --host 0.0.0.0 --port 5001
```

The server will start on **http://localhost:5001**

- Open your browser and navigate to `http://localhost:5001`
- The web interface provides a mobile-friendly UI for photo upload, symptom questionnaire, and results display
- Press `Ctrl+C` to stop the server

### Development vs Production Dependencies

- **`requirements.txt`**: Full development dependencies including pandas, matplotlib, scikit-learn, jupyter. Use this for local development, calibration scripts, and data analysis.
- **`requirements-production.txt`**: Minimal dependencies for web app only. Use this for production deployments or if you only need the web interface.

## Quick Start

### Web Interface (Recommended)

1. Start the server: `python run_server.py`
2. Open `http://localhost:5001` in your browser
3. Upload a frontal face photo
4. Complete the symptom questionnaire
5. View your screening result with deviation score and classification

### Python API

```python
from src.landmark_detection.detector import detect_landmarks
from src.measurement.asymmetry_calculator import calculate
from src.scoring.score_calculator import calculate_score

# Process an image
image_path = "path/to/nose/photo.jpg"
landmarks = detect_landmarks(image_path)
if landmarks:
    measurements = calculate(landmarks)
    result = calculate_score(measurements)
    print(f"Deviation Score: {result['deviation_score']}")
    print(f"Classification: {result['classification']}")
```

## Key Metrics

The system calculates the following nasal asymmetry metrics:

1. **Lateral Deviation**: Distance from nose tip to facial midline
2. **Septal Angle**: Angle of nasal septum from vertical
3. **Nostril Asymmetry**: Left vs. right nostril size/shape differences
4. **Bridge Alignment**: Straightness of nasal bridge

## Technology Stack

- **Computer Vision**: OpenCV, MediaPipe
- **Data Processing**: NumPy, Pandas
- **Statistical Analysis**: SciPy, scikit-learn
- **Visualization**: Matplotlib, Seaborn
- **Web Interface**: Flask
- **Database**: SQLite (via SQLAlchemy)
- **Development**: Jupyter, pytest, black

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

## Troubleshooting

### Common Issues

**Port 5000 already in use (macOS)**
- macOS AirPlay Receiver uses port 5000 by default
- NoseCheck uses port 5001 to avoid conflicts
- If port 5001 is also in use, change it in `run_server.py` or `src/app/__main__.py`

**Model download fails**
- Check your internet connection
- Download manually:
  ```bash
  mkdir -p models
  curl -L -o models/face_landmarker.task \
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
  ```

**Import errors**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version` (should be 3.8+)

**Face detection fails**
- Ensure photo is frontal (face camera directly)
- Check lighting (even, not too dark or overexposed)
- Photo should show full face with nose clearly visible
- Try a different photo with better quality

**Module not found errors**
- Make sure you're in the project root directory
- Verify `src/` directory exists and contains all modules
- Check that `__init__.py` files exist in each package directory

## Research Validation

This tool is designed for research purposes to:
- Validate correlation between calculated scores and known deviations
- Assess repeatability of measurements
- Evaluate classification accuracy across severity categories
- Serve as an educational tool for adolescent health awareness

## Expected Outcomes

- **Quantitative Validation**: High correlation (r²) between known and calculated deviations
- **Repeatability**: Coefficient of variation < 10% for repeated measurements
- **Classification Accuracy**: Reliable distinction between normal/mild/moderate/severe categories

## Contributing

This is a research project. For questions or collaboration inquiries, please contact the research team.

## License

[To be determined based on research institution requirements]

## Disclaimer

This tool is for research and educational purposes only. It is not intended for clinical diagnosis or medical decision-making. Always consult qualified healthcare professionals for medical advice.

## Citation

[To be added upon publication]
