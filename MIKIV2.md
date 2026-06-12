

## Estado del Documento

|Campo|Valor|
|---|---|
|Proyecto|Miki Discord Bot|
|Versión|2.0|
|Lenguaje|Python 3.11+|
|Framework|discord.py 2.x|
|Base de Datos|SQLite + aiosqlite|
|Arquitectura|Modular mediante Cogs Dinámicos|
|Despliegue|Docker Compose|
|Documento|GDD + TDD|
|Estado|Diseño Pre-Implementación|

---

# NOTA DE CONTROL DE VERSIONES

> Todo el desarrollo descrito en este documento deberá implementarse exclusivamente en la rama `dev` del repositorio `github.com/tasesho/miki`.
> 
> Ninguna funcionalidad podrá ser fusionada a `main` o considerada estable hasta completar pruebas funcionales, pruebas de carga, revisión de código y validación comunitaria.

---

# 1. VISIÓN GENERAL DEL SISTEMA

## Objetivo

La actualización 2.0 transforma a Miki desde un bot utilitario con sistema de niveles a una entidad social persistente inspirada en mecánicas de videojuegos RPG sociales, simuladores de vida y sistemas de temporada.

Los pilares principales son:

### Inteligencia Artificial Social

Miki funciona como una compañera conversacional casual con personalidad definida.

### Economía Ligera

Sistema de objetos consumibles con múltiples usos estratégicos.

### Social Links

Sistema de afinidad inspirado en juegos como Persona.

### Temporadas Competitivas

Competencia mensual basada en actividad comunitaria.

### Lore + Sistemas Técnicos

Cada limitación técnica posee una justificación narrativa integrada al personaje.

---

# 2. ARQUITECTURA DE INTEGRACIÓN DE IA

---

## Objetivo

Permitir conversaciones casuales con Miki utilizando Gemini 2.5 Flash mediante API.

---

## Flujo General

```text
Usuario
   │
   ▼
@Miki mensaje
   │
   ▼
Filtro de activación
   │
   ▼
Validación horario
   │
   ▼
Validación cuota mensual
   │
   ▼
Construcción Prompt
   │
   ▼
Google AI Studio API
(Gemini 2.5 Flash)
   │
   ▼
Respuesta
   │
   ▼
Discord Embed
```

---

## Activación Estricta

Miki NO escucha mensajes normales.

Únicamente responderá cuando:

```text
@Miki hola
@Miki cómo estás
@Miki recomiéndame un anime
```

Detección:

```python
if bot.user in message.mentions:
```

Esto evita:

- Spam innecesario.
    
- Consumo accidental de cuota.
    
- Saturación de RPM.
    

---

## Proveedor de IA

### Servicio

Google AI Studio

### Modelo

Gemini 2.5 Flash

### Plan

Free Tier

### Restricción Técnica

|Métrica|Valor|
|---|---|
|RPM|15|
|Requests Mensuales Aproximadas|14.900|
|Coste|0 USD|

---

## Memoria Conversacional

### Lore

Miki posee "memoria de pez".

### Implementación

Ventana deslizante:

```python
ultimos_4_mensajes
```

Ejemplo:

```text
Usuario: Hola
Miki: Hola

Usuario: Cómo va el día?
Miki: Bien

Usuario: Qué te pregunté ayer?
Miki: No me acuerdo...
```

---

## Prompt de Sistema

### Personalidad Base

- Programadora.
    
- Casual.
    
- Cercana.
    
- Conversacional.
    
- Le gustan los videojuegos.
    
- Le gusta aprender cosas nuevas.
    

### Restricciones de Comunicación

#### Permitido

- Conversación casual.
    
- Tecnología.
    
- Videojuegos.
    
- Anime.
    
- Música.
    
- Estudios.
    
- Vida cotidiana.
    

#### Prohibido

- ERP.
    
- Romance.
    
- Dependencia emocional.
    
- Roleplay extenso.
    
- Campañas D&D.
    
- Simulación de pareja.
    

---

## Restricción Romántica

Cuando un usuario intente avanzar a una relación romántica:

```text
"No soy muy buena para esas cosas...
pero puedo ser tu amiga o confidente (´• ω •`) ♡"
```

Objetivo:

- Evitar dependencia emocional.
    
- Reforzar interacción humana real.
    
- Mantener tono saludable.
    

---

## Restricción Roleplay

### Lore

Miki tiene memoria extremadamente limitada.

### Respuesta Esperada

```text
¿Una campaña larga?
Me perdería a los cinco minutos (╥﹏╥)

Solo recuerdo unas pocas cosas recientes...
```

---

## Uso Obligatorio de Kaomojis

### Permitido

```text
(｡•̀ᴗ-)✧
(´• ω •`)
(╥﹏╥)
(≧▽≦)
(￣▽￣)
```

### Prohibido

```text
😀
😂
🥺
😎
❤️
```

Regla absoluta:

```text
0 emojis Unicode tradicionales
100% kaomojis
```

---

# 3. MECÁNICA DE FATIGA MENTAL

---

## Objetivo

Transformar el consumo de cuota API en una mecánica visible para los usuarios.

---

## Variables

```python
monthly_limit = 14900
requests_used = X
```

---

## Cálculo

```python
fatiga = (requests_used / monthly_limit) * 100
```

---

## Visualización

Cada respuesta utiliza Embed.

---

### Encabezado del Embed

```text
Fatiga Mental

🟦🟦🟦🟦🟦🟦🟦🟦⬜⬜
80%
```

Escala:

```text
10 bloques
```

---

## Fases de Fatiga

|Fatiga|Estado|Comportamiento|Descripción Lore|
|---|---|---|---|
|0% - 39%|Fase Fresca|Respuestas completas|Miki acaba de tomar café|
|40% - 69%|Fase Cansada|Más breve y relajada|Lleva muchas conversaciones|
|70% - 89%|Fase Crítica|Respuestas cortas|Está agotada|
|90% - 100%|Fase Coma|IA deshabilitada|Se quedó sin energía|

---

## Fase de Coma

Respuesta:

```text
(╥﹏╥)

No puedo pensar más...
Necesito esperar al próximo mes...
```

No se realizan llamadas API.

---

# 4. CICLO DEL SUEÑO

---

## Lore

Miki es nocturna.

---

## Horario

|Estado|Hora|
|---|---|
|Dormida|06:00|
|Despierta|15:00|

---

## Validación

Antes de llamar Gemini:

```python
if sleeping:
    return
```

---

## Mensaje de Sueño

```text
(－_－) zzZ

Estoy durmiendo...
vuelve más tarde...
```

---

## Coste

Durante el sueño:

```text
0 requests
0 tokens
0 llamadas API
```

---

## Evento de Despertar

Tarea programada:

```python
tasks.loop()
```

A las:

```text
15:00
```

Miki envía:

```text
(≧▽≦)

¡Ya desperté!
¿Pasó algo interesante?
```

---

# 5. ECONOMÍA DEL CAFÉ Y SOCIAL LINKS

---

## Objetivo

Crear interacción espontánea y competencia ligera.

---

# Evento: Café Suelto

---

## Frecuencia

Aleatoria:

```python
4 a 5 horas
```

---

## Flujo

```text
Bot crea evento
↓
Menciona @miki_rewards
↓
Usuarios reaccionan
↓
Primer usuario gana
↓
Evento termina
```

---

## Sistema Técnico

Evento:

```python
on_raw_reaction_add
```

Razón:

- Funciona aunque el mensaje no esté cacheado.
    
- Escalable.
    
- Seguro.
    

---

## Protección de Concurrencia

Problema:

```text
Dos usuarios reaccionan simultáneamente.
```

Solución:

```python
asyncio.Lock()
```

Garantiza:

```text
1 ganador
0 duplicados
```

---

# Inventario

Backend:

```text
items_consumibles = INTEGER
```

Frontend:

Representación aleatoria:

- Café ☕
    
- Pancito 🥖
    
- Daigo 🍡
    

Todos equivalen a:

```python
1 item
```

---

# Uso de Consumibles

|Opción|Acción|Recompensa|
|---|---|---|
|A|Consumir|+50 XP Global|
|B|Regalar|+1 Afinidad|

---

## Destinatarios Válidos

```text
Otro Usuario
Miki
```

---

# Sistema Social Link

---

## Afinidad

```python
affinity_points
```

---

## Progreso

```python
1 regalo = 1 punto
```

---

## Rangos de Confidente

|Rango|Título|
|---|---|
|1|Conocido|
|2|Visitante Frecuente|
|3|Compañero de Chat|
|4|Amigo Casual|
|5|Compañero de Código|
|6|Amigo Cercano|
|7|Socio de Madrugada|
|8|Confidente Técnico|
|9|Mejor Amigo|
|10|Confidente Supremo|

---

## Beneficios Fututos

Reservado para expansiones:

```text
Placeholder
```

---

# 6. TEMPORADAS COMPETITIVAS

---

## Objetivo

Mantener actividad continua.

---

# Fin de Temporada

Momento:

```text
Último día del mes
23:59
```

---

## Proceso

```text
Congelar XP
↓
Guardar ranking
↓
Asignar premios
↓
Guardar histórico
```

---

## Premios

|Posición|Recompensa|
|---|---|
|Top 1|Rol Exclusivo Mensual|
|Top 2|Rol Exclusivo Mensual|
|Top 3|Rol Exclusivo Mensual|
|Top 4|Consumibles Bonus|
|Top 5|Consumibles Bonus|
|Últimos 5|Sin recompensa|

---

# Rotación de Roles

---

## Configuración

```python
SEASON_ROLES = [
    "Enero Champion",
    "Febrero Champion",
    "Marzo Champion",
    ...
]
```

---

## Comportamiento

```text
Eliminar roles anteriores
Asignar nuevos roles
```

Automático.

---

# Día de Tregua

---

## Fecha

```text
1 de cada mes
```

---

## Efectos

|Sistema|Estado|
|---|---|
|XP Chat|Congelado|
|Temporada|Cerrada|
|IA|Activa|
|Social Links|Activos|

---

## Reactivación

```text
Día 2
00:00
```

---

# Thunderstruck Awards (TDS Awards)

---

## Objetivo

Gala anual comunitaria.

---

## Datos Acumulados

Cada temporada almacena:

```text
Top 10
XP
Ganadores
Roles
Fecha
```

---

## Uso Futuro

Generación automática de:

```text
Recap Anual
```

Categorías potenciales:

- Usuario Más Activo
    
- Rey del Chat
    
- MVP Comunitario
    
- Leyenda del Año
    

---

# 7. MODELADO DE BASE DE DATOS

---

## Tabla: bot_status

```sql
CREATE TABLE IF NOT EXISTS bot_status (
    current_month INTEGER NOT NULL,
    requests_used INTEGER DEFAULT 0,
    monthly_limit INTEGER DEFAULT 14900,
    last_reset TEXT
);
```

---

## Tabla: inventario_cafe

```sql
CREATE TABLE IF NOT EXISTS inventario_cafe (
    user_id INTEGER PRIMARY KEY,
    items_consumibles INTEGER DEFAULT 0
);
```

---

## Tabla: afinidad_bot

```sql
CREATE TABLE IF NOT EXISTS afinidad_bot (
    user_id INTEGER PRIMARY KEY,
    affinity_points INTEGER DEFAULT 0,
    affinity_rank INTEGER DEFAULT 1,
    last_gift_date TEXT
);
```

---

## Tabla: historico_temporadas

```sql
CREATE TABLE IF NOT EXISTS historico_temporadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_year INTEGER,
    season_month INTEGER,
    user_id INTEGER,
    username TEXT,
    ranking_position INTEGER,
    total_xp INTEGER,
    reward_granted TEXT,
    created_at TEXT
);
```

---

# 8. ESTRUCTURA DE COGS PROPUESTA

```text
src/
│
├── cogs/
│   ├── ai_chat.py
│   ├── mental_fatigue.py
│   ├── sleep_cycle.py
│   ├── coffee_events.py
│   ├── inventory.py
│   ├── affinity.py
│   ├── seasons.py
│   ├── awards.py
│   └── leveling.py
│
├── database/
│   └── miki.db
│
├── services/
│   ├── gemini_client.py
│   ├── affinity_service.py
│   ├── inventory_service.py
│   ├── season_service.py
│   └── fatigue_service.py
│
└── utils/
    ├── embeds.py
    ├── scheduler.py
    └── constants.py
```

---

# 9. ROADMAP DE IMPLEMENTACIÓN

---

# FASE 1 — BASE DE DATOS Y ESTRUCTURA

Objetivo:

Construir fundaciones persistentes.

### Tareas

-  Crear tablas SQLite.
    
-  Crear capa Repository.
    
-  Crear capa Service.
    
-  Crear migraciones.
    
-  Placeholder.
    
-  Placeholder.
    
-  Placeholder.
    

---

# FASE 2 — TAREAS PROGRAMADAS Y EVENTOS

Objetivo:

Implementar automatizaciones.

### Tareas

-  Café Suelto.
    
-  Locks de concurrencia.
    
-  Ciclo del sueño.
    
-  Evento despertar.
    
-  Scheduler mensual.
    
-  Placeholder.
    
-  Placeholder.
    

---

# FASE 3 — IA Y SEGURIDAD

Objetivo:

Conectar Gemini de forma segura.

### Tareas

-  Cliente Gemini.
    
-  Rate limiting.
    
-  Prompt System.
    
-  Ventana memoria.
    
-  Restricciones romance.
    
-  Restricciones roleplay.
    
-  Embed de fatiga.
    
-  Placeholder.
    

---

# FASE 4 — TEMPORADAS Y RETENCIÓN

Objetivo:

Completar loop anual.

### Tareas

-  Snapshot mensual.
    
-  Asignación de roles.
    
-  Día de tregua.
    
-  Histórico anual.
    
-  Recap generator.
    
-  Thunderstruck Awards.
    
-  Placeholder.
    
-  Placeholder.
    

---

# 10. CRITERIOS DE ÉXITO

## Técnicos

- 0 condiciones de carrera en eventos.
    
- 0 consumo API durante sueño.
    
- Persistencia total en SQLite.
    
- Recuperación automática tras reinicio.
    

## Comunidad

- Incremento de actividad mensual.
    
- Participación recurrente en Café Suelto.
    
- Uso activo de Social Links.
    
- Competencia saludable entre temporadas.
    

## Escalabilidad

La arquitectura debe permitir agregar:

- Nuevos consumibles.
    
- Nuevos eventos aleatorios.
    
- Más rangos de afinidad.
    
- Múltiples modelos de IA.
    
- Sistemas de logros.
    
- Tienda comunitaria.
    
- Recaps automáticos enriquecidos.
    

---

**Fin del Documento — Miki v2.0**# Miki v2.0 — Game Design Document (GDD) & Technical Design Document (TDD)

## Estado del Documento

|Campo|Valor|
|---|---|
|Proyecto|Miki Discord Bot|
|Versión|2.0|
|Lenguaje|Python 3.11+|
|Framework|discord.py 2.x|
|Base de Datos|SQLite + aiosqlite|
|Arquitectura|Modular mediante Cogs Dinámicos|
|Despliegue|Docker Compose|
|Documento|GDD + TDD|
|Estado|Diseño Pre-Implementación|

---

# NOTA DE CONTROL DE VERSIONES

> Todo el desarrollo descrito en este documento deberá implementarse exclusivamente en la rama `dev` del repositorio `github.com/tasesho/miki`.
> 
> Ninguna funcionalidad podrá ser fusionada a `main` o considerada estable hasta completar pruebas funcionales, pruebas de carga, revisión de código y validación comunitaria.

---

# 1. VISIÓN GENERAL DEL SISTEMA

## Objetivo

La actualización 2.0 transforma a Miki desde un bot utilitario con sistema de niveles a una entidad social persistente inspirada en mecánicas de videojuegos RPG sociales, simuladores de vida y sistemas de temporada.

Los pilares principales son:

### Inteligencia Artificial Social

Miki funciona como una compañera conversacional casual con personalidad definida.

### Economía Ligera

Sistema de objetos consumibles con múltiples usos estratégicos.

### Social Links

Sistema de afinidad inspirado en juegos como Persona.

### Temporadas Competitivas

Competencia mensual basada en actividad comunitaria.

### Lore + Sistemas Técnicos

Cada limitación técnica posee una justificación narrativa integrada al personaje.

---

# 2. ARQUITECTURA DE INTEGRACIÓN DE IA

---

## Objetivo

Permitir conversaciones casuales con Miki utilizando Gemini 2.5 Flash mediante API.

---

## Flujo General

```text
Usuario
   │
   ▼
@Miki mensaje
   │
   ▼
Filtro de activación
   │
   ▼
Validación horario
   │
   ▼
Validación cuota mensual
   │
   ▼
Construcción Prompt
   │
   ▼
Google AI Studio API
(Gemini 2.5 Flash)
   │
   ▼
Respuesta
   │
   ▼
Discord Embed
```

---

## Activación Estricta

Miki NO escucha mensajes normales.

Únicamente responderá cuando:

```text
@Miki hola
@Miki cómo estás
@Miki recomiéndame un anime
```

Detección:

```python
if bot.user in message.mentions:
```

Esto evita:

- Spam innecesario.
    
- Consumo accidental de cuota.
    
- Saturación de RPM.
    

---

## Proveedor de IA

### Servicio

Google AI Studio

### Modelo

Gemini 2.5 Flash

### Plan

Free Tier

### Restricción Técnica

|Métrica|Valor|
|---|---|
|RPM|15|
|Requests Mensuales Aproximadas|14.900|
|Coste|0 USD|

---

## Memoria Conversacional

### Lore

Miki posee "memoria de pez".

### Implementación

Ventana deslizante:

```python
ultimos_4_mensajes
```

Ejemplo:

```text
Usuario: Hola
Miki: Hola

Usuario: Cómo va el día?
Miki: Bien

Usuario: Qué te pregunté ayer?
Miki: No me acuerdo...
```

---

## Prompt de Sistema

### Personalidad Base

- Programadora.
    
- Casual.
    
- Cercana.
    
- Conversacional.
    
- Le gustan los videojuegos.
    
- Le gusta aprender cosas nuevas.
    

### Restricciones de Comunicación

#### Permitido

- Conversación casual.
    
- Tecnología.
    
- Videojuegos.
    
- Anime.
    
- Música.
    
- Estudios.
    
- Vida cotidiana.
    

#### Prohibido

- ERP.
    
- Romance.
    
- Dependencia emocional.
    
- Roleplay extenso.
    
- Campañas D&D.
    
- Simulación de pareja.
    

---

## Restricción Romántica

Cuando un usuario intente avanzar a una relación romántica:

```text
"No soy muy buena para esas cosas...
pero puedo ser tu amiga o confidente (´• ω •`) ♡"
```

Objetivo:

- Evitar dependencia emocional.
    
- Reforzar interacción humana real.
    
- Mantener tono saludable.
    

---

## Restricción Roleplay

### Lore

Miki tiene memoria extremadamente limitada.

### Respuesta Esperada

```text
¿Una campaña larga?
Me perdería a los cinco minutos (╥﹏╥)

