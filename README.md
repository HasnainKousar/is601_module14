# Module 14: FastAPI Calculator App

This project is a FastAPI-based web application that allows users to perform various calculations and manage their accounts. It includes authentication, database integration, and a modern front-end UI.

## Features
- User registration and login
- Perform basic calculations (add, subtract, multiply, divide)
- Database-backed calculation history
- JWT authentication
- Integration with Redis for session management
- End-to-end, integration, and security tests

## Security
- Uses Trivy for vulnerability scanning
- Suppresses specific CVEs using `.trivyignore` (e.g., CVE-2025-43859, CVE-2024-33663)

## Getting Started
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the application locally:**
   ```bash
   uvicorn app.main:app --reload
   ```
3. **Run with Docker Compose:**
   ```bash
   docker compose up -d
   ```
4. **Execute tests locally:**
   ```bash
   pytest
   ```

## Docker Hub Repository
- [Docker Hub: hkousar13/module14](https://hub.docker.com/repository/docker/hkousar13/module14/general)

## Project Structure
- `app/` - FastAPI application code
- `static/` - CSS and JS files
- `templates/` - HTML templates
- `tests/` - Test suites (e2e, integration)
- `.trivyignore` - CVEs to ignore in Trivy scans
- `Dockerfile` & `docker-compose.yml` - Container setup

## License
Copyright 2024 Keith Williams

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
