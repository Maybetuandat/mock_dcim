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
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the instance router
app.include_router(router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9999,
        reload=True,
        log_level="info"
    )