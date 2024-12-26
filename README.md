# LinkedIn Profile Scraper

A web application that scrapes LinkedIn profile data using Python, Playwright, and Flask. Deployed on Railway.app with Docker containerization.

## Features

- Extracts key profile information:
  - Full name
  - Headline
  - Location
  - Follower count
  - Profile photo URL
  - Background photo URL
  - About/Summary section

## Tech Stack

- **Backend**: Python, Flask
- **Web Scraping**: Playwright
- **Containerization**: Docker
- **Deployment**: Railway.app
- **CI/CD**: Automated deployment via Railway

## Prerequisites

- Python 3.11+
- LinkedIn Account Cookies (li_at)
- Docker (for local containerized testing)

## Local Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd linkedin-scraper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

4. Set up environment variables:
Create a `.env` file in the root directory:
```
LINKEDIN_COOKIE=your_li_at_cookie_value
```

5. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:8080`

## Docker Setup

1. Build the Docker image:
```bash
docker build -t linkedin-scraper .
```

2. Run the container:
```bash
docker run -p 8080:8080 linkedin-scraper
```

## Deployment

This application is configured for deployment on Railway.app:

1. Fork this repository
2. Create a new project on Railway.app
3. Connect your GitHub repository
4. Add environment variables in Railway dashboard
5. Deploy!

## Project Structure

```
linkedin-scraper/
├── app/
│   ├── templates/
│   │   └── index.html
│   ├── __init__.py
│   ├── config.py
│   ├── routes.py
│   ├── scraper.py
│   ├── storage.py
│   └── utils.py
├── data/
│   └── profile_data.json
├── .env
├── .gitignore
├── Dockerfile
├── Procfile
├── README.md
├── requirements.txt
├── run.py
└── setup.sh
```

## API Usage

Send a POST request to `/scrape` with JSON body:
```json
{
    "profile_url": "https://www.linkedin.com/in/example-profile/",
    "cookie": "your_li_at_cookie_value"
}
```

Response format:
```json
{
    "person": {
        "backgroundUrl": "url",
        "firstName": "John",
        "followerCount": 500,
        "headline": "Software Engineer",
        "lastName": "Doe",
        "location": "New York, NY",
        "photoUrl": "url",
        "summary": "About section text",
        "linkedInUrl": "profile_url"
    }
}
```

## Security Notes

- Never commit your LinkedIn cookies to version control
- Use environment variables for sensitive data
- Consider implementing rate limiting for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## Disclaimer

This tool is for educational purposes only. Use it responsibly and in accordance with LinkedIn's terms of service and robots.txt directives.
