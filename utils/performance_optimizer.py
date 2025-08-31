"""
Performance optimization utilities for the Places Management System.

This module provides performance optimization functions using numpy and pandas
vectorization for faster data processing and response times.
"""

import numpy as np
import pandas as pd
import time
import gc
from typing import Dict, List, Any, Optional, Tuple, Union
from functools import wraps
import psutil
import os

# Import configuration
try:
    from config.settings import performance_config, get_optimized_dtypes, get_performance_settings
    from utils.logger import get_logger
except ImportError:
    # Fallback configuration
    class MockPerformanceConfig:
        use_numpy_operations = True
        use_pandas_vectorization = True
        optimize_data_types = True
        enable_dataframe_cache = True
        cache_timeout_seconds = 300
        batch_database_operations = True
        lazy_loading_enabled = True
        virtual_scrolling_threshold = 1000
        debounce_search_ms = 300
    
    performance_config = MockPerformanceConfig()
    
    def get_optimized_dtypes():
        return {
            'id': 'int32',
            'latitude': 'float64',
            'longitude': 'float64',
            'types': 'string',
            'name': 'string',
            'address': 'string',
            'pincode': 'string',
            'created_at': 'datetime64[ns]',
            'updated_at': 'datetime64[ns]'
        }
    
    def get_performance_settings():
        return {
            'use_numpy': True,
            'use_vectorization': True,
            'optimize_dtypes': True,
            'enable_caching': True,
            'cache_timeout': 300,
            'batch_operations': True,
            'lazy_loading': True,
            'virtual_scrolling': 1000,
            'debounce_search': 300
        }
    
    class MockLogger:
        def debug(self, msg, **kwargs): pass
        def info(self, msg, **kwargs): pass
        def warning(self, msg, **kwargs): pass
        def error(self, msg, **kwargs): pass
    
    def get_logger(_name):
        return MockLogger()

logger = get_logger(__name__)


