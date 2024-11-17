from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import weather, dish, satisfaction, dining

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 允许的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(weather.router, prefix="/api")
app.include_router(dish.router, prefix="/api")
app.include_router(satisfaction.router, prefix="/api")
app.include_router(dining.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Smart Canteen Dashboard API"} 