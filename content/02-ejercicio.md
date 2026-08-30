---
title: Ejercicio — calibración Beer-Lambert que se verifica a sí misma
dia: 2
deck: true
last_reviewed: 2026-08-30
---

## El objetivo, dicho de frente

**Vas a construir un pipeline (flujo de procesamiento) que da una respuesta segura de sí misma y equivocada en casi un 20%, y luego vas a construir el chequeo que lo detecta.**

- El ajuste de calibración va a salir casi perfecto: R² = 0.9998.
- Con ese ajuste, la concentración que prediga tu pipeline va a estar mal de todas formas.
- Nada de esto está escondido: te lo estoy diciendo ahora, antes de que lo construyas.
- El objetivo del ejercicio no es sorprenderte — es que aprendas a dudar de un resultado incluso cuando el ajuste se ve perfecto.

> Nota: si en algún punto piensas "esto ya funciona, R² es casi 1" — recuerda esta sección. Ese es exactamente el momento en que hay que verificar, no confiar.

Este es el ejercicio central del taller. Vas a escribir (autor, no solo usuario) un skill (conjunto de instrucciones reutilizables, visto el día 1) de opencode que calibra, predice y se verifica a sí mismo contra un control conocido. El hilo del día 1 — la verificación no es opcional — se vuelve concreto aquí: vas a sentir en carne propia por qué un buen ajuste estadístico no es lo mismo que una respuesta correcta.

## Los datos

**Los datos son sintéticos, así que la respuesta verdadera es aritmética exacta — no una opinión ni una medición con margen de error.**

- Colorante: azul de metileno (methylene blue), con pico de absorción λmax ≈ 664 nm y coeficiente de extinción ε ≈ 95,000 M⁻¹cm⁻¹, paso óptico (path length) de 1 cm.
- Seis estándares de calibración a concentraciones conocidas: 2, 4, 6, 8, 10 y 12 µM.
- Un espectro "incógnita" (unknown) cuya concentración real no se te revela hasta el milestone M4.
- Archivos: `calibration_*.csv`, `calibration_index.csv`, `unknown.csv`, con columnas `wavelength_nm,absorbance`.
- Cada espectro cubre de 400 a 800 nm.

> Nota: la línea base (baseline, el nivel de fondo bajo el pico) de la incógnita es distinta a la de los espectros de calibración — como pasaría un día distinto, con una cubeta distinta. Esa diferencia, aparentemente inocente, es la causa de todo lo que viene.

Los datos se generaron con un script (programa corto) determinista (seed 42, la semilla que fija el generador de números aleatorios para que el resultado sea siempre el mismo). Que sean sintéticos no los hace artificiales en el sentido de "irreales": el ε de azul de metileno es real, y cada espectro incluye ruido y una línea base que varía ligeramente, tal como se ve en un laboratorio de verdad. La diferencia es que aquí tú sabes la respuesta correcta de antemano, porque la definiste al generar los datos — por eso verificar es aritmética, no debate.

## M0 — Carga y grafica un espectro

**Si logras cargar un espectro y graficarlo, ya estás dentro — este milestone lo alcanza todo el mundo.**

- Carga cualquiera de los archivos `calibration_*.csv` con tu herramienta de análisis habitual (Python, pandas, lo que uses en el skill).
- Grafica absorbancia (absorbance) contra longitud de onda (wavelength).
- Confirma que ves un pico cerca de 664 nm.

> Nota: si te atrasas o llegas tarde, este es tu punto de entrada — no necesitas nada de lo anterior para lograrlo.

No hay truco en este milestone: es la prueba de que tu entorno funciona y de que sabes leer los archivos. Tómate el tiempo que necesites aquí antes de avanzar.

## M1 — Lee un pico por concentración

**Para cada espectro de calibración, lee la absorbancia del pico y empareja ese valor con su concentración conocida.**

- Usa `calibration_index.csv` para saber qué concentración corresponde a cada archivo `calibration_*.csv`.
- Para cada espectro, encuentra la absorbancia máxima (el instinto natural: el valor más alto de la columna `absorbance`).
- Construye una tabla: concentración conocida → absorbancia del pico, con seis filas.

Este es tu primer resultado real. Guarda esa tabla — la vas a usar en el siguiente milestone para ajustar la recta de calibración.

## M2 — Ajusta la recta de calibración

**Ajusta una recta a absorbancia contra concentración y reporta pendiente (slope), intersección (intercept) y R² = 0.9998.**

- La ley de Beer-Lambert predice una relación lineal: A = ε·l·c.
- Ajusta una recta a tus seis puntos (concentración, absorbancia del pico).
- Reporta pendiente, intersección y el coeficiente de determinación R².

> Nota: ese R² de 0.9998 está a punto de engañarte. Un ajuste casi perfecto se siente como una confirmación de que todo el pipeline está bien — y no lo está. Sigue adelante y compruébalo tú mismo en M4.

Guarda el ajuste (pendiente e intersección): lo vas a invertir en el siguiente paso para convertir una absorbancia en una concentración.

## M3 — Predice la incógnita

**Con la recta ajustada, el pipeline ya da un número seguro de sí mismo para la incógnita: cerca de 10.78 µM.**

- Lee el pico de `unknown.csv` de la misma forma que leíste los picos de calibración en M1.
- Invierte la recta de calibración (la que ajustaste en M2) para convertir esa absorbancia en una concentración.
- Reporta la concentración predicha con sus unidades.

Hasta aquí, todo se ve bien: los datos cargaron, el ajuste fue casi perfecto, y el pipeline entregó un número concreto. Si te detuvieras aquí, reportarías ese número como la respuesta. No lo hagas todavía.

## M4 — Compara contra la verdad

**La concentración verdadera es 9.00 µM: tu predicción está mal por +19.8 %, aunque el ajuste era casi perfecto.**

- Compara tu predicción de M3 (≈10.78 µM) contra el valor verdadero (9.00 µM).
- Calcula el error porcentual: +19.8 %.
- El R² de M2 seguía siendo 0.9998 — un ajuste casi perfecto no te salvó de una respuesta equivocada.

> Nota: la lección en una línea: un ajuste perfecto no es una respuesta correcta. El R² mide qué tan bien la recta describe tus seis puntos de calibración, no si tu método de lectura del pico es correcto.

Este es el momento en que el pipeline "bonito" te falla, tal como se anunció en la primera sección. La razón está en cómo leíste el pico, no en el ajuste — eso es lo que vas a diagnosticar en el siguiente milestone.

## M5 — Diagnostica, corrige y verifica

**La causa es la línea base (baseline); el arreglo va dentro del skill, no solo en tu cabeza para esta vez.**

- Resta la línea base de cada espectro antes de leer el pico, en vez de tomar el máximo crudo.
- Vuelve a correr el pipeline completo (M1 a M4) con los picos corregidos: la predicción debe caer cerca de 9.03 µM, un error de apenas +0.3 %.
- Añade al skill una comprobación (assertion) que falle de forma visible cuando un control conocido se desvíe más de una tolerancia fija — para que la próxima vez que uses el skill, el error no pase inadvertido.

> Nota: la corrección no es "me fijé mejor esta vez". Es escribir la comprobación dentro del skill, para que la próxima persona (o tú mismo, dentro de un mes) no tenga que acordarse de revisar a mano.

El motivo por el que el pico crudo falla: la absorbancia máxima incluye lo que sea que haya bajo el pico —la línea base— y la línea base de la incógnita no es la misma que la de los espectros de calibración. Al restarla antes de leer el pico, esa diferencia deja de contaminar la lectura.

## M6 — Endurece (vía rápida)

**Si llegaste hasta aquí temprano, hay más trabajo útil por hacer antes de que termine el bloque.**

- Grafica los residuales (residual plot) del ajuste de calibración para ver si quedan patrones sin explicar.
- Añade una guarda de extrapolación (extrapolation guard) que avise cuando la incógnita cae fuera del rango de concentraciones calibradas.
- Propaga la incertidumbre (uncertainty propagation) del ajuste hacia un ± en la concentración reportada, en vez de dar solo un número puntual.

Ninguno de estos tres pasos es obligatorio para completar el ejercicio. Son la diferencia entre un skill que pasa la prueba de hoy y uno que seguirías usando con datos reales.

## La lección que se lleva a casa

**Un skill de investigación en el que puedes confiar es uno que se comprueba a sí mismo.**

- La verificación que añadiste en M5 no es trabajo extra ni burocracia: es lo que separa una demostración (algo que se ve bien una vez) de un instrumento (algo en lo que puedes apoyarte la próxima vez).
- El mismo patrón — modelo fuerte planea, modelo económico ejecuta, tú siempre verificas el resultado — es el que vas a usar en tu propio trabajo el día 3.

Todo lo que hiciste hoy tenía una salida disponible: podías haberte quedado en M3 con un número seguro de sí mismo y equivocado. La diferencia entre eso y una respuesta en la que puedes confiar no fue un modelo más inteligente ni datos más limpios — fue el paso de comprobar contra algo conocido antes de reportar. Esa es la habilidad que te llevas, más allá de este ejercicio en particular.
