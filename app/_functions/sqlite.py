import sqlite3, os.path, datetime
class db:
    def __init__(self,info) -> None:
        self.dbName = info.data['name_database'] + ".db"
        self.dbPath = info.data['path_database']
        self.fullPath = self.dbPath + self.dbName
        self.page = 0
        pass
    
    async def checkDb(self):
        print("[ + ] - Loading database.") if os.path.exists(self.fullPath) else await self.generateDb()
    
    async def open(self):
        self.now = datetime.datetime.now()
        self.hours = self.now.strftime("%H:%M:%S")
        self.day = self.now.strftime("%d/%m/%Y")
        self.conn = sqlite3.connect(self.fullPath)
        self.cur = self.conn.cursor()
    
    async def close(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()
    
    async def generateDb(self):
        with open(self.fullPath, 'x'):
            pass
        
        await self.open()
        await self.cur.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, username TEXT, id_user INTEGER, date DATE, hours TEXT, reason TEXT)')
        await self.cur.execute('CREATE TABLE IF NOT EXISTS conversation (id INTEGER PRIMARY KEY, id_user INTEGER, conversation TEXT)')
        await self.close()

        print("[ ! ] - New database successfully created at ' {} ' .".format(self.fullPath))
    
    async def saveConversation(self,hashT):
        await self.open()
        for key, value in hashT.items():
            for command in value:
                self.cur.execute('INSERT INTO conversation (id_user, conversation) VALUES ({}, \'{}\')'.format(key, command)) 
        await self.close()

    async def addHistory(self,ctx,reason):
        await self.open()
        self.cur.execute('INSERT INTO history (username, id_user, date, hours ,reason) VALUES (\'{}\', {}, \'{}\', \'{}\', \'{}\')'.format(ctx.author, ctx.author.id, self.day, self.hours, reason)) 
        await self.close()

    async def lastCommand(self):
        await self.open()
        self.cur.execute('SELECT * FROM history ORDER BY id DESC LIMIT 1') 
        last_row = self.cur.fetchone()
        await self.close()
        return last_row
            
    async def deleteHistory(self):
        await self.open()
        self.cur.execute('DELETE FROM history') 
        await self.close()
    
    async def searchId(self,userid):
        try:
            await self.open()
            self.cur.execute('SELECT * FROM history WHERE id_user = {}'.format(userid)) 
            rows = self.cur.fetchall()
            result = []
            for row in rows:
                result.append(row)
            await self.close()
        except:
            result = False
        return result
    
    async def searchUsername(self,username):
            try:
                await self.open()
                self.cur.execute('SELECT * FROM history WHERE username = \'{}\''.format(username)) 
                rows = self.cur.fetchall()
                result = []
                for row in rows:
                    result.append(row)
                await self.close()
            except:
                result = ""
            return result
    
    async def viewHistory(self):
        await self.open()
        self.cur.execute('SELECT * FROM history')
        rows = self.cur.fetchall()
        result = []
        for row in rows:
            result.append(row)
        await self.close()
        return result