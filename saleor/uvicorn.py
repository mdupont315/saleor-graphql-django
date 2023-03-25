from uvicorn.workers import UvicornWorker as BaseUvicornWorker

class UvicornWorker(BaseUvicornWorker):
#    CONFIG_KWARGS = {"loop": "uvloop", "http": "httptools", "lifespan": "off"}
     CONFIG_KWARGS = {"loop": "asyncio", "http": "h11", "lifespan": "off", "forwarded_allow_ips":"*"}
