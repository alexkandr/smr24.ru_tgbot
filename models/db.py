import logging
import psycopg_pool

class DataBase:

    def __init__(self) -> None:
        self.logger = logging.getLogger('MainPgDB')

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataBase, cls).__new__(cls)
        return cls.instance

    async def connect(self, conninfo):
        """
    establishes connection to db
    
    Parameters
    ----------
    conninfo : connection string
    
    Returns
    ------- 
    None
        """
        self.logger.info('Establishing database connection')
        self.pool = psycopg_pool.AsyncNullConnectionPool(conninfo=conninfo)
        self.logger.info('db connected')
        await self.pool.open()
        await self.pool.wait()
        self.logger.info('pool opened')
    
        
    async def execute(self, command: str, factory = None, fetch: bool = False ):
        """
executes command to connected db

Parameters
----------
command : query to db
factory : row_factory for cursor
fetch : true if execution should return result of quer

Returns
------- 
None if fetch == False, else list of results. List of tuples if factory is None
        """
        pre_log_info = "Query to DATABASE:"
        for i in command.split('\n'):
            pre_log_info += ('\n\t' + i)
        self.logger.info(pre_log_info)
        

        async with self.pool.connection() as conn:
            async with conn.cursor(row_factory=factory) as cursor:
                await cursor.execute(command)
                result = None
                if fetch == True:
                    result = await cursor.fetchall() 
                    res_len=len(result)
                    if res_len !=1 :
                        post_log_info = f'list of {res_len} {type(result[0]) if res_len != 0 else "None"}'
                    else:
                        post_log_info = f'1 {type(result[0])} result: \n {result}'

                    post_log_info = 'Query returned ' + post_log_info
                    self.logger.info(post_log_info)
        
        return result
    
    async def close(self):
        await self.pool.close()


