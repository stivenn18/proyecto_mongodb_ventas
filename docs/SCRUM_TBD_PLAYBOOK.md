# 📖 SCRUM + TRUNK-BASED DEVELOPMENT (TBD) PLAYBOOK
## Adaptación de Scrum a entornos de Despliegue Continuo (CD) y Trunk-Based Development
**Proyecto:** Sistema de Ventas con MongoDB Atlas & Python  
**Repositorio:** `stivenn18/proyecto_mongodb_ventas`  


---

## 🎯 1. DIAGNÓSTICO DEL FLUJO ACTUAL Y FRICCIONES

### 1.1. Mapeo del Flujo de Entrega
El flujo de valor técnico implementado en el repositorio opera bajo la siguiente secuencia continua:

```
[Commit Local] ──> [Push a Rama Corta] ──> [Pull Request] ──> [CI: Job test (Ruff + Pytest)] 
       │
       ▼
[Code Review / Approval] ──> [Squash & Merge a main] ──> [CD: Job build_and_push] ──> [Imagen GHCR / Deploy]
```

### 1.2. Análisis de Salud del Flujo (Semáforo de Diagnóstico)

| Estado | Elemento del Flujo | Detalle / Situación Real |
| :---: | :--- | :--- |
| 🟢 **Funciona Bien** | **Pipeline Automatizado de CI/CD** | El job `test` valida sintaxis con `ruff` y pruebas unitarias con `pytest` en menos de 15 segundos. |
| 🟢 **Funciona Bien** | **Branch Protection & Rulesets** | `main` está protegido contra commits directos y force pushes; exige status checks en verde. |
| 🟡 **Genera Fricción** | **Revisión de PRs en Solitario** | En proyectos individuales o equipos pequeños, la regla de "1 aprobación externa" exige usar *Bypass rules* documentado. |
| 🟡 **Genera Fricción** | **Historias Demasiado Grandes** | Tendencia a codificar múltiples endpoints o pantallas en una sola rama, retrasando la integración a `main`. |
| 🔴 **Rompe el Flujo / Miedo** | **Miedo a Romper Producción en `main`** | Temor a fusionar código incompleto sin contar con un sistema de **Feature Flags / Toggles** activo (ej. ConfigCat). |

### 1.3. Preguntas Clave de Diagnóstico
1. **¿Cuánto tiempo vive normalmente una rama?**
   * *Diagnóstico:* Entre 1 y 4 horas. Bajo TBD ninguna rama debe superar las 24 horas de vida (*Short-Lived Branches*).
2. **¿Qué tan seguido integramos realmente a `main`?**
   * *Diagnóstico:* Mínimo 1 a 2 veces al día por desarrollador mediante micro-PRs atómicos.
3. **¿Nuestro Definition of Done (DoD) actual incluye "está en `main` y es desplegable"?**
   * *Diagnóstico:* **Sí**. Todo cambio aprobado debe estar integrado en `main`, pasar CI y generar su imagen en GHCR sin romper el estado desplegable.

---

## 👥 2. ROLES ADAPTADOS A TBD + CONTINUOUS DEPLOYMENT

Para sostener la disciplina de que `main` sea siempre desplegable, las responsabilidades de los roles de Scrum se redefinen:

```
+-----------------------------------------------------------------------------------------+
|                                ROLES ADAPTADOS EN TBD                                   |
+------------------------------------+----------------------------------------------------+
| PRODUCT OWNER (PO)                 | DEVELOPERS                                         |
| • Prioriza por valor y batch size. | • Responsabilidad colectiva de main siempre verde. |
| • Diseña y decide Feature Toggles. | • Commits pequeños y ramas de vida < 24h.          |
| • Lidera el corte (sliceado) fino. | • Ownership total del pipeline CI/CD y tests.      |
+------------------------------------+----------------------------------------------------+
|                             SCRUM MASTER (SM)                                           |
|                             • Facilita la integración continua diaria.                  |
|                             • Elimina bloqueos y el miedo a integrar a main.            |
|                             • Protege tiempo del Sprint para mejorar el pipeline.       |
+-----------------------------------------------------------------------------------------+
```

### Compromisos Concretos de Rol (*Post-its del Equipo*):
* **Product Owner:** *"A partir de mañana, redactaré las historias de usuario divididas en incrementos tan pequeños que puedan ocultarse tras un Feature Flag apagado y fusionarse a main el mismo día."*
* **Developer:** *"A partir de mañana, nunca dejaré una rama abierta por más de un día y si el pipeline de `main` se rompe, detener cualquier otra tarea para arreglarlo de inmediato."*
* **Scrum Master:** *"A partir de mañana, en cada Daily preguntaré qué se va a integrar hoy a main y protegeré horas del sprint para optimizar los tiempos de ejecución de los tests."*

---

