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

limited_worker = 10
max_loop = 10 # benchmark loop
sleep = 1 # second

@benchmark(loop=max_loop)
def concurrent_tasks(counts):
    with concurrent.futures.ThreadPoolExecutor(max_workers=limited_worker) as executor:
        for _ in range(counts):
            executor.submit( blocking_sleep, sleep )


async def nonblocking_sleep_with_sem(sem, sleep):
    async with sem:
        await nonblocking_sleep(sleep)


@benchmark(loop=max_loop)
def asyncio_tasks(counts, ev_loop):
    # create instance of Semaphore
    sem = asyncio.Semaphore(limited_worker)

    futures = []
    for _ in range(counts):
        # Note: with close parentheses coroutine
        future = asyncio.ensure_future( nonblocking_sleep_with_sem(sem, sleep) )
        futures.append(future)
    ev_loop.run_until_complete(asyncio.wait(futures))


if __name__ == '__main__':
    ev_loop = asyncio.get_event_loop()

    # compare with concurrent tasks execution
    counts = limited_worker
    concurrent_tasks(counts)
    asyncio_tasks(counts, ev_loop)

    # compare with concurrent tasks execution
    counts = 120
    concurrent_tasks(counts)
    asyncio_tasks(counts, ev_loop)

    ev_loop.close()
