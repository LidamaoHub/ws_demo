# WebSocket Middleware

This project implements a WebSocket middleware with the following features:

1. WebSocket connection with authentication
2. Broadcasting messages to all authenticated users
3. Sending personal messages to specific users
4. REST API for sending messages and getting user count
5. Hardware status monitoring for the Docker container

## Prerequisites

- Docker
- Docker Compose (optional, for easier deployment)

## Deployment

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Build the Docker image:
   ```
   docker build -t websocket-middleware .
   ```

3. Run the Docker container:
   ```
   docker run -d -p 8000:8000 websocket-middleware
   ```

   Or, if you prefer using Docker Compose, create a `docker-compose.yml` file with the following content:

   ```yaml
   version: '3'
   services:
     websocket-middleware:
       build: .
       ports:
         - "8000:8000"
   ```

   Then run:
   ```
   docker-compose up -d
   ```

4. (Optional) Set up Nginx as a reverse proxy:
   - Copy the provided `nginx.conf` to your Nginx configuration directory.
   - Modify the `server_name` directive in the `nginx.conf` file to match your domain.
   - Restart Nginx.

## Usage

### WebSocket Connection

Connect to the WebSocket at `ws://localhost:8000/ws`

### Authentication

Send a JSON message with the following format:
```json
{
  "type": "auth",
  "token": "123456"
}
```

### Sending Messages

After authentication, send a JSON message with the following format:
```json
{
  "type": "message",
  "message": "Your message here"
}
```

### REST API

- Send a message: 
  POST to `http://localhost:8000/message`
  ```json
  {
    "message": "Your message here",
    "userid": "optional-user-id"
  }
  ```

- Get user count:
  GET `http://localhost:8000/user_count`

- Get hardware status:
  GET `http://localhost:8000/hardware_status`

## Customization

- To change the authentication token, modify the condition in the `websocket_endpoint` function in `app.py`.
- To add more features or modify existing ones, edit `app.py` and rebuild the Docker image.