## 🔄 3. ARTEFACTOS Y CEREMONIAS ADAPTADOS

### 3.1. Tabla Comparativa: Scrum Clásico vs. Scrum + TBD / CD

| Artefacto / Ceremonia | Versión Clásica de Scrum | Adaptación a TBD + Continuous Deployment |
| :--- | :--- | :--- |
| **Product Backlog** | Lista priorizada de grandes historias de usuario. | Historias **sliceadas finamente** + plan de **Feature Toggles** + Criterios de Aceptación validables en producción. |
| **Sprint Backlog** | Paquete cerrado de tareas para 2-3 semanas. | Flujo continuo de tareas que se planean integrar a `main` **diariamente**. |
| **Incremento** | Se presenta únicamente al final del Sprint. | **Continuo:** Cualquier commit en `main` que pase CI es un incremento potencialmente desplegable. |
| **Daily Scrum** | *¿Qué hice ayer? ¿Qué haré hoy? ¿Qué impedimentos tengo?* | **¿Qué voy a integrar hoy a `main` y qué necesito para que sea seguro?** |
| **Sprint Review** | Demo formal del software al cierre del Sprint. | Demostración de funcionalidades ya operativas o activadas en producción mediante toggles + feedback en vivo. |
| **Sprint Retrospective**| Mejorar el proceso general del equipo. | Medición del flujo de valor: salud del pipeline, tiempo de ciclo de PRs, fallos en `main` y disciplina TBD. |

---

### 3.2. Técnica de Sliceado de Historias (*Story Slicing*)
Ejemplo de descomposición atómica aplicada a la calculadora del proyecto:

```
               [Historia Madre: "Calculadora Científica y Financiera"]
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  [Historia 1 (Slice 1)]           [Historia 2 (Slice 2)]           [Historia 3 (Slice 3)]
  "Método resta() en backend      "Exposición de resta()           "Multiplicación, división,
   con feature flag al 0%"         en UI con rollout al 10%"        historial y flag al 100%"
   Status: ✅ Fusionado            Status: En progreso              Status: Backlog
```

---

## 🏆 4. LAS 5 REGLAS DE ORO DE INTEGRACIÓN A `MAIN`

1. **Ramas Efímeras (< 24 Horas):** Ninguna rama de feature debe vivir más de un día. Si una funcionalidad es compleja, se divide en piezas menores o se apaga con un *Feature Flag*.
2. **`main` Siempre Verde (*Always Releasable*):** Si un commit rompe los tests en `main`, todo el equipo detiene sus tareas secundarias hasta restaurar el build en verde.
3. **Validación Previa Local:** Antes de hacer push, el desarrollador debe ejecutar localmente `pytest` y `ruff check .` para garantizar que no subirá código con fallos evidentes.
4. **Micro Pull Requests (< 200 líneas):** Los PRs deben ser pequeños y fáciles de revisar en menos de 15 minutos, reduciendo los cuellos de botella de Code Review.
5. **Estrategia Squash and Merge:** Todo PR se fusiona consolidando sus commits en uno solo con formato semántico (`feat:`, `fix:`, `refactor:`), preservando un historial limpio y lineal.

---

## 📋 5. DEFINITION OF DONE (DoD) PRELIMINAR

Para considerar un ítem de trabajo como **Terminado (DONE)**, debe cumplir:

### ⚙️ Criterios Técnicos:
- [x] Código fuente escrito con estándares de tipado y formateo PEP 8.
- [x] 100% de cobertura en pruebas unitarias para las nuevas funciones (`tests.py`).
- [x] Linter `ruff` ejecutado sin advertencias ni errores.
- [x] Workflow de CI (`test`) aprobado en verde en GitHub Actions.
- [x] Dockerfile compila correctamente y la imagen se genera sin fallos en GHCR.
- [x] Rama secundaria eliminada (*housekeeping*) tras el merge a `main`.

### 💼 Criterios de Negocio:
- [x] Criterios de aceptación de la historia verificados.
- [x] Si la funcionalidad no está lista para el usuario final, se encuentra oculta tras un **Feature Toggle** apagado (0% rollout).
- [x] Documentación técnica actualizada en el informe del proyecto.

---

## 📌 6. DECISIONES PENDIENTES Y HOJA DE RUTA

1. **Integración con ConfigCat / LaunchDarkly:** Conectar el SDK de gestión remota de Feature Flags en Python y JavaScript para controlar los rollouts del 0% al 100% sin necesidad de redesplegar el código.
2. **Monitoreo y Métricas DORA:** Implementar métricas de:
   * *Deployment Frequency* (Frecuencia de despliegues a `main`).
   * *Lead Time for Changes* (Tiempo desde el commit hasta producción).
   * *Change Failure Rate* (Tasa de fallos en despliegues).
   * *Mean Time to Recovery (MTTR)* (Tiempo de recuperación ante incidentes).

---

## 🔍 7. DIAGNÓSTICO Y SALUD DEL BACKLOG (TALLER 4)

Para garantizar que el Backlog sea compatible con Trunk-Based Development (*TBD-Friendly*), todo ítem debe ser evaluado con los **4 Criterios Esenciales de Entrega Continua**:

```
+-----------------------------------------------------------------------------------------+
|                              LOS 4 CRITERIOS TBD DEL BACKLOG                            |
+--------------------------+--------------------------------------------------------------+
| 1. Tamaño                | ¿Se puede desarrollar, probar e integrar a main en ≤ 1 día?  |
| 2. Verticalidad          | ¿Atraviesa todas las capas y entrega valor por sí sola?       |
| 3. Feature Toggle        | ¿Tiene definido si requiere un flag (nombre y estado 0%)?    |
| 4. Validación en Prod    | ¿Sus Criterios de Aceptación son medibles tras el despliegue?|
+--------------------------+--------------------------------------------------------------+
```

### Matriz de Evaluación del Backlog Inicial:

| # Historia / Issue | Tamaño (≤1 día) | Verticalidad | Feature Toggle | Validación Prod | Clasificación Semáforo |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **#1: Resta en Calculator (Backend)** | 🟢 Sí (<3h) | 🟢 Sí (Lógica) | 🟢 `FLAG_RESTA = False` | 🟢 Tests unitarios | 🟢 **Lista para TBD** |
| **#2: Resta en Frontend (UI)** | 🟢 Sí (<4h) | 🟢 Sí (UI + API)| 🟢 Rollout al 10% | 🟢 Vista beta-testers | 🟢 **Lista para TBD** |
| **#3: Mult, Div, Historial + 100% Flag**| 🔴 No (>3 días) | 🟡 Mixta | 🔴 Sin flags atómicos | 🟡 Difícil aislar | 🔴 **Necesita Re-sliceado** |

---

## ✂️ 8. TÉCNICAS DE SLICEADO VERTICAL Y RE-SLICING

### 8.1. Slice Horizontal vs. Slice Vertical
* **Slice Horizontal (Anti-patrón):** Crear una rama para "Base de Datos", otra para "Backend" y otra para "Frontend". Genera ramas bloqueadas durante semanas que no entregan valor hasta integrarse todas juntas (*Merge Hell*).
* **Slice Vertical (TBD):** Cortar una funcionalidad delgada que atraviesa todas las capas (DB ➔ API ➔ UI) protegida por un Feature Flag apagado, permitiendo integrarla y probarla en `main` en menos de 24 horas.

```
       SLICE HORIZONTAL (Anti-patrón)                     SLICE VERTICAL (TBD)
 ┌───────────────────────────────────────┐         ┌─────────┬─────────┬─────────┐
 │ Capa UI (Rama frontend - 2 semanas)   │         │ Slice 1 │ Slice 2 │ Slice 3 │
 ├───────────────────────────────────────┤         │ (Resta) │ (Mult)  │ (Hist)  │
 │ Capa Lógica (Rama backend - 2 semanas)│   ──>   │ DB+API  │ DB+API  │ DB+API  │
 ├───────────────────────────────────────┤         │ +Flag0% │ +Flag0% │ +Flag10%│
 │ Capa Datos (Rama DB - 1 semana)       │         │ (≤ 1 d) │ (≤ 1 d) │ (≤ 1 d) │
 └───────────────────────────────────────┘         └─────────┴─────────┴─────────┘
```

---

### 8.2. Re-slicing de la Historia #3 (Descomposición en 3 Micro-Incrementos)

Se aplicó la plantilla oficial de Re-sliceado sobre la Historia compleja #3:

#### 🔹 Incremento 3.1: Operaciones Aritméticas Básicas Avanzadas
* **Descripción:** Implementar métodos `multiplicacion()` y `division()` en `Calculator` con validación de división por cero y pruebas unitarias.
* **¿Se puede integrar en $\le 1$ día?:** Sí (~3 horas).
* **¿Necesita Feature Toggle?:** Sí, `FLAG_OP_AVANZADAS = False` (Rollout al 0%).
* **Criterios de Aceptación:**
  - `Calculator().multiplicacion(4, 3) == 12`
  - `Calculator().division(10, 2) == 5.0`
  - Manejo de excepción `ValueError` al dividir entre `0`.
  - Pipeline de CI (`test`) en verde en GitHub Actions.

#### 🔹 Incremento 3.2: Persistencia de Historial de Operaciones en MongoDB
* **Descripción:** Crear colección `historial_calculos` en MongoDB Atlas y función para auditar cada cálculo ejecutado.
* **¿Se puede integrar en $\le 1$ día?:** Sí (~4 horas).
* **¿Necesita Feature Toggle?:** Sí, `FLAG_HISTORIAL_AUDITORIA = False` (Rollout al 0%).
* **Criterios de Aceptación:**
  - Inserción correcta de documento `{ operacion, a, b, resultado, timestamp }` en MongoDB.
  - Test unitario con Mock de PyMongo validando la inserción sin requerir conexión a internet en el CI.

