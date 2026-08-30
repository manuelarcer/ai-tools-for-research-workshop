---
title: Conceptos fundamentales
dia: 1
deck: true
last_reviewed: 2026-08-30
---

## Qué es (y qué no es) un LLM

**Un LLM (large language model, modelo de lenguaje grande) predice texto; no consulta una base de hechos.**

- Trabaja con tokens (fragmentos de palabras), no con palabras completas.
- La ventana de contexto (context window, todo lo que el modelo "ve" a la vez) es finita — por eso la gestión del contexto importa tanto como lo que le pides.
- No tiene memoria entre sesiones, a menos que tú se la des (guardando notas, archivos o contexto que vuelvas a cargar).

> Nota: cuando el modelo "no sabe" algo, lo más probable es que invente una respuesta plausible en vez de decir que no sabe. De ahí nace el hilo de verificación que cierra esta sesión.

Un LLM es, en el fondo, una función que continúa texto de la manera estadísticamente más probable dado lo que ya escribiste. Eso explica tanto su utilidad (redacta, resume, programa) como su falla característica: puede sonar seguro y estar equivocado, porque nunca "sabe" nada — solo predice.

## El bucle del agente (agent loop)

**Un agente no es una caja de chat; es un bucle de prompt del sistema (system prompt, las instrucciones iniciales que guían al modelo), herramientas (tools) y repetición.**

- El modelo elige una herramienta, la herramienta se ejecuta, el resultado regresa al modelo.
- El bucle continúa: el modelo decide el siguiente paso con esa nueva información.
- Se detiene cuando la tarea está terminada o cuando tú lo detienes.

Chatear es una sola vuelta: preguntas, el modelo responde con texto, fin. Un agente en cambio puede leer un archivo, ejecutar un comando, ver el resultado y decidir el siguiente paso por su cuenta, varias veces seguidas, sin que tú escribas cada instrucción intermedia. Eso es lo que veremos correr en opencode hoy.

## Capas de contexto

**Lo que el agente sabe llega en capas que tú controlas.**

- Reglas globales: aplican a todo lo que haces con la herramienta, en cualquier proyecto.
- Reglas del proyecto: instrucciones específicas de este repositorio o carpeta de trabajo.
- Contexto de la sesión: lo que has escrito o cargado en la conversación actual.

> Nota: en Claude Code estas reglas de proyecto viven en un archivo `CLAUDE.md`; en opencode el equivalente es `AGENTS.md` (o los archivos de reglas del proyecto). Misma idea, distinto nombre.

Separar estas capas evita repetir instrucciones y evita que una regla de un proyecto se filtre a otro. Cuanto más claras estén las capas, menos tienes que explicarle al agente cada vez que abres una sesión nueva.

## Skills: instrucciones reutilizables

**Un skill es un procedimiento escrito que el agente carga cuando es relevante.**

- Progressive disclosure (revelación progresiva): el agente solo lee el skill completo cuando la tarea lo amerita, no todo el tiempo.
- Un skill es texto plano — instrucciones en lenguaje natural, no código compilado — por eso tú también puedes escribir uno.
- El día 2 lo verás desde el otro lado: en vez de solo usar un skill, vas a escribir uno propio.

Hoy solo lo verás correr: un skill ya escrito, invocado por el agente en el momento correcto. La idea es que quede claro qué hace un skill y por qué "solo texto" es suficiente, antes de pedirte que escribas el tuyo.

## Subagentes y elección de modelo

**Puedes mandar un modelo barato a explorar y uno capaz a construir, en la misma sesión.**

- La selección de modelo por subagente (per-agent model selection) es la fortaleza real de opencode frente a otras herramientas.
- La historia de costo: no todo el trabajo necesita el modelo más caro — explorar, buscar o resumir puede correr en un modelo gratuito o barato, y reservar el modelo fuerte para la parte que realmente lo exige.
- Este es el patrón insignia (signature pattern) del taller: modelo fuerte planea, modelo económico ejecuta, y siempre se verifica el resultado.

> Nota: este mismo patrón — planear con un modelo, ejecutar con otro, verificar siempre — es el que usarás en el ejercicio de Beer-Lambert del día 2.

## Hooks: disparadores del ciclo de vida

**Los hooks corren tu código automáticamente en puntos concretos de la vida del agente.**

- En opencode, los hooks son plugins en JS/TS (JavaScript/TypeScript) anclados a eventos del ciclo de vida, por ejemplo `tool.execute.before` (antes de que una herramienta se ejecute).
- Esto es de mayor ceremonia que los hooks de Claude Code, que pueden ser un archivo o un comando de shell simple — hay que ser honestos con esa diferencia.
- Se enseñan como concepto y se muestran corriendo; no se espera que los escribas en vivo hoy.

> Nota: escribir un plugin JS/TS no es el objetivo de este taller. Lo importante es entender qué resuelve un hook, no su sintaxis.

Un hook es útil cuando quieres que algo pase siempre — por ejemplo, registrar cada vez que el agente usa una herramienta, o bloquear una acción antes de que ocurra — sin tener que acordarte de pedirlo cada vez. En opencode, montar uno cuesta más trabajo que en Claude Code, así que hoy solo lo vas a ver funcionando.

## MCP y herramientas

**Las herramientas (tools) son lo que hace que el agente deje de ser una caja de texto y toque el mundo real.**

- MCP (Model Context Protocol) es la forma estándar de conectarle una capacidad nueva al agente — un buscador, un sistema de archivos, una API.
- El agente solo puede hacer lo que sus herramientas le permiten: sin una herramienta de archivos no puede leer un archivo; sin una de red no puede navegar.
- Cada herramienta conectada amplía lo que el agente puede hacer, pero también lo que puede hacer mal — por eso importa saber cuáles tiene activas.

Pensar en "qué herramientas tiene este agente" es tan importante como pensar en qué modelo usa. El modelo decide qué hacer; las herramientas determinan si puede hacerlo de verdad.

## Salvaguardas y control

**Te mantienes en el bucle decidiendo qué puede hacer el agente sin preguntar.**

- Permisos: allow (permitir sin preguntar) o ask (pedir confirmación antes de actuar).
- Hay acciones en las que el agente siempre debe pausar y preguntar — por ejemplo, borrar archivos, hacer cambios irreversibles o enviar información fuera de tu máquina.
- Nunca le entregues credenciales ni datos sensibles al agente como si fueran texto cualquiera.

> Nota: "permitir todo" es cómodo pero no es gratis — cada permiso que das es una acción que el agente puede tomar sin que tú la veas antes de que ocurra.

Configurar bien los permisos no es paranoia, es la diferencia entre un asistente que acelera tu trabajo y uno que un día borra o envía algo que no debía, porque nadie definió el límite.

## El hilo de confianza

**Para ciencia, la verificación no es opcional.**

- Los modelos fabrican citas, DOIs (identificadores de artículos) y números con total confianza, sin ninguna señal de que están inventando.
- Un resultado que no verificaste no es un resultado — es una hipótesis con buena redacción.
- Este hilo recorre cada una de las diapositivas anteriores y todo el ejercicio del día 2: cada capacidad que ganas con agentes, skills y herramientas viene con la misma obligación de comprobar la salida.

> Nota: en el día 2 verás este principio en carne propia — un ajuste con R² casi perfecto que resulta estar equivocado, y solo la verificación lo revela.

Todo lo que viste hoy — el bucle del agente, las capas de contexto, los skills, los subagentes, los hooks, las herramientas, los permisos — te da más capacidad de acción. Ninguna de esas piezas te dice si el resultado es correcto. Eso lo decides tú, verificando. El ejercicio del día 2 está construido exactamente alrededor de esa idea.
