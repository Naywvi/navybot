from _functions.info import *
from _functions.sqlite import *
from _app.app import *


import asyncio

class main:
    def __init__(self) -> None:
        asyncio.run(self.__ainit__())
        self.app.run()
        pass

    async def __ainit__(self):
        await self.initialisation()
        await self.db.checkDb()

    async def initialisation(self):
        self.info = informations()
        self.db = db(self.info)
        self.app = app(self.info.data['token'],self.db)
        

    
main()
