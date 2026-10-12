"""Extensions router module providing SSE and WebSocket endpoints."""

import asyncio
import datetime as dt
import html
import logging

from fastapi import APIRouter, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sse_starlette import EventSourceResponse

router = APIRouter(prefix="/extensions", tags=["EXT"])

# Set up logging
logger = logging.getLogger(__name__)  # Create a logger object for this module
logger.setLevel(logging.INFO)  # Set the logging level to INFO
handler = (
    logging.StreamHandler()
)  # Create a stream handler to output logs to the console
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
)  # Define the log message format
handler.setFormatter(formatter)  # Set the formatter for the handler
logger.addHandler(handler)  # Add the handler to the logger


# --------------------------------------------------------------------------------
# SSE Event Triggered Route
# --------------------------------------------------------------------------------
@router.get("/sse_event_triggered", response_class=HTMLResponse)
async def sse_event_triggered(dataFromSSE: str | None = None) -> HTMLResponse:
    """Return data received from Server-Sent Event trigger.

    Parameters
    ----------
    dataFromSSE : str | None, default=None
        Data string payload sent via SSE.

    Returns
    -------
    HTMLResponse
        HTML response echoing the escaped content.
    """
    safe_content = html.escape(dataFromSSE) if dataFromSSE else "No data provided"
    return HTMLResponse(content=safe_content)


# --------------------------------------------------------------------------------
# Streaming Events Route (Server-Sent Events)
# --------------------------------------------------------------------------------
@router.get("/stream")
async def message_stream(request: Request) -> EventSourceResponse:
    """Stream events to the client using Server-Sent Events.

    Parameters
    ----------
    request : Request
        Incoming request to monitor client disconnects.

    Returns
    -------
    EventSourceResponse
        EventSource response streaming SSE messages.
    """

    async def event_generator():
        count = 0
        while True:
            # If the client disconnects, stop the event stream
            if await request.is_disconnected():
                break

            count += 1
            # Send a message every second (e.g., every 1 count)
            if count % 1 == 0:
                yield {
                    "event": "sse_event",
                    "data": f"<div>Live Stream Update #{count}</div>",
                }

            # Every 10 counts, send a special message
            if count % 10 == 0:
                yield {
                    "event": "sse_event_10",
                    "data": f"<div>Milestone Event: Batch #{int(count / 10)} reached</div>",
                }

            # Sleep for 1 second before sending the next message
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


# --------------------------------------------------------------------------------
# WebSocket Route
# --------------------------------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Handle WebSocket connections and broadcast messages.

    Parameters
    ----------
    websocket : WebSocket
        Connected WebSocket instance.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Wait for the client to send a message (JSON format)
            msg = await websocket.receive_json()
            # Send the message to all connected clients
            await manager.send_message(msg["chat_message"])
    except WebSocketDisconnect:
        # Handle client disconnection
        logger.info("Client has disconnected.")
    except Exception:
        # Handle any unexpected errors
        logger.exception("Error Occurred")
    finally:
        # Ensure the client is disconnected properly
        await manager.disconnect(websocket)


# --------------------------------------------------------------------------------
# Loading States Route (POST)
# --------------------------------------------------------------------------------
@router.post("/loading_states", response_class=Response)
async def post_loading_states() -> Response:
    """Simulate a time-consuming operation with delay.

    Returns
    -------
    Response
        Empty response with HTTP 204 status.
    """
    await asyncio.sleep(5)  # Simulate a delay of 5 seconds
    return Response(status_code=204)  # No content to return


# --------------------------------------------------------------------------------
# Loading States Route (GET)
# --------------------------------------------------------------------------------
@router.get("/loading_states", response_class=HTMLResponse)
async def get_loading_states() -> HTMLResponse:
    """Return an HTML button that simulates a loading state when clicked.

    Returns
    -------
    HTMLResponse
        Rendered HTML markup for button.
    """
    html_content: str = """
        Click me for preload (Swapped)
        """
    return HTMLResponse(content=html_content)


# --------------------------------------------------------------------------------
# Path Dependencies Route (GET)
# --------------------------------------------------------------------------------
@router.get("/path_deps", response_class=HTMLResponse)
async def get_path_deps() -> HTMLResponse:
    """Return a simple HTML list item.

    Returns
    -------
    HTMLResponse
        Rendered list item HTML content.
    """
    html_content: str = """
        <li>Path Deps</li>
    """
    return HTMLResponse(content=html_content)


# --------------------------------------------------------------------------------
# Path Dependencies Route (POST)
# --------------------------------------------------------------------------------
@router.post("/path_deps", response_class=HTMLResponse)
async def post_path_deps() -> HTMLResponse:
    """Return an HTML button to post more data to the list.

    Returns
    -------
    HTMLResponse
        Rendered button HTML content.
    """
    html_content: str = """
        <button hx-post="/path_deps" hx-swap="none">Post more to the list</button>
    """
    return HTMLResponse(content=html_content)


# --------------------------------------------------------------------------------
# Sweet Alert Confirmation Route (GET)
# --------------------------------------------------------------------------------
@router.get("/sweet_alert_confirmed", response_class=HTMLResponse)
async def sweet_alert_confirmed() -> HTMLResponse:
    """Return a confirmation message when sweet alert is confirmed.

    Returns
    -------
    HTMLResponse
        Rendered confirmation message HTML content.
    """
    html_content: str = """
        Sweet Alert Confirmed
    """
    return HTMLResponse(content=html_content)


# --------------------------------------------------------------------------------
# SSE Connection Manager (Handles WebSocket connections)
# --------------------------------------------------------------------------------
class ConnectionManager:
    """Manage active WebSocket connections and broadcasting."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a WebSocket connection and register it.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket instance to register.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from active list.

        Parameters
        ----------
        websocket : WebSocket
            WebSocket instance to remove.
        """
        self.active_connections.remove(websocket)

    async def send_message(self, message: str) -> None:
        """Broadcast a message to all active WebSocket connections.

        Parameters
        ----------
        message : str
            Message string to broadcast.
        """
        if not self.active_connections:
            return

        # Format the current time once for all connections
        formatted_time: str = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S")
        escaped_message: str = html.escape(message)
        content: str = f"""
            <div hx-swap-oob="beforeend:#content">
            <p>{formatted_time} || {escaped_message}</p>
            </div>
            <input hx-swap-oob="outerHTML:#web_socket_input" id="web_socket_input" name="chat_message" placeholder="Web Socket Phrase"/>
        """
        for connection in self.active_connections:
            await connection.send_text(content)


# Initialize the connection manager instance
manager: ConnectionManager = ConnectionManager()
