"""Builtin router module providing built-in HTMX component endpoints."""

import asyncio
import html
import random

from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse, HTMLResponse

from app.api.services.builtin_service import BuiltinService

# Create an APIRouter instance for the built-in routes
router = APIRouter(prefix="/builtin", tags=["Builtin"])
builtin_service = BuiltinService()


@router.post(
    "/button_click/{color}",
    summary="Change the color of paragraph.",
    response_class=HTMLResponse,
)
async def button_click(color: str = "red") -> HTMLResponse:
    """Change the color of a paragraph element when clicked.

    Parameters
    ----------
    color : str, default='red'
        Target color name.

    Returns
    -------
    HTMLResponse
        Rendered colored paragraph element.
    """
    # Map colors to tailwind classes if needed, or rely on frontend styles
    if color == "red":
        tw_color = "text-red-600"
    elif color == "blue":
        tw_color = "text-blue-600"
    elif color == "green":
        tw_color = "text-green-600"
    else:
        tw_color = f"text-{html.escape(color)}-600"

    response = builtin_service.get_colored_paragraph(tw_color)
    return HTMLResponse(content=response, status_code=200)


@router.get(
    "/element",
    summary="Add a new element to the end of the body and swap a div using hx-swap-oob",
    response_class=HTMLResponse,
)
async def element() -> HTMLResponse:
    """Add a new element to page and swap div out-of-band.

    Returns
    -------
    HTMLResponse
        HTML response containing the new element and swap markup.
    """
    response = builtin_service.get_new_element()
    return HTMLResponse(content=response, status_code=200)


@router.get(
    "/select_element",
    summary="Select a particular element from the response",
    response_class=HTMLResponse,
)
async def select_element() -> HTMLResponse:
    """Return multiple elements for client-side selection.

    Returns
    -------
    HTMLResponse
        HTML response containing selectable elements.
    """
    response = builtin_service.get_select_elements()
    return HTMLResponse(content=response, status_code=200)


@router.get(
    "/select_element_oob",
    summary="Select a particular element from the response to change the button and other OOB elements",
    response_class=HTMLResponse,
)
async def select_element_oob() -> HTMLResponse:
    """Select elements and modify out-of-band controls.

    Returns
    -------
    HTMLResponse
        HTML response modifying button and OOB elements.
    """
    response = builtin_service.get_select_elements_oob()
    return HTMLResponse(content=response, status_code=200)


@router.post(
    "/include",
    summary="Include extra information in the body of the request",
    response_class=HTMLResponse,
)
async def include(request: Request) -> HTMLResponse:
    """Include extra information decoded from request body.

    Parameters
    ----------
    request : Request
        Incoming request with form-encoded payload.

    Returns
    -------
    HTMLResponse
        Rendered response reflecting included values.
    """
    body = await request.body()
    try:
        _, value = body.decode().split("=")
    except ValueError:
        value = "Unknown"

    response = builtin_service.process_include(value)
    return HTMLResponse(content=response, status_code=200)


FORBIDDEN_KEYS = frozenset([
    "undefined",
    "Enter",
    "Shift",
    "CapsLock",
    "Control",
    "Alt",
    "Meta",
    "ArrowUp",
    "ArrowDown",
    "ArrowLeft",
    "ArrowRight",
    "Backspace",
    "Delete",
    "Insert",
    "Home",
    "End",
    "PageUp",
    "PageDown",
    "Tab",
    "Escape",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
    "ScrollLock",
    "Pause",
    "ContextMenu",
    "PrintScreen",
    "NumLock",
    "Clear",
])


@router.get(
    "/vals_example",
    summary="Add information in the request",
    response_class=HTMLResponse,
)
async def vals_example(lastKey: str, extra_info: str) -> HTMLResponse:
    """Check for forbidden keys and return key-press details.

    Parameters
    ----------
    lastKey : str
        Name of the key that was pressed.
    extra_info : str
        Additional metadata sent with the event.

    Returns
    -------
    HTMLResponse
        Rendered key-press info or empty 204 if forbidden.
    """
    forbidden_keys = forbidden_keys_list()
    if lastKey not in forbidden_keys:
        safe_lastKey = html.escape(lastKey)
        safe_extra_info = html.escape(extra_info)
        response = f"""
            <div>Last Key pressed: {safe_lastKey}. {safe_extra_info}</div>
        """
        return HTMLResponse(content=response, status_code=200)
    return HTMLResponse(status_code=204)