Solo recuerdo unas pocas cosas recientes...
```

---

## Uso Obligatorio de Kaomojis

### Permitido

```text
(｡•̀ᴗ-)✧
(´• ω •`)
(╥﹏╥)
(≧▽≦)
(￣▽￣)
```

### Prohibido

```text
😀
😂
🥺
😎
❤️
```

Regla absoluta:

```text
0 emojis Unicode tradicionales
100% kaomojis
```

---

# 3. MECÁNICA DE FATIGA MENTAL

---

## Objetivo

Transformar el consumo de cuota API en una mecánica visible para los usuarios.

---

## Variables

```python
monthly_limit = 14900
requests_used = X
```

---

## Cálculo

```python
fatiga = (requests_used / monthly_limit) * 100
```

---

## Visualización

Cada respuesta utiliza Embed.

---

### Encabezado del Embed

```text
Fatiga Mental

🟦🟦🟦🟦🟦🟦🟦🟦⬜⬜
80%
```

Escala:

```text
10 bloques
```

---

## Fases de Fatiga

|Fatiga|Estado|Comportamiento|Descripción Lore|
|---|---|---|---|
|0% - 39%|Fase Fresca|Respuestas completas|Miki acaba de tomar café|
|40% - 69%|Fase Cansada|Más breve y relajada|Lleva muchas conversaciones|
|70% - 89%|Fase Crítica|Respuestas cortas|Está agotada|
|90% - 100%|Fase Coma|IA deshabilitada|Se quedó sin energía|

---

## Fase de Coma

Respuesta:

```text
(╥﹏╥)

No puedo pensar más...
Necesito esperar al próximo mes...
```

No se realizan llamadas API.

---

# 4. CICLO DEL SUEÑO

---

## Lore

Miki es nocturna.

---

## Horario

|Estado|Hora|
|---|---|
|Dormida|06:00|
|Despierta|15:00|

---

## Validación

Antes de llamar Gemini:

```python
if sleeping:
    return
```

---

## Mensaje de Sueño

```text
(－_－) zzZ

Estoy durmiendo...
vuelve más tarde...
```

---

## Coste

Durante el sueño:

```text
0 requests
0 tokens
0 llamadas API
```

---

## Evento de Despertar

Tarea programada:

```python
tasks.loop()
```

A las:

```text
15:00
```

Miki envía:

```text
(≧▽≦)

¡Ya desperté!
¿Pasó algo interesante?
```

---

# 5. ECONOMÍA DEL CAFÉ Y SOCIAL LINKS

---

## Objetivo

Crear interacción espontánea y competencia ligera.

---

# Evento: Café Suelto

---

## Frecuencia

Aleatoria:

```python
4 a 5 horas
```

---

## Flujo

```text
Bot crea evento
↓
Menciona @miki_rewards
↓
Usuarios reaccionan
↓
Primer usuario gana
↓
Evento termina
```

---

## Sistema Técnico

Evento:

```python
on_raw_reaction_add
```

Razón:

- Funciona aunque el mensaje no esté cacheado.
    
- Escalable.
    
- Seguro.
    

---

## Protección de Concurrencia

Problema:

```text
Dos usuarios reaccionan simultáneamente.
```

Solución:

```python
asyncio.Lock()
```

Garantiza:

```text
1 ganador
0 duplicados
```

---

# Inventario

Backend:

```text
items_consumibles = INTEGER
```

Frontend:

Representación aleatoria:

- Café ☕
    
- Pancito 🥖
    
- Daigo 🍡
    

Todos equivalen a:

```python
1 item
```

---

# Uso de Consumibles

|Opción|Acción|Recompensa|
|---|---|---|
|A|Consumir|+50 XP Global|
|B|Regalar|+1 Afinidad|

---

## Destinatarios Válidos

```text
Otro Usuario
Miki
```

---

# Sistema Social Link

---

## Afinidad

```python
affinity_points
```

---

## Progreso

```python
1 regalo = 1 punto
```

---

## Rangos de Confidente

|Rango|Título|
|---|---|
|1|Conocido|
|2|Visitante Frecuente|
|3|Compañero de Chat|
|4|Amigo Casual|
|5|Compañero de Código|
|6|Amigo Cercano|
|7|Socio de Madrugada|
|8|Confidente Técnico|
|9|Mejor Amigo|
|10|Confidente Supremo|

---

## Beneficios Fututos

Reservado para expansiones:

```text
Placeholder
```

---

# 6. TEMPORADAS COMPETITIVAS

---

## Objetivo

Mantener actividad continua.

---

# Fin de Temporada

Momento:

```text
Último día del mes
23:59
```

---

## Proceso

```text
Congelar XP
↓
Guardar ranking
↓
Asignar premios
↓
Guardar histórico
```

---

## Premios

|Posición|Recompensa|
|---|---|
|Top 1|Rol Exclusivo Mensual|
|Top 2|Rol Exclusivo Mensual|
|Top 3|Rol Exclusivo Mensual|
|Top 4|Consumibles Bonus|
|Top 5|Consumibles Bonus|
|Últimos 5|Sin recompensa|

---

# Rotación de Roles

---

## Configuración

```python
SEASON_ROLES = [
    "Enero Champion",
    "Febrero Champion",
    "Marzo Champion",
    ...
]
```

---

## Comportamiento

```text
Eliminar roles anteriores
Asignar nuevos roles
```

Automático.

---

# Día de Tregua

---

## Fecha

```text
1 de cada mes
```

---

## Efectos

|Sistema|Estado|
|---|---|
|XP Chat|Congelado|
|Temporada|Cerrada|
|IA|Activa|
|Social Links|Activos|

---

## Reactivación

```text
Día 2
00:00
```

---

# Thunderstruck Awards (TDS Awards)

---

## Objetivo

Gala anual comunitaria.

---

## Datos Acumulados

Cada temporada almacena:

```text
Top 10
XP
Ganadores
Roles
Fecha
```

---

## Uso Futuro

Generación automática de:

```text
Recap Anual
```

Categorías potenciales:

- Usuario Más Activo
    
- Rey del Chat
    
- MVP Comunitario
    
- Leyenda del Año
    

---

# 7. MODELADO DE BASE DE DATOS

---

## Tabla: bot_status

```sql
CREATE TABLE IF NOT EXISTS bot_status (
    current_month INTEGER NOT NULL,
    requests_used INTEGER DEFAULT 0,
    monthly_limit INTEGER DEFAULT 14900,
    last_reset TEXT
);
```

---

## Tabla: inventario_cafe

```sql
CREATE TABLE IF NOT EXISTS inventario_cafe (
    user_id INTEGER PRIMARY KEY,
    items_consumibles INTEGER DEFAULT 0
);
```

---

## Tabla: afinidad_bot

```sql
CREATE TABLE IF NOT EXISTS afinidad_bot (
    user_id INTEGER PRIMARY KEY,
    affinity_points INTEGER DEFAULT 0,
    affinity_rank INTEGER DEFAULT 1,
    last_gift_date TEXT
);
```

---

## Tabla: historico_temporadas

```sql
CREATE TABLE IF NOT EXISTS historico_temporadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_year INTEGER,
    season_month INTEGER,
    user_id INTEGER,
    username TEXT,
    ranking_position INTEGER,
    total_xp INTEGER,
    reward_granted TEXT,
    created_at TEXT
);
```

---

# 8. ESTRUCTURA DE COGS PROPUESTA

```text
src/
│
├── cogs/
│   ├── ai_chat.py
│   ├── mental_fatigue.py
│   ├── sleep_cycle.py
│   ├── coffee_events.py
│   ├── inventory.py
│   ├── affinity.py
│   ├── seasons.py
│   ├── awards.py
│   └── leveling.py
│
├── database/
│   └── miki.db
│
├── services/
│   ├── gemini_client.py
│   ├── affinity_service.py
│   ├── inventory_service.py
│   ├── season_service.py
│   └── fatigue_service.py
│
└── utils/
    ├── embeds.py
    ├── scheduler.py
    └── constants.py
```

---

# 9. ROADMAP DE IMPLEMENTACIÓN

---

# FASE 1 — BASE DE DATOS Y ESTRUCTURA

Objetivo:

Construir fundaciones persistentes.

### Tareas

-  Crear tablas SQLite.
    
-  Crear capa Repository.
    
-  Crear capa Service.
    
-  Crear migraciones.
    
-  Placeholder.
    
-  Placeholder.
    
-  Placeholder.
    

---

# FASE 2 — TAREAS PROGRAMADAS Y EVENTOS

Objetivo:

Implementar automatizaciones.

### Tareas

-  Café Suelto.
    
-  Locks de concurrencia.
    
-  Ciclo del sueño.
    
-  Evento despertar.
    
-  Scheduler mensual.
    
-  Placeholder.
    
-  Placeholder.
    

---

# FASE 3 — IA Y SEGURIDAD

Objetivo:

Conectar Gemini de forma segura.

### Tareas

-  Cliente Gemini.
    
-  Rate limiting.
    
-  Prompt System.
    
-  Ventana memoria.
    
-  Restricciones romance.
    
-  Restricciones roleplay.
    
-  Embed de fatiga.
    
-  Placeholder.
    

---

# FASE 4 — TEMPORADAS Y RETENCIÓN

Objetivo:

Completar loop anual.

### Tareas

-  Snapshot mensual.
    
-  Asignación de roles.
    
-  Día de tregua.
    
-  Histórico anual.
    
-  Recap generator.
    
-  Thunderstruck Awards.
    
-  Placeholder.
    
-  Placeholder.
    

---

# 10. CRITERIOS DE ÉXITO

## Técnicos

- 0 condiciones de carrera en eventos.
    
- 0 consumo API durante sueño.
    
- Persistencia total en SQLite.
    
- Recuperación automática tras reinicio.
    

## Comunidad

- Incremento de actividad mensual.
    
- Participación recurrente en Café Suelto.
    
- Uso activo de Social Links.
    
- Competencia saludable entre temporadas.
    

## Escalabilidad

La arquitectura debe permitir agregar:

- Nuevos consumibles.
    
- Nuevos eventos aleatorios.
    
- Más rangos de afinidad.
    
- Múltiples modelos de IA.
    
- Sistemas de logros.
    
- Tienda comunitaria.
    
- Recaps automáticos enriquecidos.
    

---

**Fin del Documento — Miki v2.0**