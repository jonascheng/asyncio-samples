import signal
import asyncio
import logging

########## Initial Logger ##########
logging.basicConfig(level=logging.INFO,
            format='[%(thread)d] %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
########################################

workers = 20
sleep = 3 # second

async def exit(loop, stop, signame):
    logger.info('got signal {}: exit'.format(signame))
    stop.set()
    this = asyncio.Task.current_task()
    tasks = asyncio.Task.all_tasks()
    # signal pending tasks to clean up except itself
    for task in tasks:
        if task is not this:
            task.cancel()
    # wait for pending tasks to clean up
    await asyncio.sleep(sleep)
    loop.stop()


async def producer(queue, stop):
    start = asyncio.get_event_loop().time()

    n = 0
    while stop.is_set() is False:
        n += 1
        item = str(n)
        logger.info('producing {}'.format(item))
        # Put an item into the queue. 
        # If the queue is full, wait until a free slot is available before adding item.
        try:
            await queue.put(item)
            # performance measurement
            processed = n - queue.qsize()            
            logger.info('rps = {}'.format(processed/(asyncio.get_event_loop().time()-start)))
        except asyncio.CancelledError:
            logger.info('producer is cancelled')
    logger.info('producer is stopped')


async def consumer(queue, stop, sem):
    while stop.is_set() is False:
        try:
            async with sem:
                # wait for an item from the producer
                item = await queue.get()
                logger.info('consuming {}'.format(item))
                # simulate i/o operation using sleep    
                await asyncio.sleep(sleep)
        except asyncio.CancelledError:
            logger.info('consumer is cancelled')
    logger.info('consumer is stopped')


def run_service():
    ev_loop = asyncio.get_event_loop()

    # create service stop event
    stop = asyncio.Event(loop=ev_loop)
    stop.clear()    # default false
    # create queue
    queue = asyncio.Queue(maxsize=100, loop=ev_loop)
    # create Semaphore
    sem = asyncio.Semaphore(workers)

    # add signal handler to stop the service
    for signame in ('SIGINT', 'SIGTERM'):
        ev_loop.add_signal_handler(getattr(signal, signame),
                                    lambda: asyncio.ensure_future(exit(ev_loop, stop, signame)))    
    try:
        # create producers
        asyncio.ensure_future(producer(queue, stop))
        # create consumers
        for _ in range(workers):
            asyncio.ensure_future(consumer(queue, stop, sem))
        
        logger.info('Event loop running forever, press CTRL+C to interrupt.')
        ev_loop.run_forever()
    finally:
        ev_loop.close()

    ev_loop.close()

if __name__ == '__main__':
    run_service()
