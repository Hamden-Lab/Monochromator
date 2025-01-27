import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
st.set_page_config(layout="wide",)
# Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
# after it's been refreshed 100 times.
count = st_autorefresh(interval=2000, key="counter")
HtmlFile = open(r"D:\OneDrive - University of Arizona\optical sciences\Research\Erika Hamden Group\Code\Cryocooler_Control_software\Final_code\temperature_log\runtime.html", 'r', encoding='utf-8')
source_code = HtmlFile.read() 
components.html(source_code,height=1200)