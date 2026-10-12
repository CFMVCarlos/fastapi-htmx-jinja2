"""Application package providing shared templates and configurations."""

from fastapi.templating import Jinja2Templates

__all__ = ["templates"]

templates = Jinja2Templates(directory="templates")
