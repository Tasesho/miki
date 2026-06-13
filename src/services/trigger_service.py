from __future__ import annotations


DEFAULT_TRIGGERS = {
    "hola": "ola   (●'◡'●)",
    "xao": "Hasta la Proxima   (˶˃ ᵕ ˂˶) .ᐟ.ᐟ ",
    "miki": "que paso?  ( °ヮ° ) ? ",
    "persona": "Persona referencia?? ",
    "vc": "Unete al vc ╰┈➤[VC]➤",
    "lit": "literalmente bruh...",
    "xd": "lmao  (¬‿¬ )",
    "F": "F en el chat  (╯﹏╰）",
    "sad": "Todo va a estar bien...  (っ´ω`)ﾉ(╥ω╥)",
    "miedo": "Tranqui, yo te protejo  (ง'̀-'́)ง",
    "odio": "No digas eso, el odio es malo  (；￣Д￣)",
    "te amo": "Yo... yo tambien?  (*/ω＼*)",
    "ayuda": "Si necesitas algo, usa !ayuda  ( °∀°)o",
    "pancito": "Invita un poco!  (っ˘ڡ˘ς)",
    "cafe": "Un cafecito para seguir programando  ( ￣▽￣)旦",
    "uwu": "nwn  (✿◡‿◡)",
    "pog": "POGGERS  ( °o°) !!",
    "afk": "No te tardes mucho...  (◕‿◕)",
    "lag": "Es el internet o es el server?  (╯°□°)╯︵ ┻━┻",
    "gg": "GG WP!  (っಠ‿ಠ)っ",
    "basado": "Factores.  (⌐■_■)",
    "miau": "Nyaa~  (＾◡＾)",
    "clima": "Usa !clima si quieres saber de verdad  ( ﾟヮﾟ)",
}


class TriggerService:
    def __init__(self, guild_repository):
        self.guild_repository = guild_repository

    async def match_response(self, guild_id: int, content: str) -> str | None:
        triggers = await self.guild_repository.get_triggers(guild_id)
        if not triggers:
            triggers = DEFAULT_TRIGGERS

        normalized = content.lower()
        for key, response in triggers.items():
            if key in normalized:
                return response
        return None
