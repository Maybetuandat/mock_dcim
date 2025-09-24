# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from instance_controller import router

# Create FastAPI app
app = FastAPI(
    title="Instance Management API",
    description="API for managing server instances with pagination and filtering",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the instance router
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Instance Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "get_instances": "/api/v1/instances/",
            "get_instance_by_id": "/api/v1/instances/{id}",
            "get_statistics": "/api/v1/instances/stats/overview"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )