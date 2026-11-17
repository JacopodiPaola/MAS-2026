# Estudios de parámetros (antes de la luz)

## ¿Para qué hacemos esto?

Antes de agregar luz queremos conocer bien a nuestros peces virtuales:

- qué necesitan para formar un cardumen;
- qué parámetros cambian mucho su comportamiento y cuáles casi no importan.

Así, cuando agreguemos luz y algo cambie, sabremos que fue por la luz y no por un parámetro mal elegido.

---

## Ideas básicas (léelas primero)

**1. BL = body length = el largo de un pez ≈ 5 cm.**
Es nuestra unidad de distancia (Puckett et al. 2018, tabla S1; Tunstrøm et al. 2013). "1 BL/s" quiere decir que el pez avanza su propio largo cada segundo.

**2. Un paso = una decisión = 0.125 s.**
En cada paso, cada pez mira a sus vecinos, elige una dirección y avanza. Puckett usa 8 decisiones por segundo (tabla S1), y Couzin (2002) dice que el paso representa el tiempo de reacción del pez. Más detalles en `handlings/DECISION_RATE.md`.

**3. Largo de paso: ℓ = velocidad × dt.**
Es lo que avanza un pez entre dos decisiones. **Descubrimos que, si el pez gira de golpe y no tiene ruido, el modelo solo depende de ℓ.** Por ejemplo, estas tres combinaciones dan **exactamente las mismas trayectorias**, porque en las tres ℓ = 0.25 BL:

| Velocidad | dt | ℓ |
|---|---|---|
| 1 BL/s | 0.25 s | 0.25 BL |
| 2 BL/s | 0.125 s | 0.25 BL |
| 0.5 BL/s | 0.5 s | 0.25 BL |

¿Por qué? Ninguna regla del pez usa los segundos. El pez solo mira dónde están los demás y avanza ℓ. Lo único que cambia es cuántos segundos "dura" cada decisión. Por eso en el estudio 3 no probamos velocidad y dt por separado.

**4. ¿Cuándo decimos que el cardumen "funciona"?**
Esta definición se decide antes de correr nada y vale para todos los estudios:

1. **Están juntos:** durante al menos el 90 % de la ventana final, el grupo más grande tiene al menos el 95 % de los peces. Dos peces cuentan como "conectados" si están a 5.5 BL o menos (el radio de atracción).
2. **No chocan:** como máximo en el 5 % de los momentos hay algún par de peces a menos de 0.25 BL.
3. **Están ordenados:** la polarización es al menos 0.65 (todos nadan hacia el mismo lado) o la rotación es al menos 0.65 (nadan en círculo, lo que se llama *milling*). Si están juntos pero sin orden, lo llamamos *swarm*.

Además comparamos con peces reales la distancia de cada pez a su vecino más cercano. En golden shiners, el vecino suele estar a 1.5–2 BL y casi nunca a menos de 1 BL ni a más de 4 BL (Katz et al. 2011, grupos de 2 peces).

**Detalles que fijamos en el código antes de correr** (`study_tools.py`):

- Todo se mide **en cada decisión del último tercio** de la corrida.
- "Ordenados" usa las **medias** del último tercio: polarización media ≥ 0.65 o rotación media ≥ 0.65.
- Estado en cada momento: **separado** si el grupo más grande tiene menos del 95 % de los peces; si no, **polarizado** si la polarización es ≥ 0.65; si no, **milling** si la rotación es ≥ 0.65; si no, **swarm**. La etiqueta final de cada corrida usa las mismas reglas con las medias.
- El enlace entre dos peces usa el radio de atracción **del modelo**. Cuando r_a cambia (estudio 1C con 7 BL y estudio 4 con 3.5–9 BL), guardamos también la misma cuenta con 5.5 BL fijos (`together_fraction_fixed_link`).
- Con 10 o 16 peces, "95 %" quiere decir **todos** los peces.
- Para los estudios 2 y 4, una configuración "funciona" si funciona en **más de la mitad** de las seeds.

---

## Los parámetros

