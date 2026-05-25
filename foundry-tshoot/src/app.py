import json
import time
from dataclasses import asdict

import streamlit as st

from healthprobe.registry import PLUGINS


st.set_page_config(
    page_title="Azure Connectivity Health Probe",
    layout="wide",
)

st.title("Azure Connectivity & Data Plane Health Probe")

st.caption(
    "Extensible Streamlit diagnostics for DNS, TLS, HTTP, Azure identity, "
    "and service-specific data-plane checks."
)

if "last_report" not in st.session_state:
    st.session_state.last_report = {
        "generated_at": None,
        "results": [],
    }


def render_result(result):
    if result.ok:
        st.success(f"{result.service} / {result.check_name}: {result.message}")
    else:
        st.error(f"{result.service} / {result.check_name}: {result.message}")

    with st.expander("Details", expanded=False):
        st.json(asdict(result))


tabs = st.tabs([plugin.name for plugin in PLUGINS] + ["Report"])

for tab, plugin in zip(tabs[:-1], PLUGINS):
    with tab:
        st.subheader(plugin.name)
        config = plugin.render_config()

        if st.button(f"Run {plugin.name} checks", key=f"run_{plugin.name}"):
            results = plugin.run(config)

            for result in results:
                render_result(result)

            st.session_state.last_report = {
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "plugin": plugin.name,
                "results": [asdict(r) for r in results],
            }

with tabs[-1]:
    st.subheader("Latest report")

    st.json(st.session_state.last_report)

    st.download_button(
        "Download JSON report",
        data=json.dumps(st.session_state.last_report, indent=2),
        file_name="azure_health_probe_report.json",
        mime="application/json",
    )