#### 🔹 Incremento 3.3: Integración en Interfaz de Usuario y Retiro de Toggles
* **Descripción:** Construir los botones visuales en la interfaz, mostrar los últimos 10 cálculos y retirar los flags de código.
* **¿Se puede integrar en $\le 1$ día?:** Sí (~4 horas).
* **¿Necesita Feature Toggle?:** Activación al 100% (`FLAG_CALCULADORA_TOTAL = True`) y posterior depuración del código del toggle.
* **Criterios de Aceptación:**
  - Interfaz web interactiva con botones de suma, resta, multiplicación, división e historial.
  - Deuda técnica de toggles eliminada sin regresiones.

---

## 📅 9. PLANIFICACIÓN DE SPRINT ORIENTADA A FLUJO DIARIO

### 9.1. Sprint Goal Orientado a TBD
> **Sprint Goal:** *"Al final del sprint, los usuarios podrán realizar cálculos aritméticos completos (suma, resta, multiplicación, división) y auditar su historial en MongoDB, aunque la vista gráfica avanzada del historial permanezca oculta tras un Feature Flag al 10% para beta-testers."*

### 9.2. Cronograma de Integración Diaria a `main`

```
+-------------------+-----------------------------------+-----------------------------------+
| DÍA 1 - 2         | DÍA 3 - 4                         | DÍA 5+                            |
+-------------------+-----------------------------------+-----------------------------------+
| • Slice 1: Resta  | • Slice 2: UI de Resta (10% flag) | • Slice 3.3: UI Completa + Hist   |
|   en backend.     | • Slice 3.2: Persistencia de      | • Pruebas E2E en Producción.      |
| • Slice 3.1: Mult |   Historial en MongoDB Atlas.     | • Rollout al 100% y retiro de     |
|   y Div en core.  | • Validación en staging/prod.     |   Feature Flags obsoletos.        |
+-------------------+-----------------------------------+-----------------------------------+
```

### 9.3. Gestión Realista de Capacidad (Buffers Técnicos)
Para evitar que `main` se bloquee, se reserva un **25% del tiempo de desarrollo** para actividades críticas de entrega continua:
* **Tiempo de Code Review:** Máximo 30 minutos de espera por PR.
* **Tiempo de CI Pipeline:** Ejecución < 30 segundos.
* **Buffer de Interrupción:** Si el build de `main` falla, prioridad inmediata para el equipo.

---

## 🚦 10. DEFINITION OF READY (DoR) Y ACUERDOS DE EQUIPO

Ninguna historia de usuario puede ingresar al **Sprint Backlog** si no cumple con los **5 Criterios Obligatorios del DoR**:

```
+-----------------------------------------------------------------------------------------+
|                         CHECKLIST DE DEFINITION OF READY (DoR)                          |
+-----------------------------------------------------------------------------------------+
| [ ] 1. Sliceado Atómico: La historia está dividida para integrarse a main en ≤ 1 día.   |
| [ ] 2. Criterios de Aceptación Medibles: Verificables una vez desplegado en prod.       |
| [ ] 3. Feature Toggle Definido: Se especificó el nombre del flag y su estado (0%).      |
| [ ] 4. Sin Dependencias Externas: No está bloqueada por otras ramas o servicios caídos. |
| [ ] 5. Estrategia de Pruebas Clara: El desarrollador sabe qué pruebas unitarias creará. |
+-----------------------------------------------------------------------------------------+
```

### 3 Acciones Concretas para la Próxima Sprint Planning:
1. **Filtro Estricto de DoR:** Rechazar en la sesión de Planning cualquier historia estimada en más de 1 día de desarrollo.
2. **Priorización por Dependencia de Integración:** Colocar en la cima del Sprint Backlog historias que puedan fusionarse a `main` el **Día 1 del Sprint**.
3. **Daily Scrum Orientada a Flujo:** Enfocar las reuniones diarias en la pregunta: *¿Qué voy a integrar hoy a main y qué necesito para que sea seguro?*.

---

### 💬 Pregunta de Cierre: *¿Qué cambia en nuestra próxima Planning después de este taller?*
> **Conclusión:** *Cambia el paradigma de planificación: dejamos de planificar "bloques gigantescos de trabajo que se prueban al final de 2 semanas" y pasamos a planificar una **secuencia ordenada de micro-integraciones diarias**. El Sprint Planning se convierte en una sesión de diseño de Feature Flags y aseguramiento del DoR, garantizando que el tronco principal (`main`) reciba valor desde el primer día.*