| Parámetro | Qué es, en simple | Nuestro valor ahora | Valor en los papers | Fuente |
|---|---|---|---|---|
| N | número de peces | 20 | 8–256 en simulación, 16–128 en experimentos | Puckett 2018 |
| Arena | tamaño del tanque | 20 × 20 BL | 28 × 28 BL (140 cm) | Puckett, tabla S1 |
| Paredes | qué pasa al llegar al borde | rebota | tanque con un borde blanco que aleja a los peces | Puckett, SI |
| dt | cada cuánto decide el pez | 0.125 s | 0.125 s (8/s); Couzin usa 0.1 s | Puckett S1; Couzin 2002 |
| Velocidad | qué tan rápido nada | 1 BL/s fija | 0.2–5 BL/s según la luz | Puckett S1 |
| r_r | zona de repulsión (se aleja) | 0.5 BL | 0.5 BL | Puckett S1 |
| r_o | zona de orientación (se alinea) | 3 BL | 3 BL | Puckett S1 |
| r_a | zona de atracción (se acerca) | 5.5 BL | 5.5 BL | Puckett S1 |
| Campo visual | cuánto ve a su alrededor | 360° | 270° (90° ciegos detrás) | Puckett 2018 |
| Giro máximo | cuánto puede girar en una decisión | sin límite (gira de golpe) | 1.75 rad (≈ 100°) por decisión | Puckett S1 |
| Ruido | error al elegir la dirección | 0 | 0.01 rad | Puckett S1 |
| Combinación | cómo se suman orientación y atracción | suma directa | suma directa (ec. 7 del SI) | Puckett SI |

En el estudio 2 probamos parámetros extra que los papers no discuten: regulación de velocidad (Katz 2011), vecinos "topológicos", actualización uno por uno, inicio compacto, velocidad distinta para cada pez y tamaño de arena.

---

## Los 4 estudios

| # | Pregunta | Carpeta |
|---|---|---|
| 1 | ¿Qué pasa si usamos los parámetros de los papers? | `01_parametros_papers/` |
| 2 | ¿Hay parámetros que nadie tuvo en cuenta y que sí importan? | `02_parametros_nuevos/` |
| 3 | ¿Cómo cambia todo con dt y velocidad? ¿Qué se mantiene igual? | `03_dt_y_velocidad/` |
| 4 | ¿Qué es lo mínimo que necesitan los peces? ¿Qué parámetros son sensibles? | `04_minimo_y_sensibilidad/` |

**Orden recomendado: 1 → 3 → 4 → 2.**
- El 1 nos da la configuración base, la de los papers.
- El 3 es rápido y nos dice en qué rango de velocidades funciona el cardumen, que es justo lo que necesitamos para la luz.
- El 4 usa esa base para encontrar lo mínimo y lo sensible.
- El 2 va al final porque necesita más código nuevo.

---

## Cómo se corre (igual en todos los estudios)

- **Código:**
  - `parameter_studies/study_model.py`: el modelo con opciones extra. Con las opciones por defecto da exactamente lo mismo que `shiner_model.py`.
  - `parameter_studies/study_tools.py`: corre una simulación y la resume en una fila de resultados.
- **`shiner_model.py` no se toca**, porque los trials comprueban su contenido.
- **Seeds:** 10 por configuración (0–9).
- **Duración:** hasta que cada pez haya nadado 180 BL, que equivale a 180 s a 1 BL/s (1440 decisiones). Medimos en el último tercio de la simulación.
- **Resultados:** se guardan en `data/` (CSV) dentro de cada estudio, para no tener que volver a simular. Las figuras van en `figures/`.

---

## Qué nos llevamos a la fase de luz (rellenar al final)

- Parámetros clave y valores elegidos, con su justificación:
- Rango de ℓ (velocidad × dt) en el que el cardumen funciona:
  - La luz va a cambiar la velocidad entre 0.2 y 5 BL/s, es decir, ℓ entre 0.025 y 0.625 BL.
- Parámetros que no importan, que se dejan en el valor más simple:

---

## Referencias

- Couzin, I. D., Krause, J., James, R., Ruxton, G. D., & Franks, N. R. (2002). Collective memory and spatial sorting in animal groups. *Journal of Theoretical Biology, 218*, 1–11.
- Katz, Y., Tunstrøm, K., Ioannou, C. C., Huepe, C., & Couzin, I. D. (2011). Inferring the structure and dynamics of interactions in schooling fish. *PNAS, 108*, 18720–18725.
- Puckett, J. G., Pokhrel, A. R., & Giannini, J. A. (2018). Collective gradient sensing in fish schools. *Scientific Reports, 8*.
- Tunstrøm, K., Katz, Y., Ioannou, C. C., Huepe, C., Lutz, M. J., & Couzin, I. D. (2013). Collective states, multistability and transitional behavior in schooling fish. *PLoS Computational Biology, 9*, e1002915.
