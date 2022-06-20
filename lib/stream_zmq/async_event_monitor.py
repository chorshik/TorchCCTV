import zmq
from zmq.utils.monitor import parse_monitor_message
import asyncio
from typing import Any, Dict
import time

from lib.stream_zmq.utils import line


async def event_monitor(monitor):
    EVENT_MAP = {}
    # print("Event names:")
    for name in dir(zmq):
        if name.startswith('EVENT_'):
            value = getattr(zmq, name)
            # print("%21s : %4i" % (name, value))
            EVENT_MAP[value] = name

    print("\n")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_loop() -> None:
        while True:
            try:
                while monitor.poll():
                    evt: Dict[str, Any] = {}
                    msg = await monitor.recv_multipart(flags=0)
                    mon_evt = parse_monitor_message(msg)
                    evt.update(mon_evt)
                    evt['description'] = EVENT_MAP[evt['event']]
                    print(f"Event: {evt}")
                    line()
                    if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
                        break
            except RuntimeError as e:
                print(e)
                time.sleep(1)

        monitor.close()
        print()
        print("event monitor thread done!")

    asyncio.ensure_future(run_loop())
