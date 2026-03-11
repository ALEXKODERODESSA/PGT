import websockets
import anyio
from rich.pretty import pprint as print
import json
import asyncio
import queue

SESSION = r'42["auth",{"session":"v0qccp36udau0i465cq9adappo","isDemo":1,"uid":33509895,"platform":1}]'

# Инициализация очереди для сигналов от бота
order_queue = queue.Queue()

async def websocket_client(url, pro, order_queue):
    while True:
        try:
            async with websockets.connect(
                url,
                extra_headers={
                    "Origin": "https://pocket-link19.co",
                    #"Origin": "https://po.trade/"
                },
            ) as websocket:
                async for message in websocket:
                    await pro(message, websocket, url, order_queue)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print(e)
            print("Connection lost... reconnecting")
            await anyio.sleep(5)
    return True


async def pro(message, websocket, url, order_queue):
    # if byte data
    if type(message) == bytes:
        decoded_data_1 = json.loads(message.decode('utf-8'))
        print(decoded_data_1)
        return
    else:
        print(message)

    if message.startswith('0{"sid":"'):
        print(f"{url.split('/')[2]} got 0 sid send 40 ")
        await websocket.send("40")
    elif message == "2":
        print(f"{url.split('/')[2]} got 2 send 3")
        await websocket.send("3")

    if message.startswith('40{"sid":"'):
        print(f"{url.split('/')[2]} got 40 sid send session")
        await websocket.send(SESSION)

    # Проверяем, есть ли данные о сделке от бота каждые 0.1 секунды
    while True:
        if not order_queue.empty():
            order_data = order_queue.get()
            print(f"Signal received: {order_data}, placing order...")
            await websocket.send(order_data)

        # Задержка 0.1 секунды перед следующей проверкой
        await asyncio.sleep(0.1)


async def main():
    # url = r'42["auth",{"session":"a:4:{s:10:\"session_id\";s:32:\"c53eec05c6f8a8be2d134d4fd55266f8\";s:10:\"ip_address\";s:14:\"46.138.176.190\";s:10:\"user_agent\";s:101:\"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\";s:13:\"last_activity\";i:1707850603;}9f383935faff5a86bc1658bbde8c61e7","isDemo":1,"uid":72038016,"platform":3}]'
    url = "wss://demo-api-eu.po.market/socket.io/?EIO=4&transport=websocket"
    # url = "wss://api-l.po.market/socket.io/?EIO=4&transport=websocket"
    await websocket_client(url, pro, order_queue)


if __name__ == "__main__":
    anyio.run(main)
