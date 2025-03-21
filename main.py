import uvicorn
from api.app import app
import logging
import multiprocessing

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    

    uvicorn.run(
        "api.app:app", 
        host="localhost",
        port=8000, 
        reload=True,
        workers=1,
        log_level="debug",
        timeout_keep_alive=60
    )