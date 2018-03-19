import asyncio
import logging
import concurrent.futures

from util import benchmark, blocking_sleep, nonblocking_sleep

########## Initial Logger ##########
logging.basicConfig(level=logging.INFO,
            format='[%(thread)d] %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
########################################

max_loop = 10 # benchmark loop
sleep = 1 # second

@benchmark(loop=max_loop)
def sequencial_tasks(counts):
    for _ in range(counts):
        blocking_sleep(sleep)        


@benchmark(loop=max_loop)
def concurrent_tasks(counts):
    with concurrent.futures.ThreadPoolExecutor(max_workers=counts) as executor:
        for _ in range(counts):
            executor.submit( blocking_sleep, sleep )


@benchmark(loop=max_loop)
def asyncio_tasks(counts, ev_loop):
    futures = []
    for _ in range(counts):
        # Note: with close parentheses coroutine
        future = asyncio.ensure_future( nonblocking_sleep(sleep) )
        futures.append(future)
    ev_loop.run_until_complete(asyncio.wait(futures))


if __name__ == '__main__':
    ev_loop = asyncio.get_event_loop()

    # compare with concurrent tasks execution
    counts = 10
    sequencial_tasks(counts)
    concurrent_tasks(counts)
    asyncio_tasks(counts, ev_loop)

    # compare with concurrent tasks execution
    counts = 120
    concurrent_tasks(counts)
    asyncio_tasks(counts, ev_loop)

    ev_loop.close()
