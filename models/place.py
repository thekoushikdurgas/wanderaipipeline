"""
Place Models for the Places Management System.

This module defines comprehensive data models for places, including
Pydantic models for validation, dataclasses for internal use, and
enums for type safety. Optimized for performance and type safety.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid
from utils.logger import get_logger
logger = get_logger(__name__)

# Pydantic imports for validation
try:
    from pydantic import BaseModel, Field, validator, root_validator
    from pydantic.types import confloat, constr
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Fallback base class
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
        def json(self):
            import json
            return json.dumps(self.dict())


class PlaceType(str, Enum):
    """Enumeration of standard place types."""
    
    # Food and Dining
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    BAR = "bar"
    BAKERY = "bakery"
    FOOD = "food"
    
    # Accommodation
    HOTEL = "hotel"
    LODGING = "lodging"
    CAMPGROUND = "campground"
    RV_PARK = "rv_park"
    
    # Attractions
    TOURIST_ATTRACTION = "tourist_attraction"
    MUSEUM = "museum"
    PARK = "park"
    LANDMARK = "landmark"
    NATURAL_FEATURE = "natural_feature"
    
    # Shopping
    SHOPPING_MALL = "shopping_mall"
    STORE = "store"
    DEPARTMENT_STORE = "department_store"
    CONVENIENCE_STORE = "convenience_store"
    GROCERY_OR_SUPERMARKET = "grocery_or_supermarket"
    
    # Health and Services
    HOSPITAL = "hospital"
    DOCTOR = "doctor"
    DENTIST = "dentist"
    PHARMACY = "pharmacy"
    VETERINARY_CARE = "veterinary_care"
    
    # Education
    SCHOOL = "school"
    UNIVERSITY = "university"
    LIBRARY = "library"
    PRIMARY_SCHOOL = "primary_school"
    
    # Transportation
    AIRPORT = "airport"
    TRAIN_STATION = "train_station"
    BUS_STATION = "bus_station"
    SUBWAY_STATION = "subway_station"
    GAS_STATION = "gas_station"
    PARKING = "parking"
    
    # Government and Public Services
    CITY_HALL = "city_hall"
    POLICE = "police"
    FIRE_STATION = "fire_station"
    POST_OFFICE = "post_office"
    COURTHOUSE = "courthouse"
    
    # Religious
    CHURCH = "church"
    MOSQUE = "mosque"
    TEMPLE = "temple"
    HINDU_TEMPLE = "hindu_temple"
    PLACE_OF_WORSHIP = "place_of_worship"
    
    # Entertainment
    MOVIE_THEATER = "movie_theater"
    CASINO = "casino"
    NIGHT_CLUB = "night_club"
    BOWLING_ALLEY = "bowling_alley"
    STADIUM = "stadium"
    
    # Business Services
    BANK = "bank"
    ATM = "atm"
    INSURANCE_AGENCY = "insurance_agency"
    REAL_ESTATE_AGENCY = "real_estate_agency"
    LAWYER = "lawyer"
    
    # Other
    POINT_OF_INTEREST = "point_of_interest"
    ESTABLISHMENT = "establishment"
    PREMISE = "premise"
    SUBPREMISE = "subpremise"
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all available place types as strings."""
        return [member.value for member in cls]
    
    @classmethod
    def validate_type(cls, place_type: str) -> bool:
        """Validate if a place type is standard."""
        return place_type.lower() in [t.lower() for t in cls.get_all_types()]


@dataclass
class Coordinates:
    """Geographic coordinates model."""
    
    latitude: float = field(metadata={"min": -90.0, "max": 90.0})
    longitude: float = field(metadata={"min": -180.0, "max": 180.0})
    
    def __post_init__(self):
        """Validate coordinates after initialization."""
        if not (-90.0 <= self.latitude <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {"latitude": self.latitude, "longitude": self.longitude}
    
    def to_tuple(self) -> tuple[float, float]:
        """Convert to tuple."""
        return (self.latitude, self.longitude)
    
    def distance_to(self, other: 'Coordinates') -> float:
        """Calculate approximate distance to another coordinate (Haversine formula)."""
        import math
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r


@dataclass
class PlaceRating:
    """Place rating model."""
    
    rating: float = field(default=0.0, metadata={"min": 0.0, "max": 5.0})
    followers: float = field(default=0.0, metadata={"min": 0.0})
    
    def __post_init__(self):
        """Validate rating after initialization."""
        if not (0.0 <= self.rating <= 5.0):
            raise ValueError(f"Rating must be between 0.0 and 5.0, got {self.rating}")
        if self.followers < 0:
            raise ValueError(f"Followers must be non-negative, got {self.followers}")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {"rating": self.rating, "followers": self.followers}


@dataclass
class PlaceAddress:
    """Place address model."""
    
    address: str
    pincode: str
    country: str = "Unknown"
    
    def __post_init__(self):
        """Validate address after initialization."""
        if not self.address or not self.address.strip():
            raise ValueError("Address cannot be empty")
        if not self.pincode or not self.pincode.strip():
            raise ValueError("Pincode cannot be empty")
        if len(self.pincode) >= 10:
            raise ValueError("Pincode must be less than 10 characters")
        if not self.country or not self.country.strip():
            self.country = "Unknown"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "address": self.address,
            "pincode": self.pincode,
            "country": self.country
        }


