from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, generate, extract_excel, extract_image 
from app.routes import email, mapping  

app = FastAPI()

# Enable CORS for all origins (can restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your routers with route prefixes
app.include_router(upload.router, prefix="/upload")
app.include_router(generate.router, prefix="/generate")
app.include_router(email.router, prefix="/email")
app.include_router(extract_excel.router)
app.include_router(extract_image.router)
app.include_router(mapping.router)

@app.get("/")
def read_root():
    return {"message": "Certificate Generator API"}

@app.get("/debug-routes")
def debug_routes():
    return [route.path for route in app.router.routes]

