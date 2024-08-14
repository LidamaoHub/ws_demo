# WebSocket Middleware Project

This project implements a WebSocket middleware with a user-friendly frontend interface. It demonstrates real-time communication, user authentication, and REST API integration.

## Features

- WebSocket connection with authentication
- Real-time message broadcasting
- Personal messaging support
- REST API for sending messages and getting user counts
- Frontend interface with protocol and server URL selection
- Local storage of user preferences for protocol and server URL
- Responsive UI with connection status indicators

## Backend Setup

### Prerequisites

- Python 3.7+
- FastAPI
- Uvicorn

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install the required packages:
   ```
   pip install fastapi uvicorn
   ```

3. Run the server:
   ```
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

## Frontend Setup

The frontend is a single HTML file (`index.html`) that can be opened directly in a web browser. No additional setup is required.

## Usage

1. Open `index.html` in a web browser.

2. Select the protocol (ws:// or wss://) and enter the server URL.

3. Enter an authentication token (default is "123456").

4. Click "Connect and Authenticate" to establish a WebSocket connection.

5. Once authenticated, you can send and receive real-time messages.

6. Use the REST API section to test HTTP endpoints.

## Key Components

### Backend (`app.py`)

- `ConnectionManager`: Manages WebSocket connections and user authentication.
- `/ws` endpoint: Handles WebSocket connections and authentication.
- `/message` endpoint: Allows sending messages via REST API.
- `/user_count` endpoint: Returns the count of total and authenticated users.

### Frontend (`index.html`)

- WebSocket connection and message handling
- User interface for sending messages and interacting with the server
- Local storage of user preferences (protocol and server URL)

## Local Storage Feature

The frontend now saves the user's protocol choice (ws:// or wss://) and server URL to the browser's local storage. This means that when a user refreshes the page or returns later, their previous settings will be automatically loaded.

## Testing

1. Start the backend server.
2. Open the frontend HTML file in a browser.
3. Connect to the WebSocket server using the provided interface.
4. Test sending and receiving messages.
5. Use the REST API section to test HTTP endpoints.

## Notes

- The default authentication token is "123456". In a real-world scenario, implement proper security measures.
- Ensure your server supports WebSocket connections if deploying to a production environment.
