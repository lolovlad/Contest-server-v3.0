import uvicorn
from MainServer.settings import settings
from MainServer.app import app

if __name__ == "__main__":
    uvicorn.run(app,
                host=settings.server_host,
                port=settings.server_port)