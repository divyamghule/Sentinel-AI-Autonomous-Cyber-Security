import streamlit as st
import requests

st.set_page_config(page_title="Sentinel AI", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .sentinel-hero {
        border: 1px solid rgba(255, 255, 255, 0.12);
        background: linear-gradient(130deg, rgba(12, 28, 44, 0.9), rgba(8, 55, 44, 0.75));
        padding: 1rem 1.2rem;
        border-radius: 14px;
        margin-bottom: 1rem;
    }

    .sentinel-banner {
        padding: 0.9rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.14);
        margin: 0.3rem 0 0.8rem 0;
    }

    .banner-blocked {
        background: linear-gradient(120deg, rgba(95, 8, 8, 0.9), rgba(155, 25, 25, 0.65));
    }

    .banner-suspicious {
        background: linear-gradient(120deg, rgba(110, 70, 8, 0.9), rgba(170, 110, 15, 0.65));
    }

    .banner-allowed {
        background: linear-gradient(120deg, rgba(8, 66, 34, 0.9), rgba(18, 122, 66, 0.65));
    }

    .indicator-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 0.4rem;
    }

    .indicator-chip {
        background: rgba(31, 119, 255, 0.16);
        border: 1px solid rgba(31, 119, 255, 0.4);
        color: #c8e0ff;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        line-height: 1.2;
    }

    .keyword-chip {
        background: rgba(255, 193, 7, 0.16);
        border: 1px solid rgba(255, 193, 7, 0.40);
        color: #ffe7aa;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
    }

    .misspelled-chip {
        background: rgba(255, 88, 88, 0.12);
        border: 1px solid rgba(255, 88, 88, 0.42);
        color: #ffb6b6;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
    }

    .mini-label {
        display: inline-block;
        margin-bottom: 0.35rem;
        color: #c7d5e0;
        font-size: 0.86rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .section-note {
        color: #a5b9cc;
        font-size: 0.94rem;
    }

    .decision-badge {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.55rem;
    }

    .decision-badge.blocked {
        background: rgba(255, 82, 82, 0.18);
        color: #ffb5b5;
        border: 1px solid rgba(255, 82, 82, 0.45);
    }

    .decision-badge.suspicious {
        background: rgba(255, 193, 7, 0.16);
        color: #ffe29c;
        border: 1px solid rgba(255, 193, 7, 0.45);
    }

    .decision-badge.allowed {
        background: rgba(0, 200, 120, 0.16);
        color: #aaf0cf;
        border: 1px solid rgba(0, 200, 120, 0.35);
    }

    .report-card {
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        background: rgba(11, 18, 31, 0.72);
        box-shadow: 0 16px 42px rgba(0, 0, 0, 0.18);
        margin-bottom: 1rem;
    }

    .report-title {
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1;
        margin: 0.15rem 0 0.2rem 0;
    }

    .report-subtitle {
        color: #a5b9cc;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛡️ Sentinel AI — Autonomous Cyber-Security")
st.markdown(
    """
    <div class="sentinel-hero">
      <strong>Adaptive Threat Intelligence</strong><br/>
      URL, file, and communication scans with rule+model hybrid risk scoring.
    </div>
    """,
    unsafe_allow_html=True,
)

# --- API Configuration ---
API = st.sidebar.text_input("API URL", "http://localhost:8000")


def _escape_html(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_indicator_chips(indicators):
    if not indicators:
        return
    chips = "".join([f'<span class="indicator-chip">{_escape_html(i)}</span>' for i in indicators])
    st.markdown(f'<div class="indicator-wrap">{chips}</div>', unsafe_allow_html=True)


def render_chip_group(items, chip_class):
    if not items:
        return
    chips = "".join([f'<span class="{chip_class}">{_escape_html(i)}</span>' for i in items])
    st.markdown(f'<div class="indicator-wrap">{chips}</div>', unsafe_allow_html=True)


def render_decision_banner(item_name, decision, message):
    if decision == "blocked":
        cls = "banner-blocked"
        title = "🚨 Threat Detected"
        badge_cls = "blocked"
        badge_text = "BLOCKED"
    elif decision == "suspicious":
        cls = "banner-suspicious"
        title = "⚠️ Suspicious Signal"
        badge_cls = "suspicious"
        badge_text = "SUSPICIOUS"
    else:
        cls = "banner-allowed"
        title = "✅ No Strong Threat"
        badge_cls = "allowed"
        badge_text = "ALLOWED"

    st.markdown(
        f"""
        <div class="sentinel-banner {cls}">
          <span class="decision-badge {badge_cls}">{badge_text}</span><br/>
          <strong>{title}</strong><br/>
          Target: {_escape_html(item_name)}<br/>
          {_escape_html(message)}
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Main Tabs ---
file_tab, comms_tab, stats_tab = st.tabs(["File & URL Scanner", "Communications Analyzer", "System Stats"])

# --- File & URL Scanner Tab ---
with file_tab:
    st.header("Pre-Execution Scanner")
    st.markdown('<p class="section-note">Analyze individual files or URLs for potential threats before you open them.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Scan URL")
        url_to_scan = st.text_input("Enter URL to scan")
        if st.button("Scan URL"):
            if url_to_scan:
                try:
                    r = requests.post(f"{API}/scan/url", data={"url": url_to_scan})
                    st.session_state['scan_result'] = r.json()
                except Exception as e:
                    st.error(f"Could not connect to API: {e}")
            else:
                st.warning("Please enter a URL.")

    with col2:
        st.subheader("Upload & Scan File")
        uploaded_file = st.file_uploader("Choose a file to scan", type=None)
        if uploaded_file:
            if st.button("Scan File"):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    r = requests.post(f"{API}/scan/file", files=files)
                    st.session_state['scan_result'] = r.json()
                except Exception as e:
                    st.error(f"Could not connect to API: {e}")

    st.markdown("---")
    st.subheader("Scan Results")

    if 'scan_result' not in st.session_state:
        st.session_state['scan_result'] = None

    if st.session_state['scan_result']:
        res = st.session_state['scan_result']
        
        item_name = res.get("file") or res.get("url", "N/A")
        score = res.get("score", 0.0)
        decision = res.get("decision", "blocked" if res.get("blocked", False) else "allowed")
        message = res.get("message", "No strong threat found.")

        render_decision_banner(item_name, decision, message)
        
        st.progress(score, text=f"Threat Score: {score:.2f}")

        res_col1, res_col2 = st.columns(2)
        res_col1.metric("Score", f"{score:.2f}")
        res_col2.metric("Status", decision.capitalize())

        if "model_score" in res and "rule_score" in res:
            m1, m2 = st.columns(2)
            m1.metric("Model Score", f"{res.get('model_score', 0.0):.2f}")
            m2.metric("Rule Score", f"{res.get('rule_score', 0.0):.2f}")

        if res.get("indicators"):
            st.caption("Risk indicators")
            render_indicator_chips(res.get("indicators"))
    else:
        st.info("Scan a file or URL to see the results here.")


# --- Communications Analyzer Tab ---
with comms_tab:
    st.header("Real-time Communications Analyzer")
    st.markdown('<p class="section-note">Paste content from messages or emails to check for phishing, scams, and suspicious links.</p>', unsafe_allow_html=True)

    # --- Result Rendering Function ---
    def render_text_analysis_results(results):
        if not results:
            return

        st.markdown("---")
        decision = results.get("decision", "blocked" if results.get("is_threat") else "allowed")
        badge_cls = decision if decision in ["blocked", "suspicious", "allowed"] else "allowed"
        badge_text = decision.upper()

        st.markdown(
            f"""
            <div class="report-card">
                <div class="decision-badge {badge_cls}">{badge_text}</div>
                <div class="report-title">Analysis Report</div>
                <div class="report-subtitle">Smart inspection of message content, links, and threat signals.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if decision == "blocked":
            st.error("Threat detected.", icon="🚨")
        elif decision == "suspicious":
            st.warning("Suspicious content found.", icon="⚠️")
        else:
            st.success("No strong threat found.", icon="✅")

        st.markdown(f"**Conclusion:** *{results.get('conclusion')}*")

        st.progress(results.get("overall_score", 0), text=f"Overall Threat Score: {results.get('overall_score', 0):.2f}")

        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            st.metric("Suspicious Keywords", len(results.get("suspicious_keywords_found", [])))
            if results.get("suspicious_keywords_found"):
                with st.expander("Show Keywords"):
                    st.markdown('<span class="mini-label">Suspicious Keywords</span>', unsafe_allow_html=True)
                    render_chip_group(results.get("suspicious_keywords_found"), "keyword-chip")

        with res_col2:
            st.metric("Misspelled Words", len(results.get("misspelled_words", [])))
            if results.get("misspelled_words"):
                with st.expander("Show Misspelled"):
                    st.markdown('<span class="mini-label">Misspelled Words</span>', unsafe_allow_html=True)
                    render_chip_group(results.get("misspelled_words"), "misspelled-chip")

        with res_col3:
            st.metric("Links Found", len(results.get("urls", [])))
            urls = results.get("urls", [])
            if urls:
                with st.expander("Show Link Analysis"):
                    for u in urls:
                        label = f"{u.get('url', 'URL')} ({u.get('decision', 'allowed')})"
                        st.markdown(f"**{label}**")
                        render_indicator_chips(u.get("indicators", []))
                        st.caption(
                            f"Score: {u.get('score', 0):.2f} | Model: {u.get('model_score', 0):.2f} | Rule: {u.get('rule_score', 0):.2f}"
                        )
                        st.markdown("---")

        st.caption(f"Decision: {decision.capitalize()}")

    # --- Analysis Logic ---
    def analyze_text(text_content):
        if text_content:
            try:
                r = requests.post(f"{API}/scan/text", data={"text": text_content})
                st.session_state['text_analysis_result'] = r.json()
            except Exception as e:
                st.error(f"Could not connect to API: {e}")
        else:
            st.warning("Please paste some content to analyze.")

    if 'text_analysis_result' not in st.session_state:
        st.session_state['text_analysis_result'] = None

    whatsapp_pane, gmail_pane, sms_pane = st.tabs(["WhatsApp", "Gmail", "SMS"])

    with whatsapp_pane:
        st.subheader("WhatsApp Message Analysis")
        wa_message = st.text_area("Paste WhatsApp message content here:", height=200, key="wa_input")
        if st.button("Analyze WhatsApp Message"):
            analyze_text(wa_message)

    with gmail_pane:
        st.subheader("Gmail Analysis")
        gmail_subject = st.text_input("Subject:", key="gmail_subject")
        gmail_body = st.text_area("Paste Gmail body here:", height=250, key="gmail_body")
        if st.button("Analyze Gmail"):
            full_email_text = f"Subject: {gmail_subject}\n\n{gmail_body}"
            analyze_text(full_email_text)

    with sms_pane:
        st.subheader("SMS/Text Message Analysis")
        sms_message = st.text_area("Paste SMS content here:", height=200, key="sms_input")
        if st.button("Analyze SMS"):
            analyze_text(sms_message)
            
    # Render results at the bottom of the tab
    render_text_analysis_results(st.session_state['text_analysis_result'])


# --- System Stats Tab ---
with stats_tab:
    st.header("System Health & Statistics")
    if st.button("Refresh Stats"):
        try:
            r = requests.get(f"{API}/stats", timeout=3)
            stats_data = r.json()
            
            stat_col1, stat_col2 = st.columns(2)
            stat_col1.metric("Total Scans Performed", stats_data.get("scans", 0))
            stat_col2.metric("Total Threats Blocked", stats_data.get("blocked", 0))
            
            st.info("Last scan details:")
            st.json(stats_data.get("last", "No scans yet."))

        except Exception as e:
            st.error(f"Could not fetch stats: {e}")
    else:
        st.info("Click 'Refresh Stats' to load the latest system statistics.")
