import time
import asyncio
import logging

logger = logging.getLogger(__name__)

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
            logger.info('{} second elapsed to execute {}'.format(diff, fn.__name__))
            logger.info('{} second to execute {} in average\n'.format(diff/loop, fn.__name__))
        return wrapped
    return decorate

def blocking_sleep(sleep): 
    time.sleep(sleep)
    logger.debug('blocking_sleep {} second'.format(sleep))


async def nonblocking_sleep(sleep):
    await asyncio.sleep(sleep)
    logger.debug('nonblocking_sleep {} second'.format(sleep))
