from aiohttp import ClientSession, TCPConnector
import asyncio
from nonebot.log import logger
from tenacity import wait_exponential, stop_after_attempt, retry_if_exception_type, retry
import time



class AsyncHashFetcher:
    """
    异步获取区块链节点哈希值的类
    """

    def __init__(self):
        """
        初始化类,创建连接池和并发控制信号量
        """
        self.sem = asyncio.Semaphore(10)  # 控制最大并发数为10
        self.session = None
        self.payload = {'jsonrpc': '2.0', 'method': 'eth_getBlockByNumber', 'params': ['latest', False], 'id': 1}
        self.endpoints = ['https://ethereum.publicnode.com', 'https://cloudflare-eth.com',
             'https://eth.rpc.blxrbdn.com', 'https://rpc.ankr.com/eth',
             'https://mainnet.infura.io/v3/8686668f975a439bb1c7b3739cd4289c',
             'https://white-lively-shard.discover.quiknode.pro/8e9697615c2c93706d58b6a65af7ce080e830831/',
             'https://virginia.rpc.blxrbdn.com', 'https://eth.llamarpc.com', 'https://eth-rpc.gateway.pokt.network']
        self.limit = 10

    async def __aenter__(self):
        self.session = ClientSession(connector=TCPConnector(limit=self.limit))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    @retry(retry=retry_if_exception_type(Exception),  # 重试所有异常
        stop=stop_after_attempt(3),  # 最多重试5次
        wait=wait_exponential(multiplier=1, min=2, max=6), # 重试间隔
    )  
    async def _get_hash(self, endpoint):
        """
        内部方法,获取指定节点的最新区块哈希值
        """
        try:    
            async with self.sem:
                async with self.session.post(endpoint, json=self.payload) as resp:     
                    data = await resp.json()            
                    return data['result']['hash'] 
        except Exception as e:
            logger.warning(f"Failed to get hash from {endpoint}")
            raise
    
    async def get_fastest_hash(self):
        """
        主要方法,从所有节点中获取最快返回的哈希结果
        超时或错误时取消任务,并继续尝试其他节点
        如果所有请求失败,抛出异常
        """
        tasks = [asyncio.create_task(self._get_hash(endpoint)) for endpoint in self.endpoints]
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=3)
        except asyncio.TimeoutError:
            logger.warning("All tasks timed out.")
            raise
        except Exception as e:
            logger.warning(f"Error while waiting for tasks: {str(e)}")
            raise

        # Cancel all pending tasks
        for task in pending:
            task.cancel()

        # Return the result of the first completed task
        for task in done:
            return task.result()

        
async def main():
    async with AsyncHashFetcher() as fetcher:
        hash_value = await fetcher.get_fastest_hash()
        print(hash_value)

if __name__ == "__main__":
    times = 10 
    while times > 1 :
        asyncio.run(main())
        times -=1
        time.sleep(50)