# 🚧 RoadGuard AI - Infrastructure Damage Detection System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

A professional-grade AI-powered infrastructure damage detection system using YOLOv8 computer vision technology. Built with Streamlit for easy deployment and beautiful visualization.

## 🌟 Features

- **AI-Powered Detection**: Utilizes state-of-the-art YOLOv8 for detecting potholes, cracks, and structural damage
- **Real-time Analysis**: Process road surface images and get instant damage assessments
- **Severity Classification**: Automatic classification of damage into Minor, Moderate, and Severe categories
- **Cost Estimation**: Intelligent repair cost calculation based on damage type and severity
- **Beautiful UI**: Professional dark-themed interface with responsive design
- **Easy Deployment**: One-click Streamlit deployment to Streamlit Cloud

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_streamlit.txt
   ```

4. **Run the Streamlit app**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 📁 Project Structure

```
infrastructure-damage-detection/
├── streamlit_app.py              # Main Streamlit application
├── requirements_streamlit.txt     # Python dependencies
├── backend/                      # FastAPI backend (optional)
│   ├── main.py
│   └── app/
│       ├── routes/
│       ├── services/
│       └── schemas.py
├── model/                       # YOLOv8 model files
│   └── trained_models/
│       └── infrastructure_damage/
│           └── weights/
│               └── best.pt       # Trained model weights
├── database/                    # Database models
│   ├── models.py
│   └── database.py
├── docs/                        # Documentation
└── README.md
```

## 🎯 Usage

### Image Upload
1. Click the upload zone or drag and drop a road surface image
2. Click "Run Detection" to analyze the image
3. View detailed results including damage type, severity, and cost estimates

### Demo Mode
If the backend API is not running, the app will automatically switch to demo mode with sample data.

### Connecting Backend (Optional)
For full functionality with real YOLOv8 detection:
1. Start the FastAPI backend: `python run_backend.py`
2. Ensure the backend is running on `http://localhost:8000`
3. The Streamlit app will automatically connect

## 🚢 Deployment to Streamlit Cloud

### Method 1: Direct Deployment

1. Push this repository to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your repository and branch
5. Set the main file path to `streamlit_app.py`
6. Click "Deploy!"

### Method 2: GitHub Actions (Auto-Deploy)

Create a `.github/workflows/deploy.yml` file:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: python/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements_streamlit.txt
      - uses: streamlit/setup-streamlit@v1
      - run: streamlit run streamlit_app.py --server.port 8501 --server.address localhost
```

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file for custom configuration:

```env
# API Configuration
API_BASE_URL=http://localhost:8000
API_KEY=your_api_key_here

# Model Configuration
MODEL_PATH=model/trained_models/infrastructure_damage/weights/best.pt
CONFIDENCE_THRESHOLD=0.5

# UI Configuration
APP_TITLE=RoadGuard AI
APP_ICON=🚧
```

## 📊 API Endpoints (Backend)

If using the backend API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/detection/detect` | POST | Upload image for detection |
| `/api/detection/image/{name}` | GET | Get annotated image |
| `/api/dashboard/overview` | GET | Dashboard statistics |
| `/api/dashboard/statistics` | GET | Detailed statistics |

## 🎨 Customization

### Changing Colors

Edit the CSS variables in `streamlit_app.py`:

```python
st.markdown("""
<style>
    :root {
        --primary-color: #f97316;
        --bg-dark: #020617;
        --bg-card: #0f172a;
        --border-color: #334155;
    }
</style>
""", unsafe_allow_html=True)
```

### Adding New Detection Types

Extend the detection types in `get_mock_detection_results()` or connect to your trained model.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ultralytics](https://ultralytics.com) for YOLOv8
- [Streamlit](https://streamlit.io) for the amazing framework
- [Indian Infrastructure Dataset](https://dataset.com) for training data

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**© 2024 RoadGuard AI Systems - Pioneering Urban Safety**
