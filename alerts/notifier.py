import streamlit as st

class StreamlitNotifier:
    @staticmethod
    def show_scheduler_status(running: bool, interval: int):
        """Tampilkan status scheduler"""
        if running:
            st.success(f"✅ Auto-check aktif (setiap {interval} menit)")
        else:
            st.info("⏸️ Auto-check tidak aktif")
    
    @staticmethod
    def show_triggered(triggered_list: list):
        """Tampilkan alert yang ter-trigger"""
        if triggered_list:
            for item in triggered_list:
                if isinstance(item, dict):
                    st.warning(f"🚨 {item.get('ticker', 'Unknown')} — {item.get('condition', 'Alert')} triggered!")
                else:
                    st.warning(f"🚨 Alert triggered: {item}")
