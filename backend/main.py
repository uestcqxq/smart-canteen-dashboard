from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import dish, weather
import uvicorn
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 允许的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dish.router, prefix="/api")
app.include_router(weather.router, prefix="/api")

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 