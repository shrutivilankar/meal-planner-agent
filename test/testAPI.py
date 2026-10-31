import httpx
import asyncio

async def test_generate_meal_plan():
    async with httpx.AsyncClient(timeout=3000) as client:
        resp = await client.post("http://127.0.0.1:8000/generate")
        resp.raise_for_status()
        print(resp.json())

asyncio.run(test_generate_meal_plan())