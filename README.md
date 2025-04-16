# Running the Project with Docker

This section provides instructions to build and run the project using Docker.

## Prerequisites

- Ensure Docker and Docker Compose are installed on your system.
- Python version 3.10 is used in the Dockerfile.

## Environment Variables

- `APP_ENV`: Set to `production` for production environment.
- `POSTGRES_USER`: Database username (default: `user`).
- `POSTGRES_PASSWORD`: Database password (default: `password`).

## Build and Run Instructions

1. Build the Docker images and start the services:

   ```bash
   docker-compose up --build
   ```

2. Access the application at `http://localhost:8080`.

## Exposed Ports

- Application: `8080` (mapped to host).
- Database: Not exposed to host.

## Special Configuration

- The application requires `libsndfile1` system library, installed during the build process.
- A virtual environment is created within the container for dependency isolation.

For further details, refer to the existing documentation in the repository.# tts_backend
