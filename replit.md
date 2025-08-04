# Overview

This is a Flask-based cryptocurrency mining automation platform with a web interface in Arabic. The application provides a centralized dashboard for managing multiple mining operations through Telegram bot integrations. Users can configure mining URLs, monitor active mining sessions, and manage their cryptocurrency mining activities through a modern web interface.

**Status**: Production-ready for deployment on Zeabur, Heroku, Railway, and other cloud platforms.

## Recent Changes (August 4, 2025)

✓ **BEAMX Mining Fix**: Fixed "dot button" functionality with correct API endpoints
✓ **URL Processing**: Added function to extract tgWebAppData from full bot URLs
✓ **Task ID Handling**: Improved BEAMX task_id extraction with proper status validation
✓ **Mining Logic**: Updated waiting time to 11 seconds for successful task completion
✓ **Page Information Reading**: Enhanced to read accurate balance, daily tasks (17/30), and hourly tasks (15/15) from JavaScript variables
✓ **Intelligent Mining Logic**: Implemented proper task completion detection - stops when daily tasks 100% complete until UTC+3, waits 10 minutes when hourly tasks 100% complete
✓ **Multiple URLs Support**: Added support for multiple URLs per user (up to 100 links) with textarea inputs and batch processing
✓ **Enhanced UI**: Updated interface to show mining information with detailed progress indicators
✓ **Background Processing**: Improved mining logic to use proper IP and User-Agent handling for background operations
✓ **Data Extraction**: Fixed regex patterns to extract accurate information from JavaScript variables instead of HTML parsing
✓ **Deployment Optimization**: Fixed all deployment issues for cloud hosting
✓ **Port Configuration**: Added dynamic PORT environment variable support
✓ **Gunicorn Integration**: Optimized for production with proper Procfile
✓ **Health Check**: Added /health endpoint for service monitoring
✓ **Security**: Strengthened secret key management for production
✓ **Documentation**: Added comprehensive deployment guides and README

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Web Framework**: Flask with Jinja2 templates for server-side rendering
- **UI Framework**: Bootstrap 5 for responsive design with RTL (right-to-left) Arabic language support
- **Styling**: Custom CSS with gradient backgrounds and glassmorphism effects
- **JavaScript**: Vanilla JS for client-side interactions, device detection, and AJAX communication
- **Internationalization**: Arabic-first interface with RTL layout and Arabic fonts (Cairo font family)

## Backend Architecture
- **Core Framework**: Flask web application with session management
- **Mining Engine**: Custom `MiningCore` class that handles mining operations through threading
- **Session Management**: Flask sessions with configurable secret key
- **Data Persistence**: JSON file-based storage (`users_data.json`) for user data, mining configurations, and custom links
- **Threading**: Multi-threaded architecture for concurrent mining operations per user
- **Logging**: Python logging module for debugging and monitoring

## Data Storage
- **Primary Storage**: JSON file system for user data, mining sessions, and configuration
- **Session Storage**: Flask session cookies for user state management
- **Data Structure**: Nested JSON with user sessions, mining types, task counters, and custom bot links
- **Backup Strategy**: File-based persistence with atomic writes

## Authentication & Authorization
- **Admin System**: Simple admin ID-based authorization (ADMIN_ID = 962731079)
- **Session Management**: Flask sessions for user state persistence
- **Access Control**: Basic admin privileges for managing forced channels and custom links

## Integration Architecture
- **Telegram Bots**: Integration with multiple cryptocurrency mining bots (COIN, BANAN, TRX, SHIB)
- **HTTP Requests**: Requests library for external API communication
- **Bot Communication**: Custom referral link system with predefined bot configurations
- **Mining Automation**: Automated task execution through URL-based mining operations

# External Dependencies

## Python Packages
- **Flask**: Web framework for HTTP handling and template rendering
- **requests**: HTTP client for external API communication and bot interactions
- **threading**: Built-in Python module for concurrent mining operations
- **logging**: Built-in Python module for application monitoring
- **datetime**: Built-in Python module for timestamp management
- **json**: Built-in Python module for data serialization
- **os**: Built-in Python module for environment variable management

## Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive UI components
- **Font Awesome 6**: Icon library for UI elements
- **Google Fonts (Cairo)**: Arabic font family for proper RTL text rendering
- **Flag CDN**: Country flag images for location display

## Telegram Bot Integrations
- **CryptoFreeMoney_bot**: COIN mining operations
- **InstaTasker_bot**: BANAN token mining
- **TRXVAULTMININGRoBot**: TRX cryptocurrency mining
- **SHIBAdsPaybot**: SHIB token mining

## External Services
- **IP Geolocation**: User location detection for displaying country information
- **Telegram Web App**: Integration with Telegram's web app data system
- **Cryptocurrency Networks**: Support for various blockchain networks (BEP20, TRX, etc.)

## Development Environment
- **Python 3**: Runtime environment
- **Replit**: Cloud-based development and hosting platform
- **Environment Variables**: Configuration through environment variables for security