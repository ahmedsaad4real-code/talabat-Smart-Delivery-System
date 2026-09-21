"""
talabat — Streamlit App
NTI Graduation Project

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import os
import joblib
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from train_model import main as train_and_save_model

# ------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="talabat",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_FILENAME = "final_delivery_delay_model.pkl"
META_FILENAME = "metadata.pkl"

# Brand palette (orange + cream, matching the reference dashboard)
ORANGE = "#F4632A"
ORANGE_DARK = "#D9491A"
ORANGE_LIGHT = "#FBA57E"
CREAM = "#FBF3EC"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#26160E"
GREEN = "#1FA97A"
RED = "#E2544C"


# ------------------------------------------------------------------
# Styling
# ------------------------------------------------------------------
def kpi_card(icon: str, label: str, value: str) -> str:
    return f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div>
                <p class="kpi-label">{label}</p>
                <p class="kpi-value">{value}</p>
            </div>
        </div>
    """
def inject_ltr_fix():
    # تمت إزالة تعديل اتجاه dir لمنع التعارض مع sliders
    pass


def inject_css():
    st.markdown(
        f"""
        <style>
        /* إجبار شريط الـ Slider والمسار الملون على الاتجاه الصحيح LTR */
        [data-testid="stSlider"] *, [data-baseweb="slider"] * {{
            direction: ltr !important;
        }}
        [data-baseweb="slider"] > div {{
            direction: ltr !important;
        }}

        /* Force readable dark text on all main-area widget labels */
        [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] .stMarkdown,
        [data-testid="stAppViewContainer"] .stMarkdown p,
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4 {{
            color: {TEXT_DARK} !important;
        }}
        
        [data-testid="stAppViewContainer"] div[data-baseweb="select"] * {{
            color: {TEXT_DARK} !important;
        }}
        
        .stTabs [data-baseweb="tab"],
        .stTabs [data-baseweb="tab"] p,
        .stTabs [data-baseweb="tab"] *,
        [data-testid="stTabs"] [data-baseweb="tab"],
        [data-testid="stTabs"] [data-baseweb="tab"] p,
        [data-testid="stTabs"] [data-baseweb="tab"] *,
        button[data-baseweb="tab"],
        button[data-baseweb="tab"] p,
        button[data-baseweb="tab"] * {{
            color: {TEXT_DARK} !important;
        }}
        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] *,
        [data-testid="stTabs"] [aria-selected="true"] p,
        [data-testid="stTabs"] [aria-selected="true"] * {{
            color: {TEXT_DARK} !important;
        }}
        
        .brand-banner, .brand-banner *,
        .result-ontime, .result-ontime *,
        .result-delay, .result-delay * {{
            color: #ffffff !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background-color: {CREAM};
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(0,0,0,0);
        }}
        .main .block-container {{
            padding-top: 1.3rem;
            max-width: 1250px;
        }}

        [data-testid="stSidebar"] {{
            background-color: {ORANGE};
        }}
        [data-testid="stSidebar"] * {{
            color: #ffffff !important;
        }}
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {{
            background-color: rgba(255,255,255,0.15);
            border-radius: 8px;
            color: #ffffff !important;
        }}
        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.3);
        }}

        .brand-banner {{
            background: linear-gradient(120deg, {ORANGE_DARK} 0%, {ORANGE} 55%, {ORANGE_LIGHT} 100%);
            border-radius: 18px;
            padding: 1.8rem 2.2rem;
            color: white;
            margin-bottom: 1.4rem;
            position: relative;
            overflow: hidden;
        }}
        .brand-banner .tag {{
            letter-spacing: 3px;
            font-size: 0.75rem;
            font-weight: 700;
            opacity: 0.9;
            text-transform: uppercase;
        }}
        .brand-banner h1 {{
            margin: 0.2rem 0 0.2rem 0;
            font-size: 2.1rem;
            font-weight: 800;
        }}
        .brand-banner p {{
            margin: 0;
            opacity: 0.92;
            font-size: 1rem;
        }}

        .kpi-card {{
            background: {CARD_BG};
            border-radius: 14px;
            padding: 1rem 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #f1e4da;
        }}
        .kpi-icon {{
            font-size: 1.6rem;
            background: {CREAM};
            border-radius: 50%;
            width: 46px; height: 46px;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }}
        .kpi-label {{
            font-size: 0.78rem;
            color: #8a7a6f;
            margin: 0;
        }}
        .kpi-value {{
            font-size: 1.3rem;
            font-weight: 800;
            color: {TEXT_DARK};
            margin: 0;
        }}

        .section-card {{
            background: {CARD_BG};
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            border: 1px solid #f1e4da;
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
            margin-bottom: 1.2rem;
        }}
        .section-title {{
            font-weight: 800;
            font-size: 1.05rem;
            color: {TEXT_DARK};
            margin-bottom: 0.9rem;
        }}

        .result-ontime {{
            background: linear-gradient(135deg, #0f9b6f 0%, {GREEN} 100%);
            color: white; border-radius: 16px; padding: 1.6rem 2rem;
        }}
        .result-delay {{
            background: linear-gradient(135deg, #b23a48 0%, {RED} 100%);
            color: white; border-radius: 16px; padding: 1.6rem 2rem;
        }}
        .result-ontime h2, .result-delay h2 {{margin: 0 0 0.3rem 0;}}
        .result-ontime p, .result-delay p {{margin: 0; opacity: 0.95;}}

        button[kind="primary"] {{
            background-color: {ORANGE} !important;
            border-color: {ORANGE} !important;
        }}
        button[kind="primary"]:hover {{
            background-color: {ORANGE_DARK} !important;
            border-color: {ORANGE_DARK} !important;
        }}

        .stTabs [data-baseweb="tab"],
        [data-testid="stTabs"] [data-baseweb="tab"] {{
            font-weight: 700;
            color: {TEXT_DARK} !important;
        }}
        .stTabs [aria-selected="true"],
        [data-testid="stTabs"] [aria-selected="true"] {{
            color: {TEXT_DARK} !important;
        }}

        [data-testid="stAppViewContainer"] [data-testid="stMetricValue"],
        [data-testid="stAppViewContainer"] [data-testid="stMetricValue"] * {{
            color: {TEXT_DARK} !important;
        }}

        footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------
# Model loading (trains automatically on first run)
# ------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_model_and_metadata():
    if not (os.path.exists(MODEL_FILENAME) and os.path.exists(META_FILENAME)):
        train_and_save_model()
    model = joblib.load(MODEL_FILENAME)
    metadata = joblib.load(META_FILENAME)
    return model, metadata


# ------------------------------------------------------------------
# Feature engineering for a single new order (mirrors the notebook)
# ------------------------------------------------------------------
def build_features(raw: dict, metadata: dict) -> pd.DataFrame:
    input_df = pd.DataFrame([raw])

    for col in metadata["feature_names"]:
        if col not in input_df.columns:
            input_df[col] = metadata["defaults"].get(col, 0)

    traffic_map = {"Low": 1, "Medium": 2, "High": 3}
    input_df["Traffic_Numeric"] = input_df["Traffic_Level"].map(traffic_map).fillna(2)

    input_df["Distance_x_Traffic"] = input_df["Delivery_Distance_km"] * input_df["Traffic_Numeric"]
    input_df["Is_Peak_Hour"] = input_df["Order_Hour"].apply(
        lambda x: 1 if (12 <= x <= 15 or 18 <= x <= 22) else 0
    )
    input_df["Is_Weekend"] = input_df["Order_DayOfWeek_Num"].apply(lambda x: 1 if x in [4, 5] else 0)
    input_df["Traffic_Delay_Risk"] = input_df["Distance_x_Traffic"] * (1 + 0.5 * input_df["Is_Peak_Hour"])

    input_df = input_df[metadata["feature_names"]]
    return input_df


def predict(model, metadata, raw: dict) -> dict:
    input_df = build_features(raw, metadata)
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]
    return {
        "Is_Delayed": int(prediction),
        "Delay_Probability_Percent": round(float(probability) * 100, 2),
        "Status": "Delay Expected ⚠️" if prediction == 1 else "On Time ✅",
    }


def gauge_chart(probability: float):
    color = RED if probability >= 50 else GREEN
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=probability,
            number={"suffix": "%", "font": {"size": 34, "color": TEXT_DARK}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": TEXT_DARK},
                "bar": {"color": color},
                "bgcolor": "white",
                "steps": [
                    {"range": [0, 40], "color": "#e6f6ef"},
                    {"range": [40, 70], "color": "#fdeecb"},
                    {"range": [70, 100], "color": "#fbdada"},
                ],
            },
            title={"text": "Delay Probability", "font": {"color": TEXT_DARK, "size": 16}},
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT_DARK},
    )
    return fig


def donut_chart(labels, values, colors, title):
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors),
            textinfo="percent",
            textfont=dict(color="white", size=12),
        )
    )
    fig.update_layout(
        title={"text": title, "font": {"color": TEXT_DARK, "size": 14}},
        height=270,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, font=dict(color=TEXT_DARK, size=11)),
    )
    return fig


# ------------------------------------------------------------------
# App
# ------------------------------------------------------------------
def main():
    inject_css()
    inject_ltr_fix()

    with st.spinner("Loading model..."):
        model, metadata = load_model_and_metadata()

    cat_values = metadata.get("categorical_values", {})
    traffic_opts = cat_values.get("Traffic_Level", ["Low", "Medium", "High"])
    weather_opts = cat_values.get("Weather_Conditions", ["Clear", "Rainy", "Cloudy", "Stormy", "Foggy"])
    vehicle_opts = cat_values.get("Vehicle_Type", ["Bike", "Motorcycle", "Car", "Scooter"])

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("## 🛵 talabat\n### Delivery Delay Predictor")
        st.caption("Smarter deliveries, fewer delays")
        st.markdown("---")
        st.markdown(
            """
            **How it works**

            Fill in the order details on the
            **Predict** tab, then click
            *Predict Delivery Status* to see
            whether the order is likely to
            arrive on time or late.
            """
        )
        st.markdown("---")
        st.caption("NTI Graduation Project · Built with Streamlit & scikit-learn")

    # ---------------- BRAND BANNER ----------------
    st.markdown(
        """
        <div class="brand-banner">
            <div class="tag">DELIVERY INTELLIGENCE</div>
            <h1>🛵 talabat</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------- KPI ROW ----------------
    metrics = metadata.get("metrics", {})
    acc = metrics.get("Accuracy", 0) * 100
    f1 = metrics.get("F1-Score", 0) * 100
    auc = metrics.get("ROC-AUC", 0) * 100
    n_total = metadata.get("n_train", 0) + metadata.get("n_test", 0)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_card("📦", "Orders Trained On", f"{n_total:,}"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("🎯", "Model Accuracy", f"{acc:.1f}%"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("⚖️", "F1-Score", f"{f1:.1f}%"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("📈", "ROC-AUC", f"{auc:.1f}%"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab_predict, tab_insights, tab_about = st.tabs(["🔮  Predict", "📊  Model Insights", "ℹ️  About"])

    # ---------------- PREDICT TAB ----------------
    with tab_predict:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Enter Order Details</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            distance = st.slider("📍 Delivery Distance (km)", 0.5, 30.0, 5.0, 0.1)
            traffic = st.selectbox(
                "🚦 Traffic Level", traffic_opts,
                index=min(1, len(traffic_opts) - 1),
                key="pred_traffic",
            )
            weather = st.selectbox("🌦️ Weather Conditions", weather_opts, key="pred_weather")

        with col2:
            vehicle = st.selectbox("🚗 Vehicle Type", vehicle_opts, key="pred_vehicle")
            order_hour = st.slider("⏰ Order Hour (0-23)", 0, 23, 19)
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day = st.selectbox("📅 Day of Week", day_names, index=4)
            order_day_num = day_names.index(day)

        st.markdown("")
        predict_clicked = st.button("🔍 Predict Delivery Status", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if predict_clicked:
            raw_order = {
                "Delivery_Distance_km": distance,
                "Traffic_Level": traffic,
                "Weather_Conditions": weather,
                "Vehicle_Type": vehicle,
                "Order_Hour": order_hour,
                "Order_DayOfWeek_Num": order_day_num,
            }

            result = predict(model, metadata, raw_order)

            res_col, gauge_col = st.columns([1, 1])

            with res_col:
                box_class = "result-delay" if result["Is_Delayed"] == 1 else "result-ontime"
                st.markdown(
                    f"""
                    <div class="{box_class}">
                        <h2>{result['Status']}</h2>
                        <p>Estimated delay probability: <b>{result['Delay_Probability_Percent']}%</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<p class="section-title">Order Summary</p>', unsafe_allow_html=True)
                summary_df = pd.DataFrame(
                    {
                        "Field": ["Distance", "Traffic", "Weather", "Vehicle", "Order Hour", "Day"],
                        "Value": [f"{distance} km", traffic, weather, vehicle, f"{order_hour}:00", day],
                    }
                )
                st.dataframe(summary_df, hide_index=True, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with gauge_col:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.plotly_chart(gauge_chart(result["Delay_Probability_Percent"]), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- INSIGHTS TAB ----------------
    with tab_insights:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.plotly_chart(
                donut_chart(
                    ["Accuracy", "Miss"],
                    [acc, 100 - acc],
                    [ORANGE, "#f1e4da"],
                    "Accuracy",
                ),
                use_container_width=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.plotly_chart(
                donut_chart(
                    ["Precision", "Recall", "F1-Score"],
                    [metrics.get("Precision", 0) * 100, metrics.get("Recall", 0) * 100, metrics.get("F1-Score", 0) * 100],
                    [ORANGE_DARK, ORANGE, ORANGE_LIGHT],
                    "Precision / Recall / F1",
                ),
                use_container_width=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Dataset Split</p>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        d1.metric("Training samples", metadata.get("n_train", "—"))
        d2.metric("Test samples", metadata.get("n_test", "—"))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Feature Importance</p>', unsafe_allow_html=True)
        try:
            classifier = model.named_steps["classifier"]
            preprocessor = model.named_steps["preprocessor"]
            feature_names_out = preprocessor.get_feature_names_out()
            importances = classifier.feature_importances_

            imp_df = (
                pd.DataFrame({"Feature": feature_names_out, "Importance": importances})
                .sort_values("Importance", ascending=False)
                .head(15)
            )
            st.bar_chart(imp_df.set_index("Feature"))
        except Exception:
            st.info("Feature importance is not available for this model configuration.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- ABOUT TAB ----------------
    with tab_about:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">About this Project</p>', unsafe_allow_html=True)
        st.markdown(
            """
            This app is the deployment layer for the **NTI Graduation** delivery-delay
            prediction project. It follows the same 7-phase pipeline built in the
            training notebook:

            1. **Data Preparation** — load raw delivery orders
            2. **Feature Engineering** — peak-hour flags, weekend flags, traffic-risk score
            3. **Model Training** — Logistic Regression, Decision Tree, Random Forest
            4. **Evaluation** — Accuracy, Precision, Recall, F1, ROC-AUC
            5. **Model Comparison** — Random Forest selected as final model
            6. **Final Packaging** — full sklearn `Pipeline` saved with `joblib`
            7. **Deployment** — this Streamlit interface

            Built with `scikit-learn`, `pandas`, `Plotly`, and `Streamlit`.
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
