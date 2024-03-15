import os
from typing import Any

from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["Health"])
def get_health() -> Any:
    return {"status": "OK"}


# Define the directory where your router modules are located
routers_directory = ["app/firestore/endpoints", "app/sqlmodel/api/endpoints"]


def import_router(router_directory, module_name):
    # Import the module dynamically
    module = __import__(f"{router_directory}.{module_name}", fromlist=["router"])

    # Get the router from the module
    router = getattr(module, "router")

    # Include the router
    api_router.include_router(
        router, prefix=f"/{module_name}", tags=[module_name.capitalize().replace("_", " ")]
    )


# Iterate through files in the directory
for directory in routers_directory:
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".py") and filename != "__init__.py":
                import_router(directory.replace("/", "."), filename[:-3])
    except FileNotFoundError:
        pass
