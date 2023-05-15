import discord, asyncio, time, requests
from discord.ext import commands

class app():
    def __init__(self, token, db) -> None:
        self.token = token
        self.db = db
        self.history_table = {}
        pass

    def run(self):
        self.intents = discord.Intents.all()
        self.client = commands.Bot(command_prefix='!', intents=self.intents)

        ########################--History command--########################

        #last command
        @self.client.command()
        async def hlast(ctx):
            await self.db.addHistory(ctx, "hlast command")
            result = await self.db.lastCommand()
            await ctx.send(result)

        #Vsearch by id
        @self.client.command()
        async def hid(ctx):
            try:
                await self.db.addHistory(ctx, "hid command")
                message_content = ctx.message.content.split("!hid ", 1)[1]
                try:
                    rows = await self.db.searchId(message_content)
                    page = 0
                    max_page = (len(rows) - 1) // 10
                    message = await ctx.send(embed=self.get_page_embed(rows, page))
                    await message.add_reaction("⬆️")
                    await message.add_reaction("⬇️")
                    def reaction_check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["⬆️", "⬇️"]
                    start_time = time.time()
                    while True:
                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=reaction_check)
                            if reaction.emoji == "⬆️":
                                page = max(page - 1, 0)
                            elif reaction.emoji == "⬇️":
                                page = min(page + 1, max_page)
                            await message.edit(embed=self.get_page_embed(rows, page))
                            await message.remove_reaction(reaction, user)
                        except asyncio.TimeoutError:
                            break
                    await message.clear_reactions()
                except:
                    await ctx.send("Bad user ID (example: 655023105923874842)")
            except:
                await ctx.send("Please provide a message to record.")
                return


        #search by username
        @self.client.command()
        async def huser(ctx):
            try:
                await self.db.addHistory(ctx, "huser command")
                message_content = ctx.message.content.split("!huser ", 1)[1]
                try:
                    rows = await self.db.searchUsername(message_content)
                    page = 0
                    max_page = (len(rows) - 1) // 10
                    message = await ctx.send(embed=self.get_page_embed(rows, page))
                    await message.add_reaction("⬆️")
                    await message.add_reaction("⬇️")
                    def reaction_check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["⬆️", "⬇️"]
                    while True:
                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=reaction_check)
                            if reaction.emoji == "⬆️":
                                page = max(page - 1, 0)
                            elif reaction.emoji == "⬇️":
                                page = min(page + 1, max_page)
                            await message.edit(embed=self.get_page_embed(rows, page))
                            await message.remove_reaction(reaction, user)
                        except asyncio.TimeoutError:
                            break
                    await message.clear_reactions()
                except:
                    await ctx.send("Bad username")
            except:
                await ctx.send("Please provide a message to record. (example : Naywvi#0970)")
                return
        
        #delete history
        @self.client.command()
        async def hdel(ctx):
            
            await self.db.deleteHistory()
            await self.db.addHistory(ctx, "hdel command")
            await ctx.send("hdel command")
        
        #View history
        @self.client.command()
        async def h(ctx):
            rows = await self.db.viewHistory()
            if not rows:
                await ctx.send("La table est vide.")
                return
            page = 0
            max_page = (len(rows) - 1) // 10
            message = await ctx.send(embed=self.get_page_embed(rows, page))
            await message.add_reaction("⬆️")
            await message.add_reaction("⬇️")
            def reaction_check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["⬆️", "⬇️"]
            while True:
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=reaction_check)
                    if reaction.emoji == "⬆️":
                        page = max(page - 1, 0)
                    elif reaction.emoji == "⬇️":
                        page = min(page + 1, max_page)
                    await message.edit(embed=self.get_page_embed(rows, page))
                    await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    print("stop")
                    break
            await message.clear_reactions()

        ########################--Fonctionality--########################
        
        #When a new user joins the server
        @self.client.event
        async def on_member_join(ctx):
            await self.db.addHistory(ctx, "new user")
            await self.client.get_channel(1097370667646722058).send("Welcome to the server !" + ctx.name)
        
        #save
        @self.client.event
        async def on_disconnect():
            # conversation = Conversation(ctx, self.history_table)
            # hashT = await conversation.histo(ctx, self.history_table)
            #print(self.history_table)
            self.db.saveConversation(self.history_table)
        
        #error gestion    
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("Invalid command")
        
        ########################--conversation--########################
        
        #helpp commande
        @self.client.command()
        async def speak(ctx):
            conversation = Conversation(ctx, self.history_table)
            await conversation.start()

        #reset conversation
        @self.client.command()
        async def reset(ctx):
            conversation = Conversation(ctx, self.history_table)
            await conversation.start()
            await conversation.reset()

        #start conversation bort
        @self.client.command()
        async def speaka(ctx, topic):
            conversation = Conversation(ctx, self.history_table)
            await conversation.speak_about(topic)

        #History conversation
        @self.client.command()
        async def ch(ctx):
            conversation = Conversation(ctx, self.history_table)
            histo = await conversation.histo(ctx, self.history_table)
            await ctx.send(histo)

        ########################--features 1--########################

        #Send joke command
        @self.client.command()
        async def joke(ctx):
            response = requests.get("https://v2.jokeapi.dev/joke/Any")
            if response.status_code == 200:
                data = response.json()
                await ctx.send(data['setup'])
            else:
                await ctx.send("no joke available")

        ########################--features 2--########################

        # Join the bot on the channel
        @self.client.command()
        async def join(ctx):
            if ctx.author.voice is None or ctx.author.voice.channel is None:
                await ctx.send("Vous devez d'abord rejoindre un channel vocal.")
                return

            channel = ctx.author.voice.channel
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            
            if voice_client and voice_client.is_connected():
                await voice_client.move_to(channel)
            else:
                voice_client = await channel.connect()
            
            await ctx.send(f"Connecté au channel vocal : {channel}")

        # Disconnect the bot
        @self.client.command()
        async def disconnect(ctx):
            if ctx.voice_client is None:
                await ctx.send("Je ne suis pas connecté à un channel vocal.")
                return

            await ctx.voice_client.disconnect()
            await ctx.send("Déconnecté du channel vocal.")

        # Start musique
        @self.client.command()
        async def start(ctx):
            if ctx.voice_client is None:
                await ctx.send("Je ne suis pas connecté à un channel vocal.")
                return

            if len(ctx.message.attachments) == 0:
                await ctx.send("Veuillez joindre un fichier audio à la commande.")
                return

            audio_file = ctx.message.attachments[0]

            if not audio_file.filename.endswith(('.mp3', '.wav')):
                await ctx.send("Le fichier attaché n'est pas un fichier audio valide.")
                return

            await audio_file.save(audio_file.filename)

            source = discord.FFmpegPCMAudio(audio_file.filename)
            ctx.voice_client.play(source)
            await ctx.send(f"Lecture de {audio_file.filename} démarrée.")

        # Pause musique
        @self.client.command()
        async def pause(ctx):
            if ctx.voice_client is None or not ctx.voice_client.is_playing():
                await ctx.send("Je ne suis pas en train de jouer de la musique.")
                return

            ctx.voice_client.pause()
            await ctx.send("Lecture de musique mise en pause.")
        
        # Continue musique
        @self.client.command()
        async def resume(ctx):
            if ctx.voice_client is None or not ctx.voice_client.is_paused():
                await ctx.send("La lecture de musique n'est pas en pause.")
                return

            ctx.voice_client.resume()
            await ctx.send("Reprise de la lecture de musique.")
        # Stop musique
        @self.client.command()
        async def stop(ctx):
            if ctx.voice_client is None or not ctx.voice_client.is_playing():
                await ctx.send("Je ne suis pas en train de jouer de la musique.")
                return

            ctx.voice_client.stop()
            await ctx.send("Arrêt de la lecture de musique.")

        #Run bot with token
        self.client.run(self.token)
        
    ########################--Return embed--########################
    def get_page_embed(self, rows, page):
        start = page * 10
        end = min(start + 10, len(rows))
        rows_on_page = rows[start:end]
        embed = discord.Embed(title="Historique", color=0x00ff00)
        for row in rows_on_page:
            embed.add_field(name=f"{row[0]} - {row[1]}", value=f"{row[2]}\n{row[3]} {row[4]} - {row[5]}")
        
        return embed

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

