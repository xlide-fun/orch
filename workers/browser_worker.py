# Alias to queue_worker for browser tier
from queue_worker import worker_loop
import asyncio

if __name__ == "__main__":
    asyncio.run(worker_loop())
