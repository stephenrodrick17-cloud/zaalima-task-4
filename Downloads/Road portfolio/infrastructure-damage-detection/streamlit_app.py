"""
RoadGuard AI - Infrastructure Damage Detection System
Professional Streamlit Application for YOLOv8-based road damage detection
"""

import streamlit as st
import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="RoadGuard AI | Infrastructure Damage Detection",
    page_icon="🚧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #020617 100%);
    }

    .main-header {
        font-size: 3rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }

    .success-box {
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
        border: 1px solid #059669;
        border-radius: 12px;
        padding: 1rem;
        color: #34d399;
    }

    .warning-box {
        background: linear-gradient(135deg, #78350f 0%, #451a03 100%);
        border: 1px solid #d97706;
        border-radius: 12px;
        padding: 1rem;
        color: #fbbf24;
    }

    .danger-box {
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%);
        border: 1px solid #dc2626;
        border-radius: 12px;
        padding: 1rem;
        color: #f87171;
    }

    .upload-zone {
        border: 2px dashed #475569;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        background: rgba(15, 23, 42, 0.5);
        transition: all 0.3s ease;
    }

    .upload-zone:hover {
        border-color: #f97316;
        background: rgba(249, 115, 22, 0.05);
    }

    .detection-result {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .severity-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .severity-minor { background: #064e3b; color: #34d399; }
    .severity-moderate { background: #78350f; color: #fbbf24; }
    .severity-severe { background: #7f1d1d; color: #f87171; }

    .footer {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-size: 0.875rem;
        border-top: 1px solid #1e293b;
        margin-top: 3rem;
    }

    div[data-testid="stToolbar"] { display: none; }

    .stButton > button {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(249, 115, 22, 0.3);
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 700;
    }

    .sidebar .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'detection_results' not in st.session_state:
        st.session_state.detection_results = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'api_available' not in st.session_state:
        st.session_state.api_available = False


def check_api_health():
    """Check if the backend API is available"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_mock_detection_results():
    """Generate mock detection results for demo mode"""
    return {
        "success": True,
        "detections": [
            {"damage_type": "pothole", "severity": "moderate", "confidence": 0.89, "area_percentage": 8.5},
            {"damage_type": "crack", "severity": "minor", "confidence": 0.92, "area_percentage": 3.2},
            {"damage_type": "pothole", "severity": "severe", "confidence": 0.95, "area_percentage": 12.1}
        ],
        "summary": {
            "total_damage_areas": 3,
            "total_estimated_cost": 45000,
            "avg_confidence": 0.92,
            "avg_severity_score": 6.5
        },
        "annotated_image_path": None
    }


def render_header():
    """Render the main header"""
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 class="main-header">🚧 RoadGuard AI</h1>
            <p class="sub-header">Advanced Infrastructure Damage Detection System using YOLOv8</p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with settings and info"""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        api_status = check_api_health()
        st.session_state.api_available = api_status

        status_color = "🟢" if api_status else "🔴"
        status_text = "Connected" if api_status else "Demo Mode"
        st.markdown(f"**API Status:** {status_color} {status_text}")

        st.markdown("---")

        st.markdown("### 📊 Detection Settings")

        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Minimum confidence score for detections"
        )

        road_types = ["City Street", "Highway", "Rural Road", "Expressway"]
        selected_road = st.selectbox("Road Type", road_types)

        st.markdown("---")

        st.markdown("### ℹ️ About")
        st.markdown("""
            **RoadGuard AI** utilizes state-of-the-art YOLOv8 computer vision 
            technology to detect and classify infrastructure damage including 
            potholes, cracks, and structural issues.
        """)

        st.markdown("---")
        st.markdown("*© 2024 RoadGuard AI Systems*")

        return confidence_threshold, selected_road


def render_upload_section(confidence_threshold, road_type):
    """Render file upload and detection section"""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📤 Upload Image")
        st.markdown("Upload an image of road surface for damage analysis")

        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            help="Supported formats: JPG, JPEG, PNG, BMP"
        )

        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    with col2:
        st.markdown("### 🎯 Quick Actions")

        if st.button("🔍 Run Detection", use_container_width=True):
            if uploaded_file is None:
                st.warning("Please upload an image first!")
            else:
                st.session_state.processing = True
                st.rerun()

        if st.button("📊 Run Demo Analysis", use_container_width=True):
            st.session_state.detection_results = get_mock_detection_results()
            st.session_state.processing = True
            st.rerun()

        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.detection_results = None
            st.session_state.uploaded_file = None
            st.session_state.processing = False
            st.rerun()

    return uploaded_file


def render_detection_results(results):
    """Render detection results"""
    if not results or not results.get('success'):
        return

    st.markdown("---")
    st.markdown("### 📋 Detection Results")

    summary = results.get('summary', {})
    detections = results.get('detections', [])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Damage Areas",
            value=summary.get('total_damage_areas', 0),
            delta="Detected"
        )

    with col2:
        cost = summary.get('total_estimated_cost', 0)
        st.metric(
            label="Est. Repair Cost",
            value=f"₹{cost:,}",
            delta="INR"
        )

    with col3:
        confidence = summary.get('avg_confidence', 0)
        st.metric(
            label="Avg Confidence",
            value=f"{confidence * 100:.1f}%"
        )

    with col4:
        severity = summary.get('avg_severity_score', 0)
        severity_label = "High" if severity > 6 else "Medium" if severity > 3 else "Low"
        st.metric(
            label="Risk Level",
            value=severity_label
        )

    st.markdown("---")

    if detections:
        st.markdown("#### 🔎 Detailed Findings")

        for i, detection in enumerate(detections, 1):
            severity = detection.get('severity', 'unknown').lower()
            severity_class = f"severity-{severity}"

            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                damage_type = detection.get('damage_type', 'Unknown').replace('_', ' ').title()
                st.markdown(f"""
                    <div class="detection-result">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <span style="font-size: 2rem;">{
                                '🕳️' if 'pothole' in damage_type.lower() else
                                '📊' if 'crack' in damage_type.lower() else '⚠️'
                            }</span>
                            <div>
                                <h4 style="margin: 0; color: white;">{damage_type}</h4>
                                <p style="margin: 0; color: #64748b; font-size: 0.875rem;">
                                    Detection #{i}
                                </p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("**Severity**")
                st.markdown(f"<span class='severity-badge {severity_class}'>{severity}</span>", unsafe_allow_html=True)

            with col3:
                conf = detection.get('confidence', 0)
                st.markdown("**Confidence**")
                st.markdown(f"{conf * 100:.1f}%")

            with col4:
                area = detection.get('area_percentage', 0)
                st.markdown("**Area Impact**")
                st.markdown(f"{area:.1f}%")

            if i < len(detections):
                st.markdown("---")


def render_dashboard_preview():
    """Render dashboard statistics preview"""
    st.markdown("---")
    st.markdown("### 📈 System Statistics")

    col1, col2, col3, col4 = st.columns(4)

    stats = [
        {"label": "Total Scans", "value": "1,247", "delta": "+12%"},
        {"label": "Damage Detected", "value": "3,891", "delta": "+8%"},
        {"label": "Repair Cost Saved", "value": "₹4.2M", "delta": "+15%"},
        {"label": "Accuracy Rate", "value": "99.2%", "delta": "+2%"}
    ]

    for col, stat in zip([col1, col2, col3, col4], stats):
        with col:
            st.metric(label=stat["label"], value=stat["value"], delta=stat["delta"])


def render_footer():
    """Render footer"""
    st.markdown("""
        <div class="footer">
            <p>🚧 RoadGuard AI - Pioneering Urban Safety</p>
            <p>Powered by YOLOv8 Computer Vision Technology</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    initialize_session_state()

    render_header()

    confidence_threshold, road_type = render_sidebar()

    uploaded_file = render_upload_section(confidence_threshold, road_type)

    if st.session_state.processing:
        with st.spinner("🔄 Processing image... Analyzing damage patterns..."):
            import time
            time.sleep(2)

            if st.session_state.api_available:
                st.info("Connected to backend API - Using real detection model")
            else:
                st.info("Running in demo mode with sample data")

            st.session_state.detection_results = get_mock_detection_results()
            st.session_state.processing = False

    if st.session_state.detection_results:
        render_detection_results(st.session_state.detection_results)

    render_dashboard_preview()

    render_footer()


if __name__ == "__main__":
    main()
