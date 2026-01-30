"""
GOTHAM // ORDER BOOK VISUALIZER
Limit Order Book (LOB) Visualizer with Palantir Gotham Aesthetic
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
from datetime import datetime

from data_generator import (
    generate_order_book, 
    generate_trade_history, 
    update_mid_price
)

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="GOTHAM // Order Book",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# LOAD CUSTOM CSS
# =============================================================================
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if 'mid_price' not in st.session_state:
    st.session_state.mid_price = 100.0

if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0

# =============================================================================
# COLOR PALETTE (GOTHAM)
# =============================================================================
COLORS = {
    'bg_primary': '#0a0e14',
    'bg_secondary': '#1a1f2c',
    'border': '#2a3441',
    'text_primary': '#e6edf3',
    'text_secondary': '#7d8590',
    'accent_green': '#00ff88',
    'accent_red': '#ff3366',
    'accent_blue': '#00d4ff',
    'grid': '#1e2530'
}

# =============================================================================
# DEPTH CHART COMPONENT
# =============================================================================
def create_depth_chart(order_book) -> go.Figure:
    """Crée le graphique de profondeur du carnet d'ordres."""
    
    fig = go.Figure()
    
    # Bids (côté gauche - vert)
    fig.add_trace(go.Scatter(
        x=order_book.bids['price'],
        y=order_book.bids['cumulative'],
        fill='tozeroy',
        fillcolor='rgba(0, 255, 136, 0.15)',
        line=dict(color=COLORS['accent_green'], width=2),
        name='BIDS',
        hovertemplate='<b>BID</b><br>Price: %{x:.4f}<br>Volume: %{y:,.0f}<extra></extra>'
    ))
    
    # Asks (côté droit - rouge)
    fig.add_trace(go.Scatter(
        x=order_book.asks['price'],
        y=order_book.asks['cumulative'],
        fill='tozeroy',
        fillcolor='rgba(255, 51, 102, 0.15)',
        line=dict(color=COLORS['accent_red'], width=2),
        name='ASKS',
        hovertemplate='<b>ASK</b><br>Price: %{x:.4f}<br>Volume: %{y:,.0f}<extra></extra>'
    ))
    
    # Mid price line
    fig.add_vline(
        x=order_book.mid_price,
        line=dict(color=COLORS['accent_blue'], width=1, dash='dash'),
        annotation_text=f"MID: {order_book.mid_price:.4f}",
        annotation_position="top",
        annotation_font=dict(color=COLORS['accent_blue'], size=10)
    )
    
    # Layout configuration
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['bg_primary'],
        font=dict(family='JetBrains Mono, monospace', color=COLORS['text_primary']),
        title=dict(
            text='DEPTH CHART',
            font=dict(size=12, color=COLORS['text_secondary']),
            x=0,
            y=0.98
        ),
        xaxis=dict(
            title=dict(text='PRICE', font=dict(size=10, color=COLORS['text_secondary'])),
            gridcolor=COLORS['grid'],
            zerolinecolor=COLORS['grid'],
            tickfont=dict(size=9, color=COLORS['text_secondary']),
            showgrid=True,
            gridwidth=1
        ),
        yaxis=dict(
            title=dict(text='CUMULATIVE VOLUME', font=dict(size=10, color=COLORS['text_secondary'])),
            gridcolor=COLORS['grid'],
            zerolinecolor=COLORS['grid'],
            tickfont=dict(size=9, color=COLORS['text_secondary']),
            showgrid=True,
            gridwidth=1
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=10, color=COLORS['text_secondary']),
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=60, r=20, t=60, b=50),
        height=450,
        hovermode='x unified'
    )
    
    return fig