class DataFrameOptimizer:
    """Optimizes pandas DataFrames for better performance."""
    
    @staticmethod
    def optimize_dataframe(df: pd.DataFrame, dtypes: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Optimize DataFrame by converting data types and reducing memory usage.
        
        Args:
            df: DataFrame to optimize
            dtypes: Dictionary of column names to optimized data types
            
        Returns:
            pd.DataFrame: Optimized DataFrame
        """
        if df.empty:
            return df
        
        if dtypes is None:
            dtypes = get_optimized_dtypes()
        
        optimized_df = df.copy()
        
        # Apply optimized data types
        for col, dtype in dtypes.items():
            if col in optimized_df.columns:
                try:
                    if dtype == 'int32':
                        optimized_df[col] = pd.to_numeric(optimized_df[col], errors='coerce').astype('Int32')
                    elif dtype == 'float64':
                        optimized_df[col] = pd.to_numeric(optimized_df[col], errors='coerce').astype(np.float64)
                    elif dtype == 'string':
                        optimized_df[col] = optimized_df[col].astype('string')
                    elif dtype == 'datetime64[ns]':
                        optimized_df[col] = pd.to_datetime(optimized_df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Failed to optimize column {col}: {e}")
        
        # Reduce memory usage
        if performance_config.optimize_dataframe_memory:
            optimized_df = DataFrameOptimizer._reduce_memory_usage(optimized_df)
        
        logger.debug("DataFrame optimized", 
                    original_memory=df.memory_usage(deep=True).sum(),
                    optimized_memory=optimized_df.memory_usage(deep=True).sum())
        
        return optimized_df
    
    @staticmethod
    def _reduce_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
        """Reduce memory usage of DataFrame."""
        start_mem = df.memory_usage(deep=True).sum() / 1024**2
        
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()
                
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)
                else:
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)
            else:
                df[col] = df[col].astype('category')
        
        end_mem = df.memory_usage(deep=True).sum() / 1024**2
        logger.debug(f"Memory usage reduced from {start_mem:.2f} MB to {end_mem:.2f} MB")
        
        return df


class VectorizedOperations:
    """Provides vectorized operations for better performance."""
    
    @staticmethod
    def vectorized_coordinate_validation(latitudes: np.ndarray, longitudes: np.ndarray) -> np.ndarray:
        """
        Vectorized coordinate validation using numpy.
        
        Args:
            latitudes: Array of latitude values
            longitudes: Array of longitude values
            
        Returns:
            np.ndarray: Boolean array indicating valid coordinates
        """
        return (
            (latitudes >= -90) & (latitudes <= 90) & 
            (longitudes >= -180) & (longitudes <= 180)
        )
    
    @staticmethod
    def vectorized_string_search(text_array: np.ndarray, search_term: str) -> np.ndarray:
        """
        Vectorized string search using numpy.
        
        Args:
            text_array: Array of text values
            search_term: Term to search for
            
        Returns:
            np.ndarray: Boolean array indicating matches
        """
        search_term_lower = search_term.lower()
        return np.char.find(np.char.lower(text_array.astype(str)), search_term_lower) >= 0
    
    @staticmethod
    def vectorized_coordinate_formatting(latitudes: np.ndarray, longitudes: np.ndarray) -> np.ndarray:
        """
        Vectorized coordinate formatting using numpy.
        
        Args:
            latitudes: Array of latitude values
            longitudes: Array of longitude values
            
        Returns:
            np.ndarray: Array of formatted coordinate strings
        """
        lat_str = np.char.add(latitudes.astype(str), ', ')
        return np.char.add(lat_str, longitudes.astype(str))
    
    @staticmethod
    def vectorized_type_filtering(types_array: np.ndarray, target_type: str) -> np.ndarray:
        """
        Vectorized type filtering using numpy.
        
        Args:
            types_array: Array of type values
            target_type: Type to filter for
            
        Returns:
            np.ndarray: Boolean array indicating matches
        """
        return types_array == target_type


class PerformanceMonitor:
    """Monitors and reports performance metrics."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation_name: str) -> None:
        """Start timing an operation."""
        self.start_times[operation_name] = time.time()
    
    def end_timer(self, operation_name: str) -> float:
        """End timing an operation and return duration."""
        if operation_name not in self.start_times:
            return 0.0
        
        duration = time.time() - self.start_times[operation_name]
        self.metrics[operation_name] = duration
        del self.start_times[operation_name]
        
        logger.debug(f"Operation '{operation_name}' completed in {duration:.4f}s")
        return duration
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        memory_usage = self.get_memory_usage()
        
        return {
            'metrics': self.metrics.copy(),
            'memory_usage': memory_usage,
            'total_operations': len(self.metrics)
        }
    
    def clear_metrics(self) -> None:
        """Clear all performance metrics."""
        self.metrics.clear()
        self.start_times.clear()


class CacheManager:
    """Manages caching for improved performance."""
    
    def __init__(self, max_size_mb: int = 100):
        """Initialize cache manager."""
        self.cache = {}
        self.max_size_mb = max_size_mb
        self.access_times = {}
    
    def get(self, key: str) -> Any:
        """Get item from cache."""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        # Check cache size and evict if necessary
        current_size = self._get_cache_size_mb()
        if current_size > self.max_size_mb:
            self._evict_oldest()
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def _get_cache_size_mb(self) -> float:
        """Get current cache size in MB."""
        total_size = 0
        for key, value in self.cache.items():
            if hasattr(value, 'memory_usage'):
                total_size += value.memory_usage(deep=True).sum()
            else:
                total_size += len(str(value))
        return total_size / 1024 / 1024
    
    def _evict_oldest(self) -> None:
        """Evict oldest items from cache."""
        if not self.access_times:
            return
        
        # Find oldest item
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
        self.access_times.clear()


def performance_decorator(operation_name: str):
    """Decorator for performance monitoring."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            monitor.start_timer(operation_name)
            
            try:
                result = func(*args, **kwargs)
                monitor.end_timer(operation_name)
                return result
            except Exception as e:
                monitor.end_timer(operation_name)
                raise e
        
        return wrapper
    return decorator


def optimize_dataframe_batch(dataframes: List[pd.DataFrame]) -> List[pd.DataFrame]:
    """
    Optimize multiple DataFrames in batch.
    
    Args:
        dataframes: List of DataFrames to optimize
        
    Returns:
        List[pd.DataFrame]: List of optimized DataFrames
    """
    optimized_dfs = []
    
    for i, df in enumerate(dataframes):
        logger.debug(f"Optimizing DataFrame {i+1}/{len(dataframes)}")
        optimized_df = DataFrameOptimizer.optimize_dataframe(df)
        optimized_dfs.append(optimized_df)
    
    return optimized_dfs


def vectorized_search_filter(df: pd.DataFrame, search_term: str, columns: List[str]) -> pd.DataFrame:
    """
    Apply vectorized search filter to DataFrame.
    
    Args:
        df: DataFrame to filter
        search_term: Search term
        columns: Columns to search in
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if not search_term or not columns:
        return df
    
    # Convert search term to lowercase
    search_term = search_term.lower()
    
    # Create mask for each column
    mask = pd.Series([False] * len(df), index=df.index)
    
    for col in columns:
        if col in df.columns:
            # Use vectorized string search
            col_mask = VectorizedOperations.vectorized_string_search(
                df[col].to_numpy(), 
                search_term
            )
            mask = mask | col_mask
    
    return df[mask]


def optimize_coordinate_operations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize coordinate-related operations in DataFrame.
    
    Args:
        df: DataFrame with coordinate columns
        
    Returns:
        pd.DataFrame: DataFrame with optimized coordinate operations
    """
    if 'latitude' in df.columns and 'longitude' in df.columns:
        # Convert to numpy arrays for faster operations
        lat_array = df['latitude'].to_numpy()
        lon_array = df['longitude'].to_numpy()
        
        # Validate coordinates
        valid_coords = VectorizedOperations.vectorized_coordinate_validation(lat_array, lon_array)
        
        # Filter out invalid coordinates
        df = df[valid_coords]
        
        # Add formatted coordinates column
        df['coordinates_formatted'] = VectorizedOperations.vectorized_coordinate_formatting(
            lat_array[valid_coords], 
            lon_array[valid_coords]
        )
    
    return df


# Global instances
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager(max_size_mb=performance_config.max_cache_size_mb)


# Export all performance utilities
__all__ = [
    'DataFrameOptimizer',
    'VectorizedOperations',
    'PerformanceMonitor',
    'CacheManager',
    'performance_decorator',
    'optimize_dataframe_batch',
    'vectorized_search_filter',
    'optimize_coordinate_operations',
    'performance_monitor',
    'cache_manager'
]
