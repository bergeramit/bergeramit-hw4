# County Health Data API - CS1060 HW4

**Live API Endpoint:** https://cs1060-hw4-bergeramit.netlify.app/county_data

A RESTful API that provides access to county-level health data from the United States. The API allows querying health metrics for different counties based on ZIP codes and measure names.

## Project Overview

This project consists of:
- **Two CSV datasets**: County health rankings and ZIP-to-county mapping data
- **SQLite database**: Created by converting CSV files using `csv_to_sqlite.py`
- **Netlify Functions**: Serverless API endpoint that queries the database
- **Automated deployment**: Deployed to Netlify with database included in function bundle

## Database Setup

The project uses two main datasets:

1. **`county_health_rankings.csv`** - Contains health metrics for US counties including:
   - Adult obesity rates
   - Violent crime rates
   - Unemployment rates
   - Children in poverty
   - Diabetic screening rates
   - And many more health indicators

2. **`zip_county.csv`** - Maps ZIP codes to county and state information

### Converting CSV to SQLite Database

The `csv_to_sqlite.py` script converts CSV files to SQLite database tables:

```bash
# Convert ZIP to county mapping data
python3 csv_to_sqlite.py data.db zip_county.csv

# Convert county health rankings data
python3 csv_to_sqlite.py data.db county_health_rankings.csv
```

This creates two tables in `data.db`:
- `zip_county` - ZIP code to county/state mapping
- `county_health_rankings` - Health metrics by county and year

## Local Development

### Prerequisites

- Node.js (for Netlify CLI)
- Python 3 (for CSV to SQLite conversion)

### Setup

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Ensure database exists:**
   ```bash
   # Convert CSV files to SQLite if not already done
   python3 csv_to_sqlite.py data.db zip_county.csv
   python3 csv_to_sqlite.py data.db county_health_rankings.csv
   ```

3. **Start local development server:**
   ```bash
   npm run dev
   # or
   netlify dev
   ```

4. **Test the API locally:**
   ```bash
   curl -H "content-type: application/json" \
     -d '{"zip":"02138","measure_name":"Adult obesity"}' \
     http://localhost:8888/county_data
   ```

## API Usage

### Endpoint

`POST /.netlify/functions/county_data`

### Request Format

Send a POST request with JSON payload:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity"}' \
  https://cs1060-hw4-bergeramit.netlify.app/county_data
```

### Parameters

- **`zip`** (string, required): 5-digit ZIP code
- **`measure_name`** (string, required): Name of the health measure to query

### Valid Measure Names

The API accepts the following health measures:
- Violent crime rate
- Unemployment
- Children in poverty
- Diabetic screening
- Mammography screening
- Preventable hospital stays
- Uninsured
- Sexually transmitted infections
- Physical inactivity
- Adult obesity
- Premature Death
- Daily fine particulate matter

### Response Format

**Success Response (200):**
```json
[
  {
    "State": "MA",
    "County": "Middlesex County",
    "State_code": "25",
    "County_code": "17",
    "Year_span": "2010",
    "Measure_name": "Adult obesity",
    "Measure_id": "11",
    "Numerator": "266426",
    "Denominator": "1143459.228",
    "Raw_value": "0.233",
    "Confidence_Interval_Lower_Bound": "0.224",
    "Confidence_Interval_Upper_Bound": "0.242",
    "Data_Release_Year": "2014",
    "fipscode": "25017"
  }
]
```

**Error Response (400):**
```json
{
  "result": null,
  "error": "Invalid measure name"
}
```

## Examples

### Query Adult Obesity Data for ZIP 02138 (Cambridge, MA)
```bash
curl -H "content-type: application/json" \
  -d '{"zip":"02138","measure_name":"Adult obesity"}' \
  https://cs1060-hw4-bergeramit.netlify.app/county_data
```

### Query Unemployment Data for ZIP 90210 (Beverly Hills, CA)
```bash
curl -H "content-type: application/json" \
  -d '{"zip":"90210","measure_name":"Unemployment"}' \
  https://cs1060-hw4-bergeramit.netlify.app/county_data
```

### Invalid Measure Name (Returns Error)
```bash
curl -H "content-type: application/json" \
  -d '{"zip":"02138","measure_name":"Invalid Measure"}' \
  https://cs1060-hw4-bergeramit.netlify.app/county_data
```

## Deployment

This project is configured for automatic deployment to Netlify:

### Deployment Features

- **Database included**: The `data.db` file is bundled with the Netlify function
- **CORS enabled**: API accepts cross-origin requests
- **Error handling**: Comprehensive validation and error responses
- **Performance optimized**: Database queries are efficient and cached

### Deploy to Netlify

1. **Connect repository to Netlify:**
   - Go to [Netlify](https://netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect your Git repository

2. **Configure build settings:**
   - Build command: `npm run build` (if needed)
   - Publish directory: `.` (root directory)
   - Functions directory: `netlify/functions`

3. **Environment variables** (if needed):
   - No additional environment variables required

4. **Deploy:**
   - Netlify will automatically detect the configuration and deploy

### Configuration Files

- **`netlify.toml`**: Netlify deployment configuration
- **`package.json`**: Node.js dependencies and scripts
- **`netlify/functions/county_data.js`**: Main API function

## Project Structure

```
├── county_health_rankings.csv    # Health metrics dataset
├── zip_county.csv               # ZIP to county mapping
├── data.db                      # SQLite database
├── csv_to_sqlite.py            # CSV to SQLite converter
├── netlify/
│   └── functions/
│       └── county_data.js       # API endpoint function
├── netlify.toml                # Netlify configuration
├── package.json                # Node.js dependencies
└── README.md                   # This file
```

## Troubleshooting

### Common Issues

1. **"data.db not found" error:**
   - Ensure CSV files are converted to SQLite using `csv_to_sqlite.py`
   - Check that `data.db` exists in the project root

2. **Function not loading:**
   - Verify `netlify.toml` has correct function configuration
   - Check that `package.json` includes required dependencies

3. **Invalid JSON errors:**
   - Ensure request has proper `Content-Type: application/json` header
   - Verify JSON payload is valid

4. **CORS errors:**
   - The API includes CORS headers, but check browser console for details

## License

This project is created for educational purposes as part of CS1060 coursework.