"""ARQ Worker 入口"""
# import os
# import sys
# import asyncio

# if sys.platform == "win32":
#     sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from kk.services.run_worker import WorkerSettings

__all__ = ["WorkerSettings"]