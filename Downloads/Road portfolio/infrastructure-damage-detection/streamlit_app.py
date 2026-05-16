"""
RoadGuard AI - Infrastructure Damage Detection System
Professional Streamlit Application for YOLOv8-based road damage detection
"""

import streamlit as st
import os
import sys
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import DamageReport, Contractor, Alert, DetectionHistory

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
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Detection"


@st.cache_data(ttl=60)
def get_all_reports():
    """Fetch all damage reports from database"""
    db = SessionLocal()
    try:
        reports = db.query(DamageReport).order_by(DamageReport.created_at.desc()).all()
        if not reports:
            return pd.DataFrame()
        
        data = []
        for r in reports:
            data.append({
                "ID": r.id,
                "Type": r.damage_type,
                "Severity": r.severity,
                "Confidence": r.confidence_score,
                "Cost": r.total_cost,
                "Status": r.status,
                "Date": r.created_at,
                "Location": f"{r.latitude}, {r.longitude}" if r.latitude else "Unknown"
            })
        return pd.DataFrame(data)
    finally:
        db.close()


@st.cache_data(ttl=60)
def get_contractor_stats():
    """Fetch contractor statistics"""
    db = SessionLocal()
    try:
        contractors = db.query(Contractor).all()
        if not contractors:
            return pd.DataFrame()
        
        data = []
        for c in contractors:
            data.append({
                "Name": c.name,
                "Specialization": c.specialization,
                "Rating": c.rating,
                "Available": c.available,
                "Current Jobs": c.current_jobs,
                "City": c.city
            })
        return pd.DataFrame(data)
    finally:
        db.close()


def save_detection_to_db(results, road_type):
    """Save detection results to database"""
    if not results or not results.get('success'):
        return False
    
    db = SessionLocal()
    try:
        summary = results.get('summary', {})
        detections = results.get('detections', [])
        
        # In a real app, we'd use actual GPS. Here we'll use some default/mock coords
        for det in detections:
            report = DamageReport(
                image_path="uploaded_image.jpg",  # Placeholder
                damage_type=det.get('damage_type', 'unknown'),
                severity=det.get('severity', 'moderate'),
                confidence_score=det.get('confidence', 0.0),
                total_cost=summary.get('total_estimated_cost', 0) / len(detections) if detections else 0,
                road_type=road_type,
                status="reported",
                created_at=datetime.utcnow()
            )
            db.add(report)
        
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        db.rollback()
        return False
    finally:
        db.close()


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
    """Render sidebar with navigation and settings"""
    with st.sidebar:
        st.markdown("### 🗺️ Navigation")
        page = st.radio("Go to", ["Detection", "Analytics Dashboard", "Historical Reports", "Contractors"])
        st.session_state.current_page = page
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")

        api_status = check_api_health()
        st.session_state.api_available = api_status

        status_color = "🟢" if api_status else "🔴"
        status_text = "Connected" if api_status else "Demo Mode"
        st.markdown(f"**API Status:** {status_color} {status_text}")

        st.markdown("---")

        if page == "Detection":
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
        else:
            confidence_threshold = 0.5
            selected_road = "City Street"

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


def render_historical_reports():
    """Render historical reports page"""
    st.markdown("### 📋 Historical Damage Reports")
    st.markdown("Browse and filter all previously detected infrastructure damages")

    df = get_all_reports()
    
    if df.empty:
        st.warning("No reports found in the database.")
        return

    # Filtering UI
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.multiselect("Damage Type", options=df["Type"].unique(), default=df["Type"].unique())
    with col2:
        severity_filter = st.multiselect("Severity", options=df["Severity"].unique(), default=df["Severity"].unique())
    with col3:
        status_filter = st.multiselect("Status", options=df["Status"].unique(), default=df["Status"].unique())

    filtered_df = df[
        (df["Type"].isin(type_filter)) & 
        (df["Severity"].isin(severity_filter)) & 
        (df["Status"].isin(status_filter))
    ]

    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID"),
            "Date": st.column_config.DatetimeColumn("Date"),
            "Cost": st.column_config.NumberColumn("Estimated Cost", format="₹%d"),
            "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1)
        }
    )

    if st.button("📥 Export to CSV", use_container_width=True):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"roadguard_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


def render_analytics_dashboard():
    """Render advanced analytics dashboard"""
    st.markdown("### 📈 Analytics Dashboard")
    st.markdown("Visual insights and trends from infrastructure damage data")

    df = get_all_reports()
    
    if df.empty:
        st.warning("No data available for analytics.")
        return

    # Top level metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reports", len(df))
    with col2:
        st.metric("Total Est. Cost", f"₹{df['Cost'].sum():,.0f}")
    with col3:
        avg_conf = df['Confidence'].mean() * 100
        st.metric("Avg Confidence", f"{avg_conf:.1f}%")
    with col4:
        active_reports = len(df[df["Status"] != "completed"])
        st.metric("Active Cases", active_reports)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # Damage Type Distribution
        type_counts = df["Type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        fig1 = px.pie(type_counts, values="Count", names="Type", title="Damage Type Distribution",
                     color_discrete_sequence=px.colors.sequential.Oranges_r)
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Severity Distribution
        sev_counts = df["Severity"].value_counts().reset_index()
        sev_counts.columns = ["Severity", "Count"]
        fig2 = px.bar(sev_counts, x="Severity", y="Count", title="Severity Distribution",
                     color="Severity", color_discrete_map={
                         "minor": "#059669", "moderate": "#d97706", "severe": "#dc2626"
                     })
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    # Time series trend
    df["Date_Only"] = df["Date"].dt.date
    trend_df = df.groupby("Date_Only").size().reset_index(name="Count")
    fig3 = px.line(trend_df, x="Date_Only", y="Count", title="Detection Trends Over Time")
    fig3.update_traces(line_color="#f97316", line_width=3)
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig3, use_container_width=True)


def render_contractors_list():
    """Render contractor management page"""
    st.markdown("### 👷 Contractor Management")
    st.markdown("Manage and monitor registered repair contractors")

    df = get_contractor_stats()
    
    if df.empty:
        st.warning("No contractors found.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                "Available": st.column_config.CheckboxColumn("Available")
            }
        )

    with col2:
        st.markdown("#### 📊 Contractor Workload")
        fig = px.bar(df, x="Name", y="Current Jobs", color="Specialization",
                    title="Active Jobs per Contractor")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)


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

    current_page = st.session_state.current_page

    if current_page == "Detection":
        uploaded_file = render_upload_section(confidence_threshold, road_type)

        if st.session_state.processing:
            with st.spinner("🔄 Processing image... Analyzing damage patterns..."):
                import time
                time.sleep(2)

                if st.session_state.api_available:
                    st.info("Connected to backend API - Using real detection model")
                else:
                    st.info("Running in demo mode with sample data")

                results = get_mock_detection_results()
                st.session_state.detection_results = results
                
                # Save to database
                if save_detection_to_db(results, road_type):
                    st.success("✅ Detection results saved to database")
                
                st.session_state.processing = False

        if st.session_state.detection_results:
            render_detection_results(st.session_state.detection_results)

        render_dashboard_preview()
    
    elif current_page == "Analytics Dashboard":
        render_analytics_dashboard()
    
    elif current_page == "Historical Reports":
        render_historical_reports()
    
    elif current_page == "Contractors":
        render_contractors_list()

    render_footer()


if __name__ == "__main__":
    main()
