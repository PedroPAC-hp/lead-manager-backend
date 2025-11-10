# lead_manager_api/api/__init__.py

from .auth import router as auth_router
from .import_routes import router as import_router

# Esta é uma boa prática, mas opcional.
# Define o que é exportado quando alguém faz 'from .api import *'
__all__ = ["auth_router", "import_router"]
