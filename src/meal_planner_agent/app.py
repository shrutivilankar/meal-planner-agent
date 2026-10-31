import asyncio, uvicorn
from bot import create_bot_app
from api import app
from dotenv import load_dotenv
load_dotenv()

async def main():

    uvicorn_config = uvicorn.Config(app, host="localhost", port=8000)
    server = uvicorn.Server(uvicorn_config)
    server_task = asyncio.create_task(server.serve())

    bot_app = create_bot_app()
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    await server_task


if __name__ == "__main__":
    asyncio.run(main())