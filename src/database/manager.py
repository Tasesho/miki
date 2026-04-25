import aiosqlite
import os
from datetime import datetime
from pathlib import Path

class DBManager:
    def __init__(self, db_path="src/database/miki.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def init_db(self):
        """Inicializa la base de datos y crea las tablas"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    discord_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    fecha_registro TEXT NOT NULL,
                    xp INTEGER DEFAULT 0,
                    nivel INTEGER DEFAULT 1,
                    twitter TEXT,
                    github TEXT,
                    instagram TEXT,
                    website TEXT
                )
            """)
            await db.commit()
    
    async def get_usuario(self, discord_id):
        """Obtiene los datos de un usuario por su Discord ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM usuarios WHERE discord_id = ?", 
                (discord_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'discord_id': row[0],
                        'username': row[1],
                        'fecha_registro': row[2],
                        'xp': row[3],
                        'nivel': row[4],
                        'twitter': row[5],
                        'github': row[6],
                        'instagram': row[7],
                        'website': row[8]
                    }
                return None
    
    async def registrar_usuario(self, discord_id, username):
        """Registra un nuevo usuario en la BD"""
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO usuarios 
                   (discord_id, username, fecha_registro, xp, nivel)
                   VALUES (?, ?, ?, 0, 1)""",
                (discord_id, username, fecha_registro)
            )
            await db.commit()
    
    async def actualizar_xp(self, discord_id, xp_ganado):
        """Actualiza el XP de un usuario y verifica si sube de nivel"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT xp, nivel FROM usuarios WHERE discord_id = ?",
                (discord_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    xp_actual, nivel_actual = row
                    nuevo_xp = xp_actual + xp_ganado
                    xp_requerido = nivel_actual * 100
                    
                    nuevo_nivel = nivel_actual
                    while nuevo_xp >= xp_requerido:
                        nuevo_xp -= xp_requerido
                        nuevo_nivel += 1
                        xp_requerido = nuevo_nivel * 100
                    
                    await db.execute(
                        "UPDATE usuarios SET xp = ?, nivel = ? WHERE discord_id = ?",
                        (nuevo_xp, nuevo_nivel, discord_id)
                    )
                    await db.commit()
                    
                    subio_nivel = nuevo_nivel > nivel_actual
                    return {
                        'xp_actual': nuevo_xp,
                        'nivel_actual': nuevo_nivel,
                        'subio_nivel': subio_nivel,
                        'nivel_anterior': nivel_actual
                    }
    
    async def actualizar_redes(self, discord_id, twitter=None, github=None, instagram=None, website=None):
        """Actualiza las redes sociales de un usuario"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE usuarios 
                   SET twitter = ?, github = ?, instagram = ?, website = ?
                   WHERE discord_id = ?""",
                (twitter, github, instagram, website, discord_id)
            )
            await db.commit()