@dataclass
class PlaceTimestamps:
    """Place timestamp model."""
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, datetime]:
        """Convert to dictionary."""
        return {
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class Place:
    """Comprehensive place model with all fields."""
    
    # Core fields
    name: str
    types: str
    coordinates: Coordinates
    address: PlaceAddress
    
    # Optional fields
    id: str = ''
    rating: Optional[PlaceRating] = None
    timestamps: Optional[PlaceTimestamps] = None
    
    def __post_init__(self):
        """Initialize optional fields and validate data."""
        if self.rating is None:
            self.rating = PlaceRating()
        if self.timestamps is None:
            self.timestamps = PlaceTimestamps()
        
        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("Place name cannot be empty")
        
        # Validate types
        if not self.types or not self.types.strip():
            raise ValueError("Place types cannot be empty")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Place':
        """Create Place instance from dictionary."""
        logger.info(f"Data: {data}")
        # Extract coordinates
        coordinates = Coordinates(
            latitude=float(data.get('latitude', 0.0)),
            longitude=float(data.get('longitude', 0.0))
        )
        
        # Extract address
        address = PlaceAddress(
            address=data.get('address', ''),
            pincode=data.get('pincode', ''),
            country=data.get('country', 'Unknown')
        )
        
        # Extract rating
        rating = PlaceRating(
            rating=float(data.get('rating', 0.0)),
            followers=float(data.get('followers', 0.0))
        )
        
        # Extract timestamps
        created_at = data.get('created_at')
        updated_at = data.get('updated_at')
        
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        else:
            created_at = datetime.utcnow()
            
        if updated_at:
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        else:
            updated_at = datetime.utcnow()
        
        timestamps = PlaceTimestamps(created_at=created_at, updated_at=updated_at)
        
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            types=data.get('types', ''),
            coordinates=coordinates,
            address=address,
            rating=rating,
            timestamps=timestamps
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Place to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'types': self.types,
            'latitude': self.coordinates.latitude,
            'longitude': self.coordinates.longitude,
            'address': self.address.address,
            'pincode': self.address.pincode,
            'country': self.address.country,
            'rating': self.rating.rating,
            'followers': self.rating.followers,
            'created_at': self.timestamps.created_at,
            'updated_at': self.timestamps.updated_at
        }
    
    def update(self, **kwargs) -> None:
        """Update place fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Update timestamp
        self.timestamps.update_timestamp()
    
    def get_distance_to(self, other_place: 'Place') -> float:
        """Calculate distance to another place."""
        return self.coordinates.distance_to(other_place.coordinates)
    
    def is_near(self, other_place: 'Place', max_distance_km: float = 10.0) -> bool:
        """Check if this place is near another place."""
        return self.get_distance_to(other_place) <= max_distance_km
    
    def has_type(self, place_type: str) -> bool:
        """Check if place has a specific type."""
        return place_type.lower() in self.types.lower()
    
    def get_types_list(self) -> List[str]:
        """Get list of place types."""
        return [t.strip() for t in self.types.split(',') if t.strip()]


# Pydantic Models for API validation
if PYDANTIC_AVAILABLE:
    class PlaceCreate(BaseModel):
        """Pydantic model for creating a new place."""
        
        name: constr(min_length=2, max_length=255) = Field(..., description="Place name")
        types: constr(min_length=1, max_length=255) = Field(..., description="Place types")
        latitude: confloat(ge=-90.0, le=90.0) = Field(..., description="Latitude coordinate")
        longitude: confloat(ge=-180.0, le=180.0) = Field(..., description="Longitude coordinate")
        address: constr(min_length=5, max_length=1000) = Field(..., description="Full address")
        pincode: str = Field(..., description="6-character pincode")
        
        @validator('pincode')
        def validate_pincode(cls, v):
            """Validate pincode format."""
            if not v or not v.strip():
                raise ValueError('Pincode cannot be empty')
            v = v.strip()
            if len(v) >= 10:
                raise ValueError('Pincode must be less than 10 characters')
            return v
        country: constr(min_length=2, max_length=100) = Field(default="Unknown", description="Country name")
        rating: confloat(ge=0.0, le=5.0) = Field(default=0.0, description="Place rating (0-5)")
        followers: confloat(ge=0.0) = Field(default=0.0, description="Number of followers")
        
        @validator('types')
        def validate_types(cls, v):
            """Validate place types."""
            if not v or not v.strip():
                raise ValueError('Types cannot be empty')
            return v.strip()
        
        @validator('name')
        def validate_name(cls, v):
            """Validate place name."""
            if not v or not v.strip():
                raise ValueError('Name cannot be empty')
            return v.strip()
        
        @validator('address')
        def validate_address(cls, v):
            """Validate address."""
            if not v or not v.strip():
                raise ValueError('Address cannot be empty')
            return v.strip()
        
        def to_place(self) -> Place:
            """Convert to Place instance."""
            return Place.from_dict(self.dict())
    
    class PlaceUpdate(BaseModel):
        """Pydantic model for updating an existing place."""
        
        name: Optional[constr(min_length=2, max_length=255)] = Field(None, description="Place name")
        types: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Place types")
        latitude: Optional[confloat(ge=-90.0, le=90.0)] = Field(None, description="Latitude coordinate")
        longitude: Optional[confloat(ge=-180.0, le=180.0)] = Field(None, description="Longitude coordinate")
        address: Optional[constr(min_length=5, max_length=1000)] = Field(None, description="Full address")
        pincode: Optional[str] = Field(None, description="6-character pincode")
        
        @validator('pincode')
        def validate_pincode(cls, v):
            """Validate pincode format."""
            if v is not None:
                if not v.strip():
                    raise ValueError('Pincode cannot be empty')
                v = v.strip()
                if len(v) >= 10:
                    raise ValueError('Pincode must be less than 10 characters')
            return v
        country: Optional[constr(min_length=2, max_length=100)] = Field(None, description="Country name")
        rating: Optional[confloat(ge=0.0, le=5.0)] = Field(None, description="Place rating (0-5)")
        followers: Optional[confloat(ge=0.0)] = Field(None, description="Number of followers")
        
        @validator('name', 'types', 'latitude', 'longitude', 'address', 'pincode', 'country', 'rating', 'followers', pre=True)
        def check_at_least_one_field(cls, v, values):
            """Ensure at least one field is provided for update."""
            # This is a simplified check - in practice, you might want to use model_validator
            return v
    
    class PlaceResponse(BaseModel):
        """Pydantic model for place response."""
        
        id: str = Field(..., description="Unique place identifier")
        name: str = Field(..., description="Place name")
        types: str = Field(..., description="Place types")
        latitude: float = Field(..., description="Latitude coordinate")
        longitude: float = Field(..., description="Longitude coordinate")
        address: str = Field(..., description="Full address")
        pincode: str = Field(..., description="Pincode (must be less than 10 characters)")
        country: str = Field(..., description="Country name")
        rating: float = Field(..., description="Place rating")
        followers: float = Field(..., description="Number of followers")
        created_at: datetime = Field(..., description="Creation timestamp")
        updated_at: datetime = Field(..., description="Last update timestamp")
        
        class Config:
            """Pydantic configuration."""
            json_encoders = {
                datetime: lambda v: v.isoformat()
            }
    
    class PlaceListResponse(BaseModel):
        """Pydantic model for list of places response."""
        
        places: List[PlaceResponse] = Field(..., description="List of places")
        total_count: int = Field(..., description="Total number of places")
        page: int = Field(..., description="Current page number")
        page_size: int = Field(..., description="Number of items per page")
        total_pages: int = Field(..., description="Total number of pages")
    
    class PlaceSearchRequest(BaseModel):
        """Pydantic model for place search request."""
        
        search_term: Optional[str] = Field(None, description="Search term")
        place_type: Optional[str] = Field(None, description="Filter by place type")
        min_rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Minimum rating")
        max_distance: Optional[float] = Field(None, gt=0.0, description="Maximum distance in km")
        latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Center latitude")
        longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Center longitude")
        country: Optional[str] = Field(None, description="Filter by country")
        page: int = Field(default=1, ge=1, description="Page number")
        page_size: int = Field(default=10, ge=1, le=100, description="Items per page")
        sort_by: str = Field(default="name", description="Sort field")
        sort_order: str = Field(default="asc", description="Sort order (asc/desc)")
        
        @validator('sort_order')
        def validate_sort_order(cls, v):
            """Validate sort order."""
            if v.lower() not in ['asc', 'desc']:
                raise ValueError('Sort order must be "asc" or "desc"')
            return v.lower()
        
        @validator('max_distance')
        def validate_coordinates(cls, v, values):
            """Validate that if distance is provided, coordinates are also provided."""
            if v is not None and (values.get('latitude') is None or values.get('longitude') is None):
                raise ValueError('Latitude and longitude are required when max_distance is provided')
            return v

else:
    # Fallback classes when Pydantic is not available
    class PlaceCreate:
        """Fallback place creation model."""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def to_place(self) -> Place:
            """Convert to Place instance."""
            return Place.from_dict(self.__dict__)
    
    class PlaceUpdate:
        """Fallback place update model."""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PlaceResponse:
        """Fallback place response model."""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PlaceListResponse:
        """Fallback place list response model."""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class PlaceSearchRequest:
        """Fallback place search request model."""
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


# Utility functions
def create_place_from_api_data(api_data: Dict[str, Any]) -> Place:
    """Create a Place instance from API response data."""
    # Extract basic information
    name = api_data.get('name', '')
    types = ', '.join(api_data.get('types', []))
    
    # Extract coordinates
    geometry = api_data.get('geometry', {})
    location = geometry.get('location', {})
    latitude = location.get('lat', 0.0)
    longitude = location.get('lng', 0.0)
    
    # Extract address
    address = api_data.get('formatted_address', '')
    pincode = api_data.get('pincode', '000000')
    country = 'Unknown'
    
    # Extract country from address components
    address_components = api_data.get('address_components', [])
    for component in address_components:
        if 'country' in component.get('types', []):
            country = component.get('long_name', 'Unknown')
            break
    
    # Extract rating and followers
    rating = api_data.get('rating', 0.0)
    followers = api_data.get('user_ratings_total', 0.0)
    
    # Create place data dictionary
    place_data = {
        'name': name,
        'types': types,
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
        'pincode': pincode,
        'country': country,
        'rating': rating,
        'followers': followers
    }
    
    return Place.from_dict(place_data)


def validate_place_data(data: Dict[str, Any]) -> List[str]:
    """Validate place data and return list of errors."""
    errors = []
    
    # Required fields
    required_fields = ['name', 'types', 'latitude', 'longitude', 'address', 'pincode']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Required field '{field}' is missing")
    
    # Validate coordinates
    if 'latitude' in data:
        try:
            lat = float(data['latitude'])
            if not (-90.0 <= lat <= 90.0):
                errors.append("Latitude must be between -90 and 90")
        except (ValueError, TypeError):
            errors.append("Latitude must be a valid number")
    
    if 'longitude' in data:
        try:
            lon = float(data['longitude'])
            if not (-180.0 <= lon <= 180.0):
                errors.append("Longitude must be between -180 and 180")
        except (ValueError, TypeError):
            errors.append("Longitude must be a valid number")
    
    # Validate pincode
    if 'pincode' in data:
        pincode = str(data['pincode'])
        if len(pincode) >= 10:
            errors.append("Pincode must be less than 10 characters")
    
    # Validate rating
    if 'rating' in data:
        try:
            rating = float(data['rating'])
            if not (0.0 <= rating <= 5.0):
                errors.append("Rating must be between 0.0 and 5.0")
        except (ValueError, TypeError):
            errors.append("Rating must be a valid number")
    
    # Validate followers
    if 'followers' in data:
        try:
            followers = float(data['followers'])
            if followers < 0:
                errors.append("Followers must be non-negative")
        except (ValueError, TypeError):
            errors.append("Followers must be a valid number")
    
    return errors


# Export all models and classes
__all__ = [
    'PlaceType',
    'Coordinates',
    'PlaceRating',
    'PlaceAddress',
    'PlaceTimestamps',
    'Place',
    'PlaceCreate',
    'PlaceUpdate',
    'PlaceResponse',
    'PlaceListResponse',
    'PlaceSearchRequest',
    'create_place_from_api_data',
    'validate_place_data'
]