def forbidden_keys_list() -> frozenset[str]:
    """Return forbidden key names that should not trigger action.

    Returns
    -------
    frozenset[str]
        Set of forbidden key strings.
    """
    return FORBIDDEN_KEYS


@router.get(
    "/beautiful_div",
    summary="Returns divs with content",
    response_class=HTMLResponse,
)
async def beautiful_div() -> HTMLResponse:
    """Return styled division element with content.

    Returns
    -------
    HTMLResponse
        HTML response with stylized division markup.
    """
    response = """
        <div>Beautiful Div Here</div>
    """
    return HTMLResponse(content=response, status_code=200)


ALLOW_RESPONSE_CHANGE: bool = False


@router.post(
    "/response_allow",
    summary="Changes the state of the variable ALLOW_RESPONSE_CHANGE",
    response_class=Response,
)
async def response_allow() -> Response:
    """Toggle response change permission state.

    Returns
    -------
    Response
        Empty response with HTTP 204 status.
    """
    global ALLOW_RESPONSE_CHANGE
    ALLOW_RESPONSE_CHANGE = not ALLOW_RESPONSE_CHANGE
    return Response(status_code=204)


@router.post(
    "/response_change",
    summary="Returns a text with random numbers when the state is True",
    response_class=Response,
)
async def response_change() -> Response:
    """Return text with random number if response change is allowed.

    Returns
    -------
    Response
        Response with random text or 204 if disallowed.
    """
    if not ALLOW_RESPONSE_CHANGE:
        return Response(status_code=204)

    random_number = random.randint(0, 100)
    response = f"Text Changed to number {random_number}"
    return Response(response, status_code=200)


@router.get(
    "/info",
    summary="Does not return anything but a OK status",
    response_class=Response,
)
async def info() -> Response:
    """Return acknowledgement response without content.

    Returns
    -------
    Response
        Empty response with HTTP 204 status.
    """
    return Response(status_code=204)


@router.get(
    "/htmx_headers",
    summary="Returns headers from the request",
    response_class=HTMLResponse,
)
async def htmx_headers(request: Request) -> HTMLResponse:
    """Check for the presence of a specific HTMX header and return response.

    Parameters
    ----------
    request : Request
        Incoming HTTP request.

    Returns
    -------
    HTMLResponse
        Response based on HTMX header presence.
    """
    await asyncio.sleep(1)
    if request.headers.get("HX-Trigger") == "htmx_header_button_id":
        response = """
            Correct button was selected based on HTMX Request Headers
        """
        return HTMLResponse(content=response, status_code=200)

    return HTMLResponse(status_code=200)


@router.get("/file_download", summary="Download a file", response_class=Response)
async def file_download() -> Response:
    """Trigger the download of a file.

    Returns
    -------
    Response
        FileResponse containing the requested file.
    """
    file_path = "static/img/trollface.png"
    return FileResponse(file_path, media_type="image/png", status_code=200)


@router.get(
    "/sync_first",
    summary="Does not return anything but a OK status",
    response_class=HTMLResponse,
)
async def sync_first() -> HTMLResponse:
    """Simulate a slow operation and indicate the first sync button won.

    Returns
    -------
    HTMLResponse
        Response indicating first sync button won.
    """
    await asyncio.sleep(2)  # Simulating some slow operation
    response = "First sync button won"
    return HTMLResponse(content=response, status_code=200)


@router.get(
    "/sync_second",
    summary="Does not return anything but a OK status",
    response_class=HTMLResponse,
)
async def sync_second() -> HTMLResponse:
    """Simulate a slow operation and indicate the second sync button won.

    Returns
    -------
    HTMLResponse
        Response indicating second sync button won.
    """
    await asyncio.sleep(2)  # Simulating some slow operation
    response = "Second sync button won"
    return HTMLResponse(content=response, status_code=200)


COUNT = 0


@router.get(
    "/server_event_trigger",
    summary="Trigger a server event",
    response_class=HTMLResponse,
)
def server_event_trigger() -> HTMLResponse:
    """Trigger a server event when the COUNT variable reaches 5.

    Returns
    -------
    HTMLResponse
        Response with HX-Trigger header when milestone is reached.
    """
    global COUNT
    COUNT += 1
    response = HTMLResponse(status_code=204)
    if COUNT == 5:
        COUNT = 0
        response.headers["HX-Trigger"] = "server_event_triggered"
    return response
