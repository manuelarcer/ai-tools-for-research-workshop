---
title: Instalación y configuración de opencode
dia: 1
deck: false
last_reviewed: 2026-08-30
---

## Antes de empezar

**Necesitas tres cosas antes de que empiece el taller.**

- Una laptop con permiso para instalar software (si es de tu empresa o universidad, confirma con IT antes del día del taller).
- Python 3.11 o más reciente.
- Una conexión a internet.

Este documento cubre la instalación de opencode en macOS y en Windows, la configuración del modelo que vamos a usar en el taller, cómo instalar un skill, y cómo confirmar que todo quedó funcionando. Si algo no coincide con lo que ves en tu pantalla, la referencia definitiva es siempre `https://opencode.ai/docs/`.

## Instalar opencode en macOS

**Un solo comando instala opencode en macOS.**

```bash
brew install anomalyco/tap/opencode
```

Si no usas Homebrew, la alternativa multiplataforma (requiere Node.js) es:

```bash
npm install -g opencode-ai
```

Después de instalar, opencode guarda su configuración en:

```
~/.config/opencode/opencode.json
```

No necesitas crear ni editar ese archivo a mano todavía — lo vamos a tocar en la sección "Configurar el modelo".

## Instalar opencode en Windows

**Es la misma herramienta, instalada por Chocolatey o por npm.**

```bash
choco install opencode
```

o, si prefieres la vía multiplataforma (requiere Node.js):

```bash
npm install -g opencode-ai
```

> Nota: estos dos comandos son los únicos pasos de Windows verificados contra la documentación oficial. El resto del proceso en Windows — rutas, variables de entorno, cualquier paso adicional — no ha sido probado por el presentador, que no tiene una máquina Windows a mano. Si algo en tu instalación no coincide con lo descrito aquí, la página oficial es la autoridad: `https://opencode.ai/docs/`.

## Configurar el modelo

**opencode no trae un modelo propio (bring-your-own-model); en este taller usamos el nivel gratuito de OpenCode Zen.**

El presentador eligió OpenCode Zen (nivel gratuito) el 2026-08-30 porque no requiere descargar ningún modelo local y funciona en una laptop modesta. Este taller usa solo esa vía — no vamos a cubrir otros proveedores ni modelos locales hoy.

Dentro de opencode, conecta el proveedor y elige el modelo con:

```
/connect
```

Sigue las instrucciones en pantalla y pega la clave (API key) cuando se te pida. Luego elige el modelo con:

```
/models
```

La configuración resultante queda en el mismo archivo mencionado antes:

```
~/.config/opencode/opencode.json
```

> Nota: si tu organización bloquea el registro para obtener una clave o el flujo de `/connect` difiere de lo descrito aquí, consulta `https://opencode.ai/docs/providers/` — esa página es la fuente de esta información.

## Instalar una skill

**Un skill es una carpeta con un archivo `SKILL.md`; instalarlo es copiar esa carpeta a donde opencode los busca.**

Para el ejercicio del día 2 vamos a usar un skill ya preparado como punto de partida:

```
exercise/beer-lambert/SKILL.md.template
```

Ese archivo es una plantilla (scaffold) para completar durante el ejercicio, no un skill terminado. Cuando llegue el momento, lo vas a copiar a la carpeta de skills de opencode, quitarle el sufijo `.template` y completar los `TODO` que contiene. La guía del ejercicio en sí — los pasos, uno por uno — está en `content/02-ejercicio.md`.

## Comprobar que funciona

**Una comprobación te dice si la instalación quedó bien.**

Dentro de opencode, corre:

```
/models
```

> Nota: el resultado exacto que debería aparecer no está verificado contra la documentación oficial. Lo que sí puedes esperar de una instalación sana es que el comando responda sin errores y te muestre una lista de modelos disponibles, incluyendo el proveedor de OpenCode Zen que conectaste en la sección anterior. Si en cambio ves un error de conexión, un comando no reconocido, o una lista vacía, algo en la instalación o en la configuración del proveedor falló — revisa las secciones anteriores o `https://opencode.ai/docs/`.

## Problemas comunes

**Tres fallas explican la mayoría de los problemas de instalación.**

- **El comando `opencode` no se reconoce después de instalar.** Es casi siempre una entrada faltante en el PATH (la lista de carpetas donde tu terminal busca comandos ejecutables) — el instalador colocó el binario en una carpeta que tu terminal todavía no conoce. Cierra y vuelve a abrir la terminal primero; si el problema persiste, es un problema de PATH que resuelve la documentación oficial según tu instalador.
- **Un proxy corporativo bloquea el endpoint del modelo.** Si `/connect` o `/models` fallan con un error de red y estás en una red de empresa o universidad, es probable que un proxy o firewall corporativo esté bloqueando la conexión saliente hacia el proveedor del modelo. Habla con tu equipo de IT antes del taller si sospechas que este es tu caso.
- **Tu versión de Python es menor a 3.11.** Confirma tu versión con `python3 --version` antes del taller y actualiza si hace falta — varias partes del ejercicio del día 2 asumen 3.11 o más reciente.

> Nota: `python3 --version` es un comando estándar de Python, no de opencode — no está en la tabla de comandos verificados de este documento. Si tu sistema usa otro alias (`python --version`, por ejemplo), ese es el que debes correr.

> Nota: si ninguna de estas tres explica lo que ves, no inventes un arreglo — anota el mensaje de error exacto y pregúntalo al inicio del taller o revisa `https://opencode.ai/docs/`.
