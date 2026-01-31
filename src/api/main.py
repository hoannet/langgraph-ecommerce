"""FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, orders, payment, products, rag
from src.core.config import get_settings
from src.core.logging import get_logger, setup_logging
from src.database.mongodb import MongoDB

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    logger.info("Starting application...")
    
    # Connect to MongoDB
    try:
        await MongoDB.connect()
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
    
    # Connect to TiDB Vector
    try:
        from src.database.tidb import TiDBVector
        TiDBVector.connect()
        logger.info("TiDB Vector connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to TiDB Vector: {e}")
    
    yield
    
    # Close connections
    await MongoDB.close()
    
    from src.database.tidb import TiDBVector
    TiDBVector.close()
    
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="LangGraph-based chatbot with PaymentAgent",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(chat.router)
    app.include_router(payment.router)
    app.include_router(products.router)
    app.include_router(orders.router)
    app.include_router(rag.router)

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "LangGraph Chatbot API",
            "version": settings.app_version,
            "docs": "/docs",
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    logger.info(f"FastAPI application created: {settings.app_name} v{settings.app_version}")
    return app


# Create app instance
app = create_app()
