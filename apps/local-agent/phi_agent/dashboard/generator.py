"""
Dashboard generator for Streamlit apps
"""
from pathlib import Path
from typing import Optional, List, Literal
from pydantic import BaseModel


class ChartSpec(BaseModel):
    """Specification for a chart"""
    type: Literal["bar", "line", "pie", "scatter"]
    title: str
    data_source: str  # CSV path or inline data key
    x_field: str
    y_field: str
    color: Optional[str] = None


class TableSpec(BaseModel):
    """Specification for a table"""
    title: str
    data_source: str
    columns: Optional[List[str]] = None


class DashboardSpec(BaseModel):
    """Complete dashboard specification"""
    title: str
    description: Optional[str] = None
    charts: List[ChartSpec] = []
    tables: List[TableSpec] = []


def generate_streamlit_app(spec: DashboardSpec, output_path: Path) -> str:
    """Generate a Streamlit dashboard app from spec"""
    
    app_code = f'''import streamlit as st
import pandas as pd
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
from pathlib import Path

st.set_page_config(
    page_title="{spec.title}",
    layout="wide"
)

st.title("{spec.title}")
'''
    
    if spec.description:
        app_code += f'\nst.markdown("{spec.description}")\n'
    
    # Generate charts
    for chart in spec.charts:
        if HAS_PLOTLY:
            app_code += f'''
# Chart: {chart.title}
try:
    df_chart = pd.read_csv("{chart.data_source}")
    fig = px.{chart.type}(
        df_chart,
        x="{chart.x_field}",
        y="{chart.y_field}",
        title="{chart.title}"
    )
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error loading chart data: {{e}}")
'''
        else:
            app_code += f'''
# Chart: {chart.title}
try:
    df_chart = pd.read_csv("{chart.data_source}")
    st.bar_chart(df_chart.set_index("{chart.x_field}")["{chart.y_field}"])
    st.caption("{chart.title}")
except Exception as e:
    st.error(f"Error loading chart data: {{e}}")
'''
    
    # Generate tables
    for table in spec.tables:
        app_code += f'''
# Table: {table.title}
try:
    df_table = pd.read_csv("{table.data_source}")
    st.subheader("{table.title}")
    if {table.columns}:
        st.dataframe(df_table[{table.columns}], use_container_width=True)
    else:
        st.dataframe(df_table, use_container_width=True)
except Exception as e:
    st.error(f"Error loading table data: {{e}}")
'''
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(app_code)
    
    return str(output_path)

