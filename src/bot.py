import discord
from discord.ext import commands
from collections import Counter
import os
from config import TOKEN

class MikiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # carga de modulos
        for filename in os.listdir("./src/modules"):
            if filename.endswith(".py") and filename != "__init__.py":
                await self.load_extension(f'modules.{filename[:-3]}')
                print(f" Módulo '{filename}' cargado exitosamente.")
bot = MikiBot()
bot.run(TOKEN)


# Cargar variables de entorno desde .env
load_dotenv()

# Obtener el token de las variables de entorno
TOKEN = os.getenv("DISCORD_TOKEN1")

# Activar intents
intents = discord.Intents.default()
intents.message_content = True

#Lista de saludos para @bot.command talk
saludos=[
    "¡Hola!",
    "¡Saludos! Espero que tengas un buen día.",
    "¡Ey! ¿Qué andas haciendo?",
    "¡Hey! Me alegra verte por aquí.",
]
bot = commands.Bot(command_prefix="!", intents=intents)


async def triggers(message):
    """maneja los triggers y responde con el mensaje necesario"""
    triggers ={
        "hola": "ola   (●'◡'●)",
        "xao": "Hasta la Proxima   (˶˃ ᵕ ˂˶) .ᐟ.ᐟ ",
        "miki": "que paso?  ( °ヮ° ) ? ",
        "persona": "Persona referencia?? ",
        "vc": "Unete al vc ╰┈➤🔊-vc-➤",
        "lit":"literalmente bruh...",
        "xd":"porque el desagrado? (╥﹏╥)",
        "freaky":"𝓯𝓻𝓮𝓪𝓴𝔂",
    }
    
    mensaje_usuario = message.content.lower()
    for key, response in triggers.items():
        if key in mensaje_usuario:
            await message.channel.send(response)
            break    #cuando encuentra 1 coincidencia se detiene

#bot events

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_message(message):
    """Responde automaticamente si el mensaje contiene palabras clave"""
    
    if message.author == bot.user: 
        return   #evita que el bot se reponda a si mismo


    await triggers(message)

    await bot.process_commands(message)

#bot commands
@bot.command()
async def talk(ctx):
    """Comando que responde con un saludo aleatorio"""
    respuesta= random.choice(saludos)
    await ctx.send(respuesta)

@bot.command()
async def presentarse(ctx):
    """Comando que responde con la presentacion del bot""" 
    embed= discord.Embed(
        title="¡Hola a todos! (˶˃ ᵕ ˂˶) .ᐟ.ᐟ ",
        description=f"Soy **Miki**, un bot creado por {ctx.author.mention}. Estoy aquí para darle más vida al chat. ¡Un gusto conocerlos!",
        color=discord.Color.pink()
    )
    embed.set_footer(text="¡Usa !ayuda para ver mis comandos!")

    await ctx.send(embed=embed)


@bot.command()
async def say(ctx, *, mensaje: str):
    """Repite el mensaje del usuario"""
    await ctx.send(mensaje)

@bot.command()
async def gravity(ctx):
    """Muestra un mensaje sobre gravedad y un GIF"""
    gif_url = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExejJ0ZHZqbHVtbWlsajl4aW9ncGZ4cXBzdTZxaDJhb3NtZ2xud3YwbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l46CqLVMWzaJUFPLW/giphy.gif"  # Aquí puedes poner el enlace del GIF
    embed = discord.Embed(title="   ", description=" Graveda' 🗣️🔥", color=discord.Color.blue())
    embed.set_image(url=gif_url)  # Inserta el GIF en el embed
    await ctx.send(embed=embed)


@bot.command()
async def historial(ctx):
    """comando que muestra las palabas mas repetidas en el canal"""
    

    canal=ctx.channel
    mensajes = []
    
    async for mensaje in canal.history(limit=100):
        mensajes.append(mensaje.content.lower())
    
    palabras= []

    for texto in mensajes:
        
        texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚüñ\s]", "", texto)
        palabras.extend(texto.split())
  
    contador = Counter(palabras)

    resultado = "Palabras mas repetidas: \n  (debido a temas de optimizacion el comando esta limitado a 100 mensajes) \n"
    for palabra, cantidad in contador.most_common(10):
        resultado += f"{palabra}: {cantidad}\n"
    
    await ctx.send(resultado)

@bot.command()
async def clima(ctx, ciudad, pais):
    """Muestra el clima/tiempo de una zona especifica"""     #se usa como: !clima santiago chile --> 32 grados 20%humedad
    api_key= os.getenv("WEATHER_API_KEY")     #guarda la API key en un archivo .env para evitar comprometer la key del bot
    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={ciudad},{pais}'

    respuesta = requests.get(url)

    if respuesta.status_code== 200:
        datos=respuesta.json()
        temp = datos["current"]["temp_c"]
        humedad = datos["current"]["humidity"]
        condicion = datos["current"]["condition"]["text"]

        mensaje = f"🌍 **Ciudad:** {ciudad.title()}\n🌡️ **Temperatura:** {temp}°C\n💧 **Humedad:** {humedad}%\n☁️ **Condición:** {condicion}"
    else:
        mensaje = "❌ No se encontró la ciudad. Intenta con otro nombre."

    await ctx.send(mensaje)


@bot.command()
async def gif(ctx, *, query:str):
    """Busca un gif usando la api de giphy"""

    api_key=os.getenv("GIPHY_API_KEY")     #obtiene la API key desde .env

    url= f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=1&lang=es"   

    response= requests.get(url)

    if response.status_code ==200:
        data = response.json()


        if data['data']:                #si encuentra algun gif envia el primero que encuentra
            gif_url = data['data'][0]['images']['original']['url']
            
            
            embed = discord.Embed(
                title= f"GIF para: {query.title()}",
                description=f"TOma GIF 👊👊!! '{query.title()}'",
                color=discord.Color.red()
            )
            embed.set_image(url=gif_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No se encontraron GIFs para esa búsqueda.")     
    else:
        await ctx.send( "Hubo un problema con la búsqueda del GIF. Intenta nuevamente.")

@bot.command()
async def ayuda(ctx):
    """Muestra los comandos disponibles del bot"""
    respuesta = """```
Comandos disponibles:
- !gif        - Responde con un gif relacionado (Ex: !gif <anime>  busca gif anime)
- !clima      - Busca clima para la region  (!clima <Ciudad><Pais>)
- !historial  - Muestra las 10 palabras más repetidas en los últimos 100 mensajes.
- !say        - Repite el mensaje de un usuario.
- !gravity    - graveda' .
- !presentarse - La presentación del bot.
- !talk       - Saludo.
- !ayuda      - Muestra esta lista de comandos.
También cuento con una variedad de triggers, ¡así que habla para descubrirlos!
```"""
    await ctx.send(respuesta)

# Ejecutar el bot
print("Token leído:", TOKEN)  # Agrega esto temporalmente
print("Bot versión 1.1.0")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: No se encontró el token en el archivo .env")
