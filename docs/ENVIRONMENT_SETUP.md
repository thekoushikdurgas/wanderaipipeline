# Environment Setup and Configuration

## Overview

This document describes the environment configuration for the Places Management System and recent improvements made to the setup process.

## Environment Variables

### Required Variables

#### Database Configuration
- `user`: PostgreSQL username
- `password`: PostgreSQL password
- `host`: Database host address
- `port`: Database port (default: 5432)
- `dbname`: Database name
- `DATABASE_URL`: Alternative connection string format

#### Application Configuration
- `DEBUG`: Set to `True` to enable debug mode and performance logging
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Optional Variables

#### OLA Maps API Configuration
- `OLA_MAPS_API_KEY`: API key for OLA Maps services
- `OLA_MAPS_BEARER_TOKEN`: Bearer token for API authentication

## Setup Methods

### Method 1: Automated Setup (Recommended)
```bash
python setup_env.py
```

This script will:
- Copy `env.example` to `.env`
- Display a summary of the configuration
- Mask sensitive values for security
- Provide next steps

### Method 2: Manual Setup
```bash
cp env.example .env
```

Then edit the `.env` file to customize your configuration.

## Performance Logging

### Recent Fix
The performance logging system has been fixed to properly track operation timing. Previously, there were warnings about timers not being started due to mock implementations.

### How to Enable
Set `DEBUG=True` in your `.env` file to enable:
- Database operation timing
- Excel operation timing
- API call timing
- Performance metrics logging

### Example Output
```
⏱️ Operation 'database_initialization' completed in 1.1034s
⏱️ Operation 'excel_write_operation' completed in 2.0601s
⏱️ Operation 'get_all_places' completed in 2.6001s
```

## Current Configuration

The project is configured to use:
- **Database**: Supabase PostgreSQL
- **Host**: aws-1-ap-southeast-1.pooler.supabase.com
- **Port**: 6543 (Transaction Pooler)
- **Database**: postgres
- **User**: postgres.evsjreawstqtkcsbwfjt

## Security Notes

- Sensitive values (passwords, tokens) are masked in the setup script output
- The `env.example` file contains actual credentials for the current setup
- For production use, replace with your own secure credentials
- Never commit `.env` files to version control

## Troubleshooting

### Performance Logging Not Working
1. Ensure `DEBUG=True` is set in your `.env` file
2. Check that the environment variable is being loaded correctly
3. Verify that the logging system is initialized properly

### Database Connection Issues
1. Verify all database environment variables are set correctly
2. Check network connectivity to the database host
3. Ensure the database credentials are valid

### API Testing Issues
1. Verify OLA Maps API credentials are set correctly
2. Check that the API key and bearer token are valid
3. Ensure network connectivity to the OLA Maps API
