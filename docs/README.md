# Place Models

This package contains comprehensive data models for the Places Management System, providing type safety, validation, and structured data handling.

## Overview

The models package includes:

- **Place**: Main place data model with all fields
- **PlaceType**: Enumeration of standard place types
- **Coordinates**: Geographic coordinates with validation
- **PlaceRating**: Rating and follower count model
- **PlaceAddress**: Address information model
- **PlaceTimestamps**: Creation and update timestamps
- **Pydantic Models**: For API validation and serialization

## Quick Start

### Basic Usage

```python
from models.place import Place, Coordinates, PlaceAddress, PlaceRating

# Create a place
coords = Coordinates(latitude=28.6139, longitude=77.2090)
address = PlaceAddress(
    address="Connaught Place, New Delhi",
    pincode="110001",
    country="India"
)
rating = PlaceRating(rating=4.5, followers=1250)

place = Place(
    name="Connaught Place",
    types="tourist_attraction, shopping_mall",
    coordinates=coords,
    address=address,
    rating=rating
)

print(f"Place: {place.name}")
print(f"Location: {place.coordinates.latitude}, {place.coordinates.longitude}")
print(f"Rating: {place.rating.rating}/5.0")
```

### From Dictionary Data

```python
from models.place import Place, validate_place_data

# Place data from API or database
place_data = {
    'name': 'Taj Mahal',
    'types': 'tourist_attraction, landmark',
    'latitude': 27.1751,
    'longitude': 78.0421,
    'address': 'Agra, Uttar Pradesh 282001',
    'pincode': '282001',
    'country': 'India',
    'rating': 4.8,
    'followers': 5000
}

# Validate data
errors = validate_place_data(place_data)
if not errors:
    place = Place.from_dict(place_data)
    print(f"Created place: {place.name}")
```

### API Data Conversion

```python
from models.place import create_place_from_api_data

# API response data
api_data = {
    'name': 'Eiffel Tower',
    'types': ['tourist_attraction', 'landmark'],
    'geometry': {
        'location': {'lat': 48.8584, 'lng': 2.2945}
    },
    'formatted_address': 'Champ de Mars, Paris, France',
    'address_components': [
        {'long_name': '75007', 'types': ['postal_code']},
        {'long_name': 'France', 'types': ['country']}
    ],
    'rating': 4.6,
    'user_ratings_total': 3500
}

place = create_place_from_api_data(api_data)
```

## Model Components

### Place

The main place model containing all place information:

```python
@dataclass
class Place:
    name: str                    # Place name
    types: str                   # Comma-separated place types
    coordinates: Coordinates     # Geographic coordinates
    address: PlaceAddress        # Address information
    place_id: Optional[int]      # Database ID
    rating: Optional[PlaceRating] # Rating and followers
    timestamps: Optional[PlaceTimestamps] # Creation/update times
```

**Methods:**

- `from_dict(data)`: Create from dictionary
- `to_dict()`: Convert to dictionary
- `update(**kwargs)`: Update fields
- `get_distance_to(other_place)`: Calculate distance
- `is_near(other_place, max_distance_km)`: Check proximity
- `has_type(place_type)`: Check if has specific type
- `get_types_list()`: Get list of types

### Coordinates

Geographic coordinates with validation:

```python
@dataclass
class Coordinates:
    latitude: float   # -90 to 90
    longitude: float  # -180 to 180
```

**Methods:**

- `distance_to(other)`: Calculate distance using Haversine formula
- `to_dict()`: Convert to dictionary
- `to_tuple()`: Convert to tuple

### PlaceRating

Rating and follower information:

```python
@dataclass
class PlaceRating:
    rating: float     # 0.0 to 5.0
    followers: float  # Non-negative
```

### PlaceAddress

Address information:

```python
@dataclass
class PlaceAddress:
    address: str   # Full address
    pincode: str   # Postal code (max 9 digits)
    country: str   # Country name
```

### PlaceType Enum

Standard place types for validation:

```python
class PlaceType(str, Enum):
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    TOURIST_ATTRACTION = "tourist_attraction"
    # ... many more
```

**Class Methods:**

- `get_all_types()`: Get all available types
- `validate_type(place_type)`: Validate a type

## Validation

### Data Validation

```python
from models.place import validate_place_data

errors = validate_place_data(place_data)
if errors:
    print(f"Validation errors: {errors}")
```

### Model Validation

The models include built-in validation:

```python
# This will raise ValueError for invalid coordinates
coords = Coordinates(latitude=200.0, longitude=0.0)  # Invalid latitude

# This will raise ValueError for invalid rating
rating = PlaceRating(rating=6.0, followers=100)  # Invalid rating
```

## Pydantic Models (Optional)

If Pydantic is available, additional models are provided for API validation:

```python
from models.place import PlaceCreate, PlaceUpdate, PlaceResponse

# For creating places
create_data = PlaceCreate(
    name="New Place",
    types="restaurant",
    latitude=40.7128,
    longitude=-74.0060,
    address="123 Main St, New York",
    pincode="100001"
)

# For updating places
update_data = PlaceUpdate(
    rating=4.5,
    followers=1000
)

# For API responses
response = PlaceResponse(
    place_id=1,
    name="Place Name",
    # ... other fields
)
```

## Database Integration

### Using with Database

```python
from models.place import Place
from utils.database import PlacesDatabase

# Create place
place = Place.from_dict(place_data)

# Add to database
db = PlacesDatabase()
success = db.add_place_with_model(place)

# Get from database
retrieved_place = db.get_place_by_id_with_model(place_id)

# Update place
place.update(rating=4.5, followers=1500)
db.update_place_with_model(place)
```

## Examples

See `examples/place_model_usage.py` for comprehensive examples of:

- Basic place creation
- Data validation
- Place operations (distance, proximity)
- API data conversion
- Place type validation

## Features

### Type Safety

- Strong typing with dataclasses
- Enum for place types
- Validation on creation

### Data Validation 1

- Coordinate range validation
- Rating range validation (0-5)
- Pincode format validation
- Required field validation

### Geographic Operations

- Distance calculation using Haversine formula
- Proximity checking
- Coordinate validation

### API Integration

- Easy conversion from API data
- Pydantic models for API validation
- JSON serialization support

### Database Integration 1

- Dictionary conversion for database operations
- Model-based database methods
- Automatic timestamp handling

## Error Handling

The models provide clear error messages:

```python
try:
    place = Place.from_dict(invalid_data)
except ValueError as e:
    print(f"Invalid place data: {e}")
```

## Performance

- Lightweight dataclasses
- Minimal memory overhead
- Fast validation
- Efficient distance calculations

## Dependencies

- **Required**: `dataclasses`, `typing`, `datetime`, `enum`
- **Optional**: `pydantic` (for API validation models)
- **Built-in**: `math` (for distance calculations)

## Migration from Dictionary Data

If you're currently using dictionaries for place data, migration is straightforward:

```python
# Before
place_data = {
    'name': 'Place Name',
    'latitude': 40.7128,
    'longitude': -74.0060,
    # ... other fields
}

# After
place = Place.from_dict(place_data)
# Now you have type safety and validation
```

The models are designed to be backward compatible and can work alongside existing dictionary-based code.
