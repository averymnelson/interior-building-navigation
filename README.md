# Interior Building Navigation System

## Overview

The Interior Building Navigation System is a web-based application that provides wayfinding functionality for the ENRC building. This system helps users navigate between rooms, find the nearest restrooms, and access information about different rooms within the building.

## Features

- **Interactive Map**: Visualize the building layout with an interactive map
- **Pathfinding**: Find the optimal path between any two points in the building
- **Nearest Restroom Finder**: Locate the closest accessible restroom from any position
- **Turn-by-Turn Directions**: Get detailed navigation instructions with distance and turning information
- **Room Information**: Access details about rooms including descriptions, contacts, and departments
- **Keycard Access Support**: Toggle routes that require keycard access
- **Admin Dashboard**: Manage room information through an administrative interface

## Architecture

The system follows a client-server architecture:

- **Frontend**: HTML/CSS/JavaScript with Leaflet.js for map visualization
- **Backend**: Python Flask server handling pathfinding and data management
- **Database**: Supabase (PostgreSQL-based) for data storage

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Supabase account (for database)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/averymnelson/interior-building-navigation.git
   cd interior-building-navigation
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Create a Supabase project
   - Import the database schema from the `database_schema.sql` file
   - Configure your `.env` file with the Supabase URL and key

## Running the Application

To run the application in development mode:

```bash
flask --app app run
```

For production deployment:

```bash
flask --app app run --host=0.0.0.0
```

The application will be available at `http://localhost:5000` (development) or the server's IP address (production).
It can also be accessed at https://interior-building-navigation.onrender.com

## Database Structure

The system uses four main tables:

1. **Point Table**: Stores locations in the building (rooms, entrances, corners)
2. **Edge Table**: Stores connections between points
3. **Keycard Edge Table**: Stores connections requiring keycard access
4. **Room Info Table**: Stores information about rooms (descriptions, contacts, departments)

## Project Structure

```
interior-building-navigation/
├── navigation_system/
│   ├── algorithms/          # Pathfinding and direction algorithms
│   ├── models/              # Data models for navigation graph
│   ├── tools/               # Utility tools
│   └── utils/               # Helper functions
├── static/
│   ├── images/              # Map images and icons
│   └── styles.css           # CSS styling
├── templates/               # HTML templates
│   ├── admin.html           # Admin dashboard
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── settings.html        # Settings page
│   └── wayfinding.html      # Main navigation interface
├── .env                     # Environment variables
├── app.py                   # Main Flask application
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Usage Instructions

### Basic Navigation

1. Open the application and navigate to the Wayfinding page
2. Enter your starting location
3. Enter your destination room or select "Restroom" to find the nearest restroom
4. Click "Get Directions" to calculate the route
5. Follow the turn-by-turn directions displayed in the panel

### Admin Access

1. Go to the Settings page
2. Click the "Admin Login" button
3. Enter your administrator credentials (contact your system administrator for access)
4. Use the admin dashboard to view, add, edit, or delete room information

Note: Admin access is restricted to authorized personnel only.

## Dependencies

- **Flask**: Web framework
- **Supabase**: Database client
- **Leaflet.js**: Interactive map library
- **Bootstrap**: CSS framework
- **Python-dotenv**: Environment variable management

### Python Dependencies

The project requires the following Python packages:

```
aiohappyeyeballs==2.6.1
aiohttp==3.11.18
aiosignal==1.3.2
annotated-types==0.7.0
anyio==4.9.0
attrs==25.3.0
blinker==1.9.0
certifi==2025.1.31
click==8.1.8
colorama==0.4.6
deprecation==2.1.0
Flask==3.1.0
frozenlist==1.6.0
gotrue==2.12.0
gunicorn==23.0.0
h11==0.14.0
h2==4.2.0
hpack==4.1.0
httpcore==1.0.8
httpx==0.28.1
hyperframe==6.1.0
idna==3.10
iniconfig==2.1.0
itsdangerous==2.2.0
Jinja2==3.1.5
MarkupSafe==3.0.2
multidict==6.4.3
packaging==24.2
pillow==11.1.0
pluggy==1.5.0
postgrest==1.0.1
propcache==0.3.1
pydantic==2.11.3
pydantic_core==2.33.1
PyJWT==2.10.1
pytest==8.3.5
pytest-mock==3.14.0
python-dateutil==2.9.0.post0
python-dotenv==1.1.0
realtime==2.4.2
six==1.17.0
sniffio==1.3.1
storage3==0.11.3
StrEnum==0.4.15
supafunc==0.9.4
typing-inspection==0.4.0
typing_extensions==4.13.2
websockets==14.2
Werkzeug==3.1.0
yarl==1.20.0
```

You can install all dependencies using:
```bash
pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Open a Pull Request

## License

MIT License

Copyright (c) 2025 Interior Building Navigation Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- University of Arkansas for providing the building CAD files
- The ENRC facility staff for providing room information data
- Supabase for database services
- The Flask and Leaflet.js communities for their excellent documentation
