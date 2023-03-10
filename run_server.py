import uvicorn
from MainServer.settings import settings

if __name__ == "__main__":
    uvicorn.run("MainServer.app:app",
                host=settings.server_host,
                port=settings.server_port,
                reload=True)