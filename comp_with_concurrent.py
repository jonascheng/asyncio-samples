import time
import asyncio
import logging
import concurrent.futures

########## Initial Logger ##########
logging.basicConfig(level=logging.INFO,
            format='[%(thread)d] %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
########################################

max_loop = 10 # benchmark loop
sleep = 1 # second

def benchmark(loop):
    def decorate(fn):
        def wrapped(*args, **kwargs):
            logger.info('benchmark {}'.format(fn.__name__))
            # start timer
            start = time.perf_counter()
            # execute time consuming tasks {loop} times
            for _ in range(loop):
                    fn(*args, **kwargs)
            # stop timer
            end = time.perf_counter()
            # calculate elapsed time
            diff = end - start
            logger.info('{} second elapsed to execute {}\n\n'.format(diff, fn.__name__))
        return wrapped
    return decorate


def blocking_sleep(): 
    time.sleep(sleep)
    logger.debug('blocking_sleep {} second'.format(sleep))


async def nonblocking_sleep():
    await asyncio.sleep(sleep)
    logger.debug('nonblocking_sleep {} second'.format(sleep))


@benchmark(loop=max_loop)
def sequencial_tasks(counts):
    for _ in range(counts):
        blocking_sleep()        


@benchmark(loop=max_loop)
def concurrent_tasks(counts):
    with concurrent.futures.ThreadPoolExecutor(max_workers=counts+1) as executor:
        for _ in range(counts):
            executor.submit( blocking_sleep )


@benchmark(loop=max_loop)
def asyncio_tasks(counts, ev_loop):
    futures = []
    for _ in range(counts):
        # Note: with close parentheses coroutine
        future = asyncio.ensure_future( nonblocking_sleep() )
        futures.append(future)
    ev_loop.run_until_complete(asyncio.wait(futures))


if __name__ == '__main__':
    ev_loop = asyncio.get_event_loop()

    # compare with sequencial tasks execution
    counts = 10
    sequencial_tasks(counts)
    concurrent_tasks(counts)
    asyncio_tasks(counts, ev_loop)

    # compare with concurrent tasks execution
    counts = 120
    concurrent_tasks(counts)
    asyncio_tasks(counts, ev_loop)

    ev_loop.close()
