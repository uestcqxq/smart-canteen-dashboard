from fastapi import APIRouter, HTTPException, BackgroundTasks
import httpx
import os
from dotenv import load_dotenv
from fastapi_cache.decorator import cache

router = APIRouter()

# 加载环境变量
load_dotenv()

# 获取高德地图 API key 和默认城市
AMAP_KEY = os.getenv("AMAP_KEY")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "泰州")

@router.get("/weather")
@cache(expire=1800)  # 缓存30分钟
async def get_weather(city: str = DEFAULT_CITY):
    """获取指定城市的天气信息"""
    try:
        print(f"开始获取天气信息，城市: {city}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 先通过城市名称获取城市编码
            geo_url = "https://restapi.amap.com/v3/geocode/geo"
            geo_params = {
                "address": city,
                "key": AMAP_KEY
            }
            
            print(f"请求地理编码 URL: {geo_url}")
            print(f"地理编码参数: {geo_params}")
            
            geo_response = await client.get(geo_url, params=geo_params)
            print(f"地理编码响应状态码: {geo_response.status_code}")
            geo_data = geo_response.json()
            print(f"地理编码响应数据: {geo_data}")
            
            if geo_data["status"] == "1" and geo_data["geocodes"]:
                adcode = geo_data["geocodes"][0]["adcode"]
                
                # 使用城市编码获取天气信息
                weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
                weather_params = {
                    "city": adcode,
                    "key": AMAP_KEY,
                    "extensions": "base"
                }
                
                print(f"请求天气 URL: {weather_url}")
                print(f"天气请求参数: {weather_params}")
                
                weather_response = await client.get(weather_url, params=weather_params)
                print(f"天气API响应状态码: {weather_response.status_code}")
                weather_data = weather_response.json()
                print(f"天气API响应数据: {weather_data}")
                
                if weather_data["status"] == "1" and weather_data["lives"]:
                    live_weather = weather_data["lives"][0]
                    response_data = {
                        "code": 200,
                        "data": {
                            "city": city,
                            "temperature": live_weather["temperature"],
                            "weather": live_weather["weather"],
                            "windDirection": live_weather["winddirection"],
                            "windPower": live_weather["windpower"],
                            "humidity": live_weather["humidity"]
                        },
                        "message": "success"
                    }
                    print(f"处理后的返回数据: {response_data}")
                    return response_data
            
            print("未找到天气数据")
            raise HTTPException(status_code=404, detail="未找到该城市或天气信息")
                
    except httpx.TimeoutException:
        print("请求超时")
        raise HTTPException(status_code=504, detail="请求超时")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 