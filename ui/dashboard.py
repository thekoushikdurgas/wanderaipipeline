"""
Analytics dashboard for the Places Management System.

This module provides comprehensive analytics and visualization capabilities
for analyzing place data, including charts, metrics, and insights.
Optimized with numpy and pandas vectorization for faster response times.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

# Import utilities and configuration
try:
    from utils.settings import analytics_config
    from utils.logger import get_logger
    from utils.error_handlers import handle_errors, safe_execute
except ImportError:
    # Fallback configuration
    class MockAnalyticsConfig:
        chart_height = 400
        chart_width = 600
        default_zoom = 1
        map_style = "open-street-map"
        recent_activity_limit = 10
        place_types = ["restaurant", "hotel", "tourist_attraction"]
    
    analytics_config = MockAnalyticsConfig()
    
    class MockLogger:
        def debug(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def info(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def warning(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
        def error(self, msg, **kwargs): 
            # Mock logger - no operation implementation
            pass
    
    def get_logger(_name):
        # Mock function - parameter name ignored
        return MockLogger()
    
    def handle_errors(**_kwargs):
        # Mock decorator - kwargs ignored
        def decorator(func):
            return func
        return decorator
    
    def safe_execute(op, _name, default=None, _context=None):
        # Mock function - execute operation with basic error handling
        try:
            return op()
        except Exception:  # Catch specific exception type
            return default

logger = get_logger(__name__)


class MetricsCalculator:
    """Calculator for various analytics metrics with numpy/pandas optimization."""
    
    @staticmethod
    @handle_errors(show_user_message=False)
    def calculate_basic_metrics(places_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate basic metrics from places data using vectorized operations.
        
        Args:
            places_df: DataFrame containing places data
            
        Returns:
            Dict containing calculated metrics
        """
        logger.debug("Calculating basic metrics", records_count=len(places_df))
        
        if places_df.empty:
            return {
                'total_places': 0,
                'unique_types': 0,
                'avg_latitude': 0.0,
                'avg_longitude': 0.0,
                'most_common_type': 'N/A',
                'coordinate_spread': {'lat_range': 0.0, 'lon_range': 0.0}
            }
        
        # Use numpy for faster calculations
        lat_array = places_df['latitude'].to_numpy()
        lon_array = places_df['longitude'].to_numpy()
        
        # Extract new columns with default values if missing
        if 'rating' in places_df.columns:
            try:
                # Handle both numeric and string formats
                rating_series = pd.to_numeric(places_df['rating'], errors='coerce').fillna(0.0)
                rating_array = rating_series.to_numpy()
            except Exception as e:
                logger.warning("Error converting rating column", error=str(e))
                rating_array = np.zeros(len(places_df))
        else:
            rating_array = np.zeros(len(places_df))
            
        if 'followers' in places_df.columns:
            try:
                # Handle both numeric and string formats
                followers_series = pd.to_numeric(places_df['followers'], errors='coerce').fillna(0.0)
                followers_array = followers_series.to_numpy()
            except Exception as e:
                logger.warning("Error converting followers column", error=str(e))
                followers_array = np.zeros(len(places_df))
        else:
            followers_array = np.zeros(len(places_df))
        
        metrics = {}
        
        # Vectorized basic counts
        metrics['total_places'] = len(places_df)
        metrics['unique_types'] = places_df['types'].nunique()
        
        # New metrics for rating, followers, and country
        if 'rating' in places_df.columns:
            metrics['avg_rating'] = float(np.mean(rating_array))
            metrics['max_rating'] = float(np.max(rating_array))
            metrics['min_rating'] = float(np.min(rating_array))
        else:
            metrics['avg_rating'] = 0.0
            metrics['max_rating'] = 0.0
            metrics['min_rating'] = 0.0
            
        if 'followers' in places_df.columns:
            metrics['total_followers'] = int(np.sum(followers_array))
            metrics['avg_followers'] = float(np.mean(followers_array))
            metrics['max_followers'] = int(np.max(followers_array))
        else:
            metrics['total_followers'] = 0
            metrics['avg_followers'] = 0.0
            metrics['max_followers'] = 0
            
        if 'country' in places_df.columns:
            metrics['unique_countries'] = places_df['country'].nunique()
            country_counts = places_df['country'].value_counts()
            metrics['most_common_country'] = country_counts.index[0] if not country_counts.empty else 'N/A'
        else:
            metrics['unique_countries'] = 0
            metrics['most_common_country'] = 'N/A'
            
        # Enhanced metrics for pincode analysis
        if 'pincode' in places_df.columns:
            valid_pincodes = places_df[places_df['pincode'].notna()]
            metrics['unique_pincodes'] = valid_pincodes['pincode'].nunique()
            pincode_counts = valid_pincodes['pincode'].value_counts()
            metrics['most_common_pincode'] = pincode_counts.index[0] if not pincode_counts.empty else 'N/A'
            metrics['pincode_coverage'] = (len(valid_pincodes) / len(places_df)) * 100
        else:
            metrics['unique_pincodes'] = 0
            metrics['most_common_pincode'] = 'N/A'
            metrics['pincode_coverage'] = 0.0
            
        # Enhanced metrics for address analysis
        if 'address' in places_df.columns:
            metrics['address_completeness'] = (places_df['address'].notna().sum() / len(places_df)) * 100
            # Count places with complete address information
            complete_addresses = places_df['address'].notna().sum()
            metrics['places_with_address'] = complete_addresses
        else:
            metrics['address_completeness'] = 0.0
            metrics['places_with_address'] = 0
        
        # Vectorized coordinate statistics using numpy
        metrics['avg_latitude'] = float(np.mean(lat_array))
        metrics['avg_longitude'] = float(np.mean(lon_array))
        
        # Vectorized most common type calculation
        type_counts = places_df['types'].value_counts()
        metrics['most_common_type'] = type_counts.index[0] if not type_counts.empty else 'N/A'
        
        # Vectorized coordinate spread calculation
        lat_range = float(np.max(lat_array) - np.min(lat_array))
        lon_range = float(np.max(lon_array) - np.min(lon_array))
        metrics['coordinate_spread'] = {
            'lat_range': lat_range,
            'lon_range': lon_range,
            'geographic_spread': float(np.sqrt(lat_range**2 + lon_range**2))
        }
        
        # Vectorized data quality metrics
        metrics['data_quality'] = MetricsCalculator._calculate_data_quality_vectorized(places_df)
        
        logger.debug("Basic metrics calculated", metrics_count=len(metrics))
        return metrics
    
    @staticmethod
    def _calculate_data_quality_vectorized(places_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data quality metrics using vectorized operations."""
        quality_metrics = {}
        
        # Vectorized completeness check
        total_fields = len(places_df.columns)
        null_counts = places_df.isnull().sum().sum()
        quality_metrics['completeness'] = ((total_fields * len(places_df) - null_counts) / 
                                         (total_fields * len(places_df)) * 100)
        
        # Vectorized coordinate validity using numpy
        lat_array = places_df['latitude'].to_numpy()
        lon_array = places_df['longitude'].to_numpy()
        
        valid_coords = int(np.sum(
            (lat_array >= -90) & (lat_array <= 90) & 
            (lon_array >= -180) & (lon_array <= 180)
        ))
        quality_metrics['coordinate_validity'] = float(valid_coords / len(places_df) * 100)
        
        # Vectorized duplicate detection
        duplicates = places_df.duplicated(subset=['name', 'address']).sum()
        quality_metrics['duplicate_count'] = duplicates
        quality_metrics['uniqueness'] = ((len(places_df) - duplicates) / len(places_df) * 100)
        
        return quality_metrics
    
    @staticmethod
    @handle_errors(show_user_message=False)
    def calculate_comprehensive_data_quality(places_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate comprehensive data quality metrics for all columns based on database schema.
        
        Args:
            places_df: DataFrame containing places data with all schema columns
            
        Returns:
            Dict containing comprehensive data quality metrics
        """
        logger.debug("Calculating comprehensive data quality metrics")
        
        if places_df.empty:
            return {'error': 'No data available for quality analysis'}
        
        quality_metrics = {}
        
        # Define expected columns based on database schema
        expected_columns = [
            'id', 'latitude', 'longitude', 'types', 'name', 
            'address', 'pincode', 'rating', 'followers', 'country', 
            'created_at', 'updated_at'
        ]
        
        # Column completeness analysis
        column_completeness = {}
        for col in expected_columns:
            if col in places_df.columns:
                non_null_count = places_df[col].notna().sum()
                completeness = (non_null_count / len(places_df)) * 100
                column_completeness[col] = {
                    'completeness_percentage': completeness,
                    'non_null_count': non_null_count,
                    'null_count': len(places_df) - non_null_count
                }
            else:
                column_completeness[col] = {
                    'completeness_percentage': 0.0,
                    'non_null_count': 0,
                    'null_count': len(places_df)
                }
        
        quality_metrics['column_completeness'] = column_completeness
        
        # Overall data quality score
        total_completeness = sum(
            col_data['completeness_percentage'] 
            for col_data in column_completeness.values()
        )
        quality_metrics['overall_quality_score'] = total_completeness / len(expected_columns)
        
        # Data type validation
        data_type_issues = {}
        if 'latitude' in places_df.columns:
            try:
                lat_issues = places_df['latitude'].apply(lambda x: not isinstance(x, (int, float)) and pd.notna(x)).sum()
                data_type_issues['latitude'] = lat_issues
            except Exception:
                data_type_issues['latitude'] = 0
            
        if 'longitude' in places_df.columns:
            try:
                lon_issues = places_df['longitude'].apply(lambda x: not isinstance(x, (int, float)) and pd.notna(x)).sum()
                data_type_issues['longitude'] = lon_issues
            except Exception:
                data_type_issues['longitude'] = 0
            
        if 'rating' in places_df.columns:
            try:
                rating_issues = places_df['rating'].apply(lambda x: not isinstance(x, (int, float)) and pd.notna(x)).sum()
                data_type_issues['rating'] = rating_issues
            except Exception:
                data_type_issues['rating'] = 0
            
        if 'followers' in places_df.columns:
            try:
                followers_issues = places_df['followers'].apply(lambda x: not isinstance(x, (int, float)) and pd.notna(x)).sum()
                data_type_issues['followers'] = followers_issues
            except Exception:
                data_type_issues['followers'] = 0
        
        quality_metrics['data_type_issues'] = data_type_issues
        
        # Coordinate validation
        if 'latitude' in places_df.columns and 'longitude' in places_df.columns:
            valid_coords = (
                (places_df['latitude'] >= -90) & (places_df['latitude'] <= 90) &
                (places_df['longitude'] >= -180) & (places_df['longitude'] <= 180)
            ).sum()
            quality_metrics['valid_coordinates'] = valid_coords
            quality_metrics['coordinate_validity_percentage'] = (valid_coords / len(places_df)) * 100
        
        # Duplicate detection
        duplicate_checks = {}
        if 'name' in places_df.columns and 'address' in places_df.columns:
            name_address_duplicates = places_df.duplicated(subset=['name', 'address']).sum()
            duplicate_checks['name_address_duplicates'] = name_address_duplicates
            
        if 'id' in places_df.columns:
            id_duplicates = places_df.duplicated(subset=['id']).sum()
            duplicate_checks['id_duplicates'] = id_duplicates
            
        quality_metrics['duplicate_analysis'] = duplicate_checks
        
        # Timestamp analysis
        if 'created_at' in places_df.columns:
            try:
                created_dates = pd.to_datetime(places_df['created_at'], utc=True, errors='coerce')
                valid_created_dates = created_dates.notna().sum()
                quality_metrics['valid_created_dates'] = valid_created_dates
                quality_metrics['created_date_validity'] = (valid_created_dates / len(places_df)) * 100
            except Exception as e:
                logger.warning("Error analyzing created_at dates", error=str(e))
                quality_metrics['valid_created_dates'] = 0
                quality_metrics['created_date_validity'] = 0.0
                
        if 'updated_at' in places_df.columns:
            try:
                updated_dates = pd.to_datetime(places_df['updated_at'], utc=True, errors='coerce')
                valid_updated_dates = updated_dates.notna().sum()
                quality_metrics['valid_updated_dates'] = valid_updated_dates
                quality_metrics['updated_date_validity'] = (valid_updated_dates / len(places_df)) * 100
            except Exception as e:
                logger.warning("Error analyzing updated_at dates", error=str(e))
                quality_metrics['valid_updated_dates'] = 0
                quality_metrics['updated_date_validity'] = 0.0
        
        return quality_metrics
    
    @staticmethod
    @handle_errors(show_user_message=False)
    def calculate_time_based_metrics(places_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate time-based analytics metrics using vectorized operations.
        
        Args:
            places_df: DataFrame containing places data with timestamp columns
            
        Returns:
            Dict containing time-based metrics
        """
        logger.debug("Calculating time-based metrics")
        
        if places_df.empty or 'created_at' not in places_df.columns:
            return {'error': 'No timestamp data available'}
        
        # Use copy to avoid modifying original dataframe
        df_copy = places_df.copy()
        
        # Vectorized datetime conversion - ensure consistent timezone
        try:
            df_copy['created_at'] = pd.to_datetime(df_copy['created_at'], utc=True, errors='coerce')
            # Remove any rows with invalid dates
            df_copy = df_copy.dropna(subset=['created_at'])
        except Exception as e:
            logger.warning("Error converting datetime column", error=str(e))
            return {'error': 'Invalid timestamp data format'}
        
        # Check if we have valid data after conversion
        if df_copy.empty:
            return {'error': 'No valid timestamp data available'}
        
        metrics = {}
        
        # Vectorized recent activity calculation - ensure consistent datetime types
        thirty_days_ago = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
        # Ensure both are timezone-aware for comparison
        recent_mask = df_copy['created_at'] >= thirty_days_ago
        metrics['recent_additions'] = int(np.sum(recent_mask))
        
        # Vectorized growth rate calculation
        if len(df_copy) > 1:
            date_range = (df_copy['created_at'].max() - df_copy['created_at'].min()).days
            metrics['daily_addition_rate'] = len(df_copy) / date_range if date_range > 0 else 0
        else:
            metrics['daily_addition_rate'] = 0
        
        # Vectorized peak activity calculation
        df_copy['hour'] = df_copy['created_at'].dt.hour
        df_copy['day_of_week'] = df_copy['created_at'].dt.day_name()
        
        # Use numpy for mode calculation
        hour_array = df_copy['hour'].to_numpy()
        day_array = df_copy['day_of_week'].to_numpy()
        
        # Calculate mode using numpy
        unique_hours, counts = np.unique(hour_array, return_counts=True)
        peak_hour_idx = np.argmax(counts)
        metrics['peak_hour'] = int(unique_hours[peak_hour_idx]) if len(unique_hours) > 0 else 0
        
        unique_days, day_counts = np.unique(day_array, return_counts=True)
        peak_day_idx = np.argmax(day_counts)
        metrics['peak_day'] = unique_days[peak_day_idx] if len(unique_days) > 0 else 'Unknown'
        
        return metrics


class ChartsGenerator:
    """Generator for various analytics charts with optimized data processing."""
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error generating charts")
    def create_places_by_type_chart(places_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a bar chart showing places by type using vectorized operations.
        
        Args:
            places_df: DataFrame containing places data
            
        Returns:
            Plotly figure or None if error
        """
        logger.debug("Creating places by type chart")
        
        if places_df.empty:
            return None
        
        # Vectorized type counting
        type_counts = places_df['types'].value_counts().head(10)  # Top 10 types
        
        # Use numpy arrays for faster plotting
        values = type_counts.values
        labels = type_counts.index.to_numpy()
        
        fig = px.bar(
            x=values,
            y=labels,
            orientation='h',
            title="📊 Places by Type (Top 10)",
            labels={'x': 'Number of Places', 'y': 'Place Type'},
            color=values,
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            height=analytics_config.chart_height,
            showlegend=False,
            xaxis_title="Number of Places",
            yaxis_title="Place Type",
            title_x=0.5
        )
        
        logger.debug("Places by type chart created", type_count=len(type_counts))
        return fig
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error generating map")
    def create_geographic_distribution_map(places_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a map showing geographic distribution of places using vectorized filtering.
        
        Args:
            places_df: DataFrame containing places data
            
        Returns:
            Plotly figure or None if error
        """
        logger.debug("Creating geographic distribution map")
        
        if places_df.empty:
            return None
        
        # Vectorized coordinate validation using numpy
        lat_array = places_df['latitude'].to_numpy()
        lon_array = places_df['longitude'].to_numpy()
        
        valid_mask = (
            (lat_array >= -90) & (lat_array <= 90) & 
            (lon_array >= -180) & (lon_array <= 180)
        )
        
        valid_coords = places_df[valid_mask]
        
        if valid_coords.empty:
            logger.warning("No valid coordinates found for map")
            return None
        
        fig = px.scatter_mapbox(
            valid_coords,
            lat='latitude',
            lon='longitude',
            hover_name='name',
            hover_data={
                'types': True,
                'address': True,
                'pincode': True,
                'latitude': ':.4f',
                'longitude': ':.4f'
            },
            color='types',
            title="🗺️ Geographic Distribution of Places",
            zoom=analytics_config.default_zoom,
            height=analytics_config.chart_height
        )
        
        fig.update_layout(
            mapbox_style=analytics_config.map_style,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            title_x=0.5
        )
        
        logger.debug("Geographic distribution map created", 
                    valid_coordinates=len(valid_coords))
        return fig
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error generating timeline chart")
    def create_addition_timeline_chart(places_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a timeline chart showing place additions over time using vectorized operations.
        
        Args:
            places_df: DataFrame containing places data
            
        Returns:
            Plotly figure or None if error
        """
        logger.debug("Creating addition timeline chart")
        
        if places_df.empty or 'created_at' not in places_df.columns:
            return None
        
        # Use copy to avoid modifying original dataframe
        temp_df = places_df.copy()
        
        # Vectorized datetime conversion - ensure consistent timezone
        try:
            temp_df['created_at'] = pd.to_datetime(temp_df['created_at'], utc=True, errors='coerce')
            # Remove any rows with invalid dates
            temp_df = temp_df.dropna(subset=['created_at'])
        except Exception as e:
            logger.warning("Error converting datetime column", error=str(e))
            return None
        
        # Check if we have valid data after conversion
        if temp_df.empty:
            return None
        
        # Vectorized date grouping
        daily_additions = temp_df.groupby(temp_df['created_at'].dt.date).size()
        
        # Use numpy arrays for plotting
        dates = np.array(list(daily_additions.index))
        counts = daily_additions.values
        
        fig = px.line(
            x=dates,
            y=counts,
            title="📈 Place Additions Over Time",
            labels={'x': 'Date', 'y': 'Number of Places Added'},
            markers=True
        )
        
        fig.update_layout(
            height=analytics_config.chart_height,
            xaxis_title="Date",
            yaxis_title="Places Added",
            title_x=0.5
        )
        
        logger.debug("Addition timeline chart created", 
                    data_points=len(daily_additions))
        return fig
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error generating heatmap")
    def create_coordinate_heatmap(places_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a heatmap of place coordinates using vectorized operations.
        
        Args:
            places_df: DataFrame containing places data
            
        Returns:
            Plotly figure or None if error
        """
        logger.debug("Creating coordinate heatmap")
        
        if places_df.empty or len(places_df) < 5:
            return None
        
        # Vectorized coordinate validation
        lat_array = places_df['latitude'].to_numpy()
        lon_array = places_df['longitude'].to_numpy()
        
        valid_mask = (
            (lat_array >= -90) & (lat_array <= 90) & 
            (lon_array >= -180) & (lon_array <= 180)
        )
        
        valid_coords = places_df[valid_mask]
        
        if len(valid_coords) < 5:
            return None
        
        fig = px.density_mapbox(
            valid_coords,
            lat='latitude',
            lon='longitude',
            radius=10,
            title="🔥 Place Density Heatmap",
            zoom=analytics_config.default_zoom,
            height=analytics_config.chart_height
        )
        
        fig.update_layout(
            mapbox_style=analytics_config.map_style,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            title_x=0.5
        )
        
        logger.debug("Coordinate heatmap created")
        return fig
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error generating pincode chart")
    def create_pincode_distribution_chart(places_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a chart showing distribution of places by pincode.
        
        Args:
            places_df: DataFrame containing places data
            
        Returns:
            Plotly figure or None if error
        """
        logger.debug("Creating pincode distribution chart")
        
        if places_df.empty or 'pincode' not in places_df.columns:
            return None
        
        # Filter out null pincodes
        valid_pincodes = places_df[places_df['pincode'].notna()]
        
        if valid_pincodes.empty:
            return None
        
        # Count places by pincode
        pincode_counts = valid_pincodes['pincode'].value_counts().head(15)  # Top 15 pincodes
        
        if pincode_counts.empty:
            return None
        
        fig = px.bar(
            x=pincode_counts.values,
            y=pincode_counts.index,
            orientation='h',
            title="📮 Places by Pincode (Top 15)",
            labels={'x': 'Number of Places', 'y': 'Pincode'},
            color=pincode_counts.values,
            color_continuous_scale='plasma'
        )
        
        fig.update_layout(
            height=analytics_config.chart_height,
            xaxis_title="Number of Places",
            yaxis_title="Pincode",
            title_x=0.5
        )
        
        logger.debug("Pincode distribution chart created")
        return fig
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error generating data quality chart")
    def create_data_quality_chart(places_df: pd.DataFrame) -> Optional[go.Figure]:
        """
        Create a chart showing data quality metrics for all columns.
        
        Args:
            places_df: DataFrame containing places data
            
        Returns:
            Plotly figure or None if error
        """
        logger.debug("Creating data quality chart")
        
        if places_df.empty:
            return None
        
        # Calculate data quality metrics
        quality_metrics = MetricsCalculator.calculate_comprehensive_data_quality(places_df)
        
        if 'error' in quality_metrics:
            return None
        
        # Extract column completeness data
        column_completeness = quality_metrics.get('column_completeness', {})
        
        if not column_completeness:
            return None
        
        # Prepare data for visualization
        columns = list(column_completeness.keys())
        completeness_values = [col_data['completeness_percentage'] for col_data in column_completeness.values()]
        
        fig = px.bar(
            x=columns,
            y=completeness_values,
            title="📊 Data Completeness by Column",
            labels={'x': 'Column', 'y': 'Completeness (%)'},
            color=completeness_values,
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(
            height=analytics_config.chart_height,
            xaxis_title="Column",
            yaxis_title="Completeness (%)",
            title_x=0.5,
            xaxis={'tickangle': 45}
        )
        
        # Add a horizontal line at 100% for reference
        fig.add_hline(y=100, line_dash="dash", line_color="green", 
                     annotation_text="100% Complete")
        
        logger.debug("Data quality chart created")
        return fig


class DashboardRenderer:
    """Main dashboard rendering class with optimized data processing."""
    
    @staticmethod
    @handle_errors(show_user_message=True, user_message="Error loading analytics dashboard")
    def render_analytics_dashboard(places_df: pd.DataFrame) -> None:
        """
        Render the complete analytics dashboard with optimized calculations.
        
        Args:
            places_df: DataFrame containing all places data
        """
        logger.debug("Rendering analytics dashboard", 
                    records_count=len(places_df))
        
        st.header("📊 Analytics Dashboard")
        
        if places_df.empty:
            st.info("📭 No data available for analytics. Add some places first!")
            return
        
        # Pre-compute all metrics in parallel using vectorized operations
        metrics = safe_execute(
            lambda: MetricsCalculator.calculate_basic_metrics(places_df),
            "calculate_basic_metrics",
            default_return={}
        )
        
        time_metrics = safe_execute(
            lambda: MetricsCalculator.calculate_time_based_metrics(places_df),
            "calculate_time_metrics",
            default_return={}
        )
        
        # Ensure metrics are not None (defensive programming)
        if metrics is None:
            metrics = {}
        if time_metrics is None:
            time_metrics = {}
        
        # Render metrics cards
        DashboardRenderer._render_metrics_cards(metrics, time_metrics)
        
        # Render charts section
        DashboardRenderer._render_charts_section(places_df)
        
        # Render data quality section
        data_quality = metrics.get('data_quality', {}) if isinstance(metrics, dict) else {}
        DashboardRenderer._render_data_quality_section(data_quality)
        
        # Render recent activity section
        DashboardRenderer._render_recent_activity_section(places_df)
        
        logger.debug("Analytics dashboard rendered successfully")
    
    @staticmethod
    def _render_metrics_cards(metrics: Dict[str, Any], time_metrics: Dict[str, Any]) -> None:
        """Render key metrics cards."""
        st.markdown("### 📈 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Places", 
                metrics.get('total_places', 0),
                delta=time_metrics.get('recent_additions', 0),
                help="Total number of places in the database"
            )
        
        with col2:
            st.metric(
                "Unique Types", 
                metrics.get('unique_types', 0),
                help="Number of different place types"
            )
        
        with col3:
            avg_lat = metrics.get('avg_latitude', 0)
            st.metric(
                "Avg Latitude", 
                f"{avg_lat:.4f}" if avg_lat else "0.0000",
                help="Average latitude of all places"
            )
        
        with col4:
            avg_lon = metrics.get('avg_longitude', 0)
            st.metric(
                "Avg Longitude", 
                f"{avg_lon:.4f}" if avg_lon else "0.0000",
                help="Average longitude of all places"
            )
        
        # Additional metrics row
        if time_metrics and 'daily_addition_rate' in time_metrics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Daily Addition Rate",
                    f"{time_metrics.get('daily_addition_rate', 0):.2f}",
                    help="Average places added per day"
                )
            
            with col2:
                st.metric(
                    "Most Common Type",
                    metrics.get('most_common_type', 'N/A'),
                    help="Most frequently occurring place type"
                )
            
            with col3:
                spread = metrics.get('coordinate_spread', {}).get('geographic_spread', 0)
                st.metric(
                    "Geographic Spread",
                    f"{spread:.4f}°" if spread else "0.0000°",
                    help="Geographic distribution span"
                )
            
            with col4:
                peak_hour = time_metrics.get('peak_hour', 0)
                st.metric(
                    "Peak Hour",
                    f"{peak_hour:02d}:00",
                    help="Hour with most place additions"
                )
        
        # Enhanced metrics row based on schema columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Unique Pincodes",
                metrics.get('unique_pincodes', 0),
                help="Number of unique pincodes covered"
            )
        
        with col2:
            pincode_coverage = metrics.get('pincode_coverage', 0)
            st.metric(
                "Pincode Coverage",
                f"{pincode_coverage:.1f}%",
                help="Percentage of places with pincode data"
            )
        
        with col3:
            address_completeness = metrics.get('address_completeness', 0)
            st.metric(
                "Address Completeness",
                f"{address_completeness:.1f}%",
                help="Percentage of places with complete address"
            )
        
        with col4:
            st.metric(
                "Unique Countries",
                metrics.get('unique_countries', 0),
                help="Number of unique countries represented"
            )
    
    @staticmethod
    def _render_charts_section(places_df: pd.DataFrame) -> None:
        """Render charts section with optimized chart generation."""
        st.markdown("### 📊 Visual Analytics")
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Places by type chart
            type_chart = safe_execute(
                lambda: ChartsGenerator.create_places_by_type_chart(places_df),
                "create_type_chart"
            )
            if type_chart:
                st.plotly_chart(type_chart, width='stretch')
            else:
                st.info("Unable to generate places by type chart")
        
        with col2:
            # Geographic distribution map
            geo_map = safe_execute(
                lambda: ChartsGenerator.create_geographic_distribution_map(places_df),
                "create_geo_map"
            )
            if geo_map:
                st.plotly_chart(geo_map, width='stretch')
            else:
                st.info("Unable to generate geographic map")
        
        # Timeline chart (full width)
        if 'created_at' in places_df.columns:
            timeline_chart = safe_execute(
                lambda: ChartsGenerator.create_addition_timeline_chart(places_df),
                "create_timeline_chart"
            )
            if timeline_chart:
                st.plotly_chart(timeline_chart, width='stretch')
        
        # Heatmap (full width)
        heatmap = safe_execute(
            lambda: ChartsGenerator.create_coordinate_heatmap(places_df),
            "create_heatmap"
        )
        if heatmap:
            st.plotly_chart(heatmap, width='stretch')
        
        # New charts based on schema columns
        col1, col2 = st.columns(2)
        
        with col1:
            # Pincode distribution chart
            pincode_chart = safe_execute(
                lambda: ChartsGenerator.create_pincode_distribution_chart(places_df),
                "create_pincode_chart"
            )
            if pincode_chart:
                st.plotly_chart(pincode_chart, width='stretch')
            else:
                st.info("Unable to generate pincode distribution chart")
        
        with col2:
            # Data quality chart
            quality_chart = safe_execute(
                lambda: ChartsGenerator.create_data_quality_chart(places_df),
                "create_quality_chart"
            )
            if quality_chart:
                st.plotly_chart(quality_chart, width='stretch')
            else:
                st.info("Unable to generate data quality chart")
    
    @staticmethod
    def _render_data_quality_section(data_quality: Dict[str, Any]) -> None:
        """Render data quality metrics section."""
        if not data_quality:
            return
        
        st.markdown("### 🔍 Data Quality Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            completeness = data_quality.get('completeness', 0)
            st.metric(
                "Data Completeness",
                f"{completeness:.1f}%",
                help="Percentage of fields that are filled"
            )
        
        with col2:
            coord_validity = data_quality.get('coordinate_validity', 0)
            st.metric(
                "Coordinate Validity",
                f"{coord_validity:.1f}%",
                help="Percentage of valid coordinates"
            )
        
        with col3:
            uniqueness = data_quality.get('uniqueness', 0)
            st.metric(
                "Data Uniqueness",
                f"{uniqueness:.1f}%",
                help="Percentage of unique records"
            )
        
        # Show duplicates warning if any
        duplicate_count = data_quality.get('duplicate_count', 0)
        if duplicate_count > 0:
            st.warning(f"⚠️ Found {duplicate_count} potential duplicate records")
    
    @staticmethod
    def _render_recent_activity_section(places_df: pd.DataFrame) -> None:
        """Render recent activity section with optimized sorting."""
        st.markdown("### 🕒 Recent Activity")
        
        if 'created_at' not in places_df.columns:
            st.info("No timestamp data available for recent activity")
            return
        
        # Vectorized sorting and selection
        recent_places = places_df.sort_values('created_at', ascending=False).head(
            analytics_config.recent_activity_limit
        )
        
        if recent_places.empty:
            st.info("No recent activity to display")
            return
        
        # Display recent places in a nice format
        for _, place in recent_places.iterrows():
            with st.expander(
                f"📍 {place['name']} ({place['types']}) - {place['created_at']}", 
                expanded=False
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Address:** {place['address']}")
                    st.write(f"**Type:** {place['types']}")
                
                with col2:
                    st.write(f"**Coordinates:** {place['latitude']:.4f}, {place['longitude']:.4f}")
                    st.write(f"**Pincode:** {place['pincode']}")


# Export dashboard components
__all__ = [
    'MetricsCalculator',
    'ChartsGenerator', 
    'DashboardRenderer'
]
