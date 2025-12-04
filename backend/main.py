from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import trades, pnl, curve, arb

app = FastAPI(title="Energy Trading Operations Suite API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(pnl.router, prefix="/api/pnl", tags=["pnl"])
app.include_router(curve.router, prefix="/api/curve", tags=["curve"])
app.include_router(arb.router, prefix="/api/arb", tags=["arb"])

@app.get("/")
def read_root():
    return {"message": "Energy Trading Operations Suite API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