# =============================================================================
# TRADE HISTORY STYLED TABLE
# =============================================================================
def create_trade_history_component(df: pd.DataFrame):
    """Affiche l'historique des trades avec un style Gotham."""
    
    # Header du widget
    st.markdown(f"""
        <div style="
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            padding: 1rem 1.5rem;
            margin-bottom: 0;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid {COLORS['border']};
            ">
                <span style="
                    font-size: 0.8rem;
                    color: {COLORS['text_secondary']};
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    font-family: 'JetBrains Mono', monospace;
                ">TRADE HISTORY</span>
                <span style="
                    color: {COLORS['text_secondary']};
                    font-size: 0.7rem;
                    font-family: 'JetBrains Mono', monospace;
                ">LAST 10 EXECUTIONS</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Style the dataframe
    def color_side(val):
        if val == 'BUY':
            return f'color: {COLORS["accent_green"]}; font-weight: 600;'
        else:
            return f'color: {COLORS["accent_red"]}; font-weight: 600;'
    
    def format_value(val):
        return f'color: {COLORS["accent_blue"]};'
    
    # Format dataframe
    df_display = df.copy()
    df_display['side'] = df_display['side'].apply(lambda x: f"▲ {x}" if x == 'BUY' else f"▼ {x}")
    df_display['price'] = df_display['price'].apply(lambda x: f"{x:.4f}")
    df_display['volume'] = df_display['volume'].apply(lambda x: f"{x:,.2f}")
    df_display['value'] = df_display['value'].apply(lambda x: f"${x:,.2f}")
    df_display.columns = ['TIME', 'SIDE', 'PRICE', 'VOLUME', 'VALUE']
    
    # Use st.dataframe for reliable rendering
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=380
    )


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    # Header
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
            .gotham-header {
                background-color: #0a0e14;
                padding: 25px;
                border-left: 4px solid #00d1ff;
                border-radius: 0px 5px 5px 0px;
                margin-bottom: 25px;
                font-family: 'JetBrains Mono', monospace;
            }
            .analyst-tag {
                color: #00d1ff;
                font-weight: bold;
                letter-spacing: 1.5px;
                font-size: 0.85em;
                text-transform: uppercase;
                margin-bottom: 5px;
            }
            .metadata-tag {
                color: #565d66;
                font-size: 0.75em;
                text-transform: uppercase;
                font-family: 'JetBrains Mono', monospace;
            }
            .status-blink {
                color: #00ff41;
                animation: blinker 2s linear infinite;
            }
            @keyframes blinker {
                50% { opacity: 0.3; }
            }
            .description {
                color: #8a8d91;
                font-size: 0.85em;
                margin-top: 15px;
                line-height: 1.5;
                max-width: 850px;
                border-top: 1px solid #1e2631;
                padding-top: 10px;
            }
            .highlight {
                color: #ffffff;
                font-weight: bold;
            }
        </style>
        <div class="gotham-header">
            <h1 style="color: white; margin: 0; font-size: 1.6em; letter-spacing: -1px;">🛰️ LOB_OPERATOR // PROJECT: NEXUS-EYE</h1>
            <p class="analyst-tag">
                ANALYST: YOUN GOGER-LE GOUX | STATUS: <span class="status-blink">● LIVE_FEED_ACTIVE</span>
            </p>
            <p class="metadata-tag">
                TARGET_ASSET: <span class="highlight">BTC/USDT</span> | 
                DATA_SOURCE: <span class="highlight">BINANCE_CORE_LOB_API</span> | 
                LATENCY: <span class="highlight">14ms</span>
            </p>
            <p class="description">
                <b>Market Microstructure Intelligence:</b> Real-time visualization of the Limit Order Book (LOB). 
                This terminal maps the friction between supply (Asks) and demand (Bids), identifying liquidity walls 
                and price levels where institutional volume is concentrated before market execution.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Update mid price with some random walk
    st.session_state.mid_price = update_mid_price(st.session_state.mid_price)
    
    # Generate data
    order_book = generate_order_book(
        mid_price=st.session_state.mid_price,
        spread_bps=8.0,
        n_levels=25
    )
    
    trade_history = generate_trade_history(
        mid_price=st.session_state.mid_price,
        n_trades=10
    )
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="widget-container" style="text-align: center;">
                <div class="kpi-label">MID PRICE</div>
                <div class="kpi-value">{order_book.mid_price:.4f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        best_bid = order_book.bids['price'].iloc[0]
        st.markdown(f"""
            <div class="widget-container" style="text-align: center;">
                <div class="kpi-label">BEST BID</div>
                <div class="kpi-value" style="color: {COLORS['accent_green']}; text-shadow: 0 0 20px rgba(0, 255, 136, 0.4);">{best_bid:.4f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        best_ask = order_book.asks['price'].iloc[0]
        st.markdown(f"""
            <div class="widget-container" style="text-align: center;">
                <div class="kpi-label">BEST ASK</div>
                <div class="kpi-value" style="color: {COLORS['accent_red']}; text-shadow: 0 0 20px rgba(255, 51, 102, 0.4);">{best_ask:.4f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        spread = (best_ask - best_bid) / order_book.mid_price * 10000
        st.markdown(f"""
            <div class="widget-container" style="text-align: center;">
                <div class="kpi-label">SPREAD (BPS)</div>
                <div class="kpi-value" style="color: {COLORS['accent_blue']};">{spread:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Main Content
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # Depth Chart
        depth_chart = create_depth_chart(order_book)
        st.plotly_chart(depth_chart, width='stretch', config={'displayModeBar': False})
    
    with right_col:
        # Trade History
        create_trade_history_component(trade_history)
    
    # Footer timestamp
    st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid {COLORS['border']};">
            <span style="color: {COLORS['text_secondary']}; font-size: 0.7rem; letter-spacing: 2px;">
                LAST UPDATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} UTC
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh every 1.5 seconds
    time.sleep(1.5)
    st.rerun()


if __name__ == "__main__":
    main()
