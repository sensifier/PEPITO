import requests
import io
import ccxt
import logging
import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_image
from datetime import datetime
from config import CHART_COLORS, SHOW_NEGATIVE_PRICE_CHARTS

class BitcoinChartGenerator:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.colors = CHART_COLORS

    def fetch_ohlcv_data(self, start_timestamp, end_timestamp):
        """Fetch OHLCV data from exchange"""
        try:
            duration = end_timestamp - start_timestamp
            duration_hours = duration / 3600
            
            # Determine appropriate timeframe
            if duration_hours <= 4:
                timeframe = '1m'
            elif duration_hours <= 24:
                timeframe = '5m'
            elif duration_hours <= 72:
                timeframe = '15m'
            else:
                timeframe = '1h'
            
            ohlcv = self.exchange.fetch_ohlcv(
                symbol='BTC/USDT',
                timeframe=timeframe,
                since=int(start_timestamp * 1000),
                limit=500
            )
            
            if not ohlcv:
                return None
                
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
            
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def create_chart(self, start_time, end_time, duration_str, event_type, show_chart=False):
        """Create the Bitcoin chart"""
        try:
            df = self.fetch_ohlcv_data(start_time, end_time)
            if df is None or df.empty:
                logging.error("No data available for chart")
                return None
            
            # Calculate price change
            start_price = df['open'].iloc[0]
            end_price = df['close'].iloc[-1]
            price_change = ((end_price - start_price) / start_price) * 100
            
            # Check if we should skip negative price changes
            if not SHOW_NEGATIVE_PRICE_CHARTS and price_change < 0:
                logging.info(f"Skipping chart due to negative price change: {price_change:.2f}%")
                return None
                
            price_change_color = self.colors['up'] if price_change >= 0 else self.colors['down']

            # Create the chart figure
            fig = self._create_candlestick_chart(df, price_change, price_change_color)
            
            # Add additional annotations
            self._add_price_annotations(fig, df, start_price, end_price)
            self._add_watermark(fig)
            self._add_title(fig, event_type)

            return fig
            
        except Exception as e:
            logging.error(f"Error creating chart: {e}")
            return None

    def _create_candlestick_chart(self, df, price_change, price_change_color):
        """Create base candlestick chart"""
        fig = go.Figure(data=[
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                increasing_line_color=self.colors['up'],
                decreasing_line_color=self.colors['down'],
                increasing_fillcolor=self.colors['up'],
                decreasing_fillcolor=self.colors['down'],
                line=dict(width=1),
                name='BTCUSDT'
            )
        ])

        # Add price change annotation
        fig.add_annotation(
            x=df['timestamp'].iloc[len(df)//2],
            y=df['high'].max(),
            text=f"{price_change:+.2f}%",
            font=dict(size=36, color=price_change_color),
            showarrow=False,
            opacity=0.9,
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor=price_change_color,
            borderwidth=2,
            borderpad=10
        )

        # Update layout
        fig.update_layout(
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            xaxis_rangeslider_visible=False,
            height=600,
            yaxis=dict(
                title="Price (USDT)",
                titlefont=dict(color=self.colors['text']),
                tickfont=dict(color=self.colors['text']),
                showgrid=False,
                side='left',
                tickformat='$,.0f'
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(color=self.colors['text']),
                type='date'
            ),
            margin=dict(t=50, l=60, r=40, b=90),
            showlegend=False,
            hoverlabel=dict(
                bgcolor=self.colors['background'],
                font_size=14
            )
        )

        return fig

    def _add_price_annotations(self, fig, df, start_price, end_price):
        """Add price labels to chart"""
        fig.add_annotation(
            x=df['timestamp'].iloc[0],
            y=start_price,
            text=f"${start_price:,.2f}",
            font=dict(size=12, color=self.colors['text']),
            showarrow=False,
            xanchor='right',
            yanchor='middle',
            xshift=-10
        )

        fig.add_annotation(
            x=df['timestamp'].iloc[-1],
            y=end_price,
            text=f"${end_price:,.2f}",
            font=dict(size=12, color=self.colors['text']),
            showarrow=False,
            xanchor='left',
            yanchor='middle',
            xshift=10
        )

    def _add_watermark(self, fig):
        """Add #PepitoIsSatoshi watermark"""
        fig.add_annotation(
            x=0.5,
            y=0.5,
            xref='paper',
            yref='paper',
            text="#PepitoIsSatoshi",
            showarrow=False,
            font=dict(
                family='Helvetica',
                size=50,
                color='rgba(0, 100, 100, 0.25)'
            ),
            textangle=-30,
            align='center',
            opacity=0.5
        )

    def _add_title(self, fig, event_type):
        """Add title to chart"""
        fig.add_annotation(
            x=0.5,
            y=-0.2,
            xref='paper',
            yref='paper',
            text=f"Bitcoin Price During<br>Pépito's {'Indoor' if event_type == 'in' else 'Outdoor'} Adventure",
            showarrow=False,
            font=dict(
                family='Helvetica',
                size=20,
                color=self.colors['up']
            ),
            align='center',
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor=self.colors['up'],
            borderwidth=2,
            borderpad=10,
            opacity=0.9,
            xanchor='center',
        )

    def create_chart_for_period(self, start_time, end_time, duration_str, event_type):
        """Generate and send Bitcoin chart for a specific period"""
        try:
            fig = self.create_chart(start_time, end_time, duration_str, event_type, show_chart=False)
            if fig is None:
                return None

            # Convert the figure to PNG bytes
            img_bytes = to_image(fig, format="png")
            return io.BytesIO(img_bytes)
        except Exception as e:
            logging.error(f"Error generating Bitcoin chart: {e}")
            return None