class Tree:
    def __init__(self, root):
        self.root = root

class Conversation:
    def __init__(self, ctx, history_table):
        self.ctx = ctx
        self.tree = None
        self.current_node = None
        self.history_table = history_table
        self.history = None
        
    async def histo(self,ctx,history_table):
        user_id = str(ctx.author.id)
        if user_id in history_table:
            user_history = history_table[user_id]
            return user_history
        else:
            return "nothing"
    
    async def start(self):
        self.tree = Tree(
            Node("Aimez-vous la viande ?", 
                 Node("Aimez-vous le poisson ?", 
                      Node("Aimez-vous le saumon ?"), 
                      Node("Aimez-vous la truite ?")
                 ),
                 Node("Aimez-vous les légumes ?", 
                      Node("Aimez-vous les carottes ?"),
                      Node("Aimez-vous les haricots verts ?")
                 )
            )
        )
        self.current_node = self.tree.root
        await self.ctx.send("Bonjour, je vais vous poser une série de questions pour mieux comprendre vos préférences alimentaires. Veuillez répondre par oui ou non.")
        await self.ask_question(self.current_node)
    
    async def ask_question(self, node):
        message = await self.ctx.send(node.value)
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        reaction, user = await self.ctx.bot.wait_for('reaction_add', check=lambda r, u: u == self.ctx.author and r.message.id == message.id and str(r.emoji) in ['👍', '👎'])
        if str(reaction.emoji) == '👍':
            if node.left:
                self.current_node = node.left
                await self.ask_question(node.left)
            else:
                await self.ctx.send("Nous vous recommandons de manger du saumon !")
        elif str(reaction.emoji) == '👎':
            if node.right:
                self.current_node = node.right
                await self.ask_question(node.right)
            else:
                await self.ctx.send("Nous vous recommandons de manger des haricots verts !")
        
        # Ajouter la commande à l'historique de l'utilisateur
        if self.history is None:
            self.history = []
        self.history.append(str(reaction.emoji))
        self.history_table[str(self.ctx.author.id)] = self.history
    
    async def reset(self):
        self.current_node = self.tree.root
        await self.ask_question(self.current_node)
    
    async def speak_about(self, topic):
        # Exemple de sujets traités par le bot : "python", "discord", "nourriture"
        topics = ["python", "discord", "nourriture"]
        if topic in topics:
            await self.ctx.send(f"Je peux parler de {topic}.")
        else:
            await self.ctx.send(f"Je ne connais pas {topic}.")

