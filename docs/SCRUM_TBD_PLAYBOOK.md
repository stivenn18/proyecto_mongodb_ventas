# 📖 SCRUM + TRUNK-BASED DEVELOPMENT (TBD) PLAYBOOK (VERSIÓN 3.0)
## Adaptación de Ceremonias Scrum a Continuous Deployment y Liberación Segura
**Proyecto:** Sistema de Ventas con MongoDB Atlas & Python  
**Repositorio:** `stivenn18/proyecto_mongodb_ventas`  
**Entorno de Producción:** `https://proyecto-mongodb-ventas.onrender.com`  
**Feature Flags:** ConfigCat SDK Cloud  


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

---

## 🚀 11. CI/CD ROBUSTO, AUTO-DEPLOY A RENDER Y GOBERNANZA DE CONFIGCAT (TALLER 3)

### 11.1. Auto-Deploy desde `main` a Render
Se implementó el despliegue continuo mediante infraestructura como código ([`render.yaml`](file:///c:/Users/stive/Downloads/proyecto_mongodb_ventas/render.yaml)) y la API web en FastAPI ([`app.py`](file:///c:/Users/stive/Downloads/proyecto_mongodb_ventas/app.py)):

* **Repositorio Vinculado:** `stivenn18/proyecto_mongodb_ventas`
* **Rama de Producción:** `main` (Despliegue 100% automatizado tras merge).
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
* **Health Check Endpoint:** `/health` (Monitorea el estado `{ "status": "healthy", "service": "ventas-wishlist-api" }`).
* **Variables de Entorno:** `CONFIGCAT_SDK_KEY`, `MONGO_URI`, `ENVIRONMENT=production`.

---

### 11.2. Integración de ConfigCat SDK y Acuerdos de Gobernanza
Se integró el SDK oficial de **ConfigCat** (`configcat-client`) para gestionar los Feature Flags de forma remota sin requerir redespliegues de código:

```
+-----------------------------------------------------------------------------------------+
|                  CICLO DE VIDA DEL FEATURE TOGGLE (WISHLIST E-COMMERCE)                 |
+-------------------+-----------------------------------+---------------------------------+
| ESTADO DEL TOGGLE | COMPORTAMIENTO OBSERVADO          | AUDIENCIA OBJETIVO              |
+-------------------+-----------------------------------+---------------------------------+
| 🔴 OFF (0%)       | Botón "❤️ Guardar" y modal oculto | Código desplegado e inactivo.   |
| 🟡 CANARY (10%)   | Visible solo para Beta-Testers    | Validación real de feedback.    |
| 🟢 ON (100%)      | Funcionalidad 100% pública        | Todos los usuarios de la tienda.|
+-------------------+-----------------------------------+---------------------------------+
```

#### Acuerdos de Gobernanza de Feature Flags:
1. **Responsable de Activación:** El *Product Owner (PO)* junto al equipo técnico decide el momento de avance de rollout (0% ➔ 10% ➔ 100%).
2. **Fecha de Limpieza Obligatoria (*Toggle Debt*):** Todo flag activado al 100% debe ser retirado del código en un plazo máximo de 1 Sprint para evitar deuda técnica acumulada.

---

### 11.3. Definition of Done (DoD) Versión Final (3 Dimensiones)

El **Definition of Done definitivo** acordado por el equipo cubre las 3 dimensiones indispensables para el flujo TBD:

```
+-----------------------------------------------------------------------------------------+
|                    DEFINITION OF DONE (DoD) FINAL - VERSIÓN OFICIAL                     |
+----------------------------+----------------------------+-------------------------------+
| ⚙️ DOD TÉCNICO             | 💼 DOD DE NEGOCIO          | 🚀 DOD DE DESPLIEGUE          |
+----------------------------+----------------------------+-------------------------------+
| • Código revisado en PR.   | • Acceptance Criteria      | • Auto-desplegado en Render   |
| • CI en verde (Pytest+Ruff)|   cumplidos al 100%.       |   desde main.                 |
| • Imagen Docker en GHCR.   | • Validable en producción. | • Health check /health en OK. |
| • Feature Toggle probado.  | • PO conoce el estado del  | • Logs y métricas sin errores.|
| • Cero regresiones.        |   Toggle (OFF/10%/100%).   | • Toggle en estado acordado.  |
+----------------------------+----------------------------+-------------------------------+
```

---

## 🏆 12. CIERRE FORMAL DE FASE 1 (CHECKLIST CUMPLIDO)

- [x] Auto-deploy desde `main` a **Render** configurado y validado con `/health`.
- [x] Feature Toggle con **ConfigCat** operativo para el Ejemplo 1 (*Wishlist E-Commerce*).
- [x] Suite de pruebas unitarias robusta con 100% de cobertura y `ruff linter` aprobado.
- [x] Definition of Done (DoD) definitivo documentado y aplicado.
- [x] Repositorio `main` protegido con Rulesets y operando bajo Trunk-Based Development real.

---

## 🎬 13. ADAPTACIÓN DEL SPRINT REVIEW A CONTINUOUS DEPLOYMENT (TALLER 6)

### 13.1. Principios del Nuevo Review
En un entorno con integración diaria a `main` y auto-deploy continuo, el Sprint Review deja de ser una "reunión de aprobación tardía" o un momento tenso de entrega y se transforma en una **demostración de valor real en producción (o activable)**.

```
+-----------------------------------------------------------------------------------------+
|                  COMPARATIVA: SPRINT REVIEW CLÁSICO VS. REVIEW EN CD + TBD              |
+------------------------------------+----------------------------------------------------+
| SPRINT REVIEW CLÁSICO              | SPRINT REVIEW EN CONTINUOUS DEPLOYMENT (TBD)       |
+------------------------------------+----------------------------------------------------+
| • Demo del incremento al final     | • Demo de lo que YA ESTÁ (o puede estar) en        |
|   del sprint (ambiente local/QA).  |   producción real (Render).                        |
| • Lógica de "Todo o Nada".         | • Valor incremental protegido por Feature Toggles. |
| • Feedback tardío tras semanas     | • Feedback continuo + validación con usuarios      |
|   de desarrollo acumulado.         |   reales y telemetría de producción.               |
| • Enfocado en "¿Qué construimos?". | • Enfocado en "¿Qué valor recibieron los usuarios?"|
+------------------------------------+----------------------------------------------------+
```

### 13.2. Estructura Obligatoria de la Demo (Máximo 4-5 minutos por ítem)
Cada incremento presentado durante el Review debe seguir una pauta ágil y rigurosa:
1. **¿Qué problema de usuario resuelve?** Explicación del dolor o necesidad resuelta.
2. **¿Está activo para todos o detrás de toggle?** Transparencia del estado del flag en ConfigCat (OFF / Canario % / 100% ON).
3. **Demo en vivo en Render:** Verificación en el entorno productivo real activando/desactivando el Feature Flag si aplica.
4. **Métrica o evidencia de valor:** Datos observados en telemetría o feedback de usuarios.
5. **Pregunta al PO / Stakeholder:** *“¿Esto genera el valor esperado y estamos listos para ampliar la audiencia?”*

### 13.3. Simulación Práctica del Review (Incrementos Reales del Proyecto)

#### 🔹 Incremento 1: Lista de Deseos (Wishlist E-Commerce)
* **Problema resuelto:** Los clientes necesitaban guardar productos de interés sin agregarlos de inmediato al carrito de compras.
* **Estado del Toggle:** Protegido por el flag `wishlist_enabled` en ConfigCat Cloud.
* **Demo en vivo:** Se muestra la tienda en Render (`https://proyecto-mongodb-ventas.onrender.com`). Con el flag en OFF, los botones de favoritos y el modal no son visibles. Se conmuta el flag a ON en vivo y el frontend actualiza la UI mostrando los botones de corazón y el contador de favoritos sin redesplegar.
* **Pregunta clave:** *“¿La experiencia de guardado responde a la expectativa del cliente antes de iniciar la campaña de fidelización?”*

#### 🔹 Incremento 2: Catálogo Dinámico con Filtros y Buscador Reactivo
* **Problema resuelto:** Búsqueda lenta de productos por catálogo extenso. Permite filtrar instantáneamente por laptops, componentes, periféricos y monitores.
* **Estado del Toggle:** 100% Activo para todos los usuarios.
* **Demo en vivo:** Navegación fluida y filtrado instantáneo en la web de Render.
* **Pregunta clave:** *“¿La categorización cubre las líneas prioritarias para la temporada de ventas?”*

#### 🔹 Incremento 3: Telemetría de Flags y Monitoreo de Salud (`/health` y `/api/flags`)
* **Problema resuelto:** Visibilidad operativa del backend y sincronización en tiempo real con ConfigCat.
* **Estado:** 100% Activo en producción.
* **Demo en vivo:** Consulta de `/health` devolviendo `{ "status": "healthy" }` con latencia inferior a 50 ms.

---

## 🔍 14. ADAPTACIÓN DE LA SPRINT RETROSPECTIVE (TALLER 6)

### 14.1. Los 3 Nuevos Focos Obligatorios
La Retrospectiva deja de debatir impresiones subjetivas y pasa a inspeccionar objetivamente el **flujo continuo de valor, la salud del pipeline y la disciplina TBD**:

```
+-----------------------------------------------------------------------------------------+
|                        LOS 3 FOCOS OBLIGATORIOS DE LA RETROSPECTIVA                     |
+----------------------------+----------------------------+-------------------------------+
| 1. SALUD DEL PIPELINE      | 2. DISCIPLINA TBD          | 3. FLUJO DE VALOR             |
+----------------------------+----------------------------+-------------------------------+
| • ¿Cuántas veces falló CI? | • ¿Cuántas integraciones a | • Lead Time desde commit a    |
| • ¿Cuánto tardó el deploy? |   main logramos por día?   |   producción (< 30 min).      |
| • ¿Hubo rollbacks o fallos | • ¿Alguna rama vivió >24h? | • ¿El valor llegó realmente   |
|   en health checks?        | • ¿Uso limpio de Toggles?  |   al usuario final?           |
+----------------------------+----------------------------+-------------------------------+
```

### 14.2. Dinámica de Retrospectiva (Tablero Semáforo en Miro)

| Columna | Tarjetas / Observaciones del Equipo |
| :--- | :--- |
| 🟢 **Lo que funcionó bien en el flujo** | • CI de GitHub Actions ejecuta Pytest y Ruff en menos de 15s.<br>• Auto-deploy a Render funciona sin intervención manual tras el merge.<br>• Integración de ConfigCat permite cambiar el comportamiento de la app en menos de 5s sin hacer deploy. |
| 🟡 **Lo que generó fricción** | • Dependencia de aprobación externa en PRs atómicos retrasó integraciones.<br>• Falta de tablero visual de métricas de negocio para observar conversiones en tiempo real. |
| 🔴 **Lo que rompió el flujo o generó miedo** | • Miedo a activar toggles que tocan transacciones monetarias sin observabilidad.<br>• Presencia de ramas con más de 24 horas de vida debido a tests flaky o falta de sliceado fino. |
| 🛠️ **Acciones de Mejora Acordadas** | **1.** Implementar política estricta de cuarentena inmediata para cualquier test flaky detectado en el pipeline.<br>**2.** Definir dashboard de observabilidad previo a la creación de cualquier Feature Toggle transaccional.<br>**3.** Crear proceso de limpieza automática de Feature Toggles que superen los 14 días de vida (*Toggle Debt Removal*). |

### 14.3. Preguntas Guía del Facilitador
* *¿Qué nos impidió integrar más veces a main?* La falta de confianza en la suite de pruebas cuando aparecen tests inestables y la costumbre de acumular cambios grandes en lugar de hacer micro-commits.
* *¿El auto-deploy nos dio más confianza o más miedo?* Dio confianza técnica en la automatización, pero generó miedo cuando no existen métricas de observabilidad claras para monitorear el comportamiento en producción.
* *¿Los Feature Toggles nos ayudaron o se volvieron deuda?* Ayudaron enormemente a desacoplar el deploy del release, pero se vuelven deuda peligrosa si no tienen fecha de vencimiento y limpieza formal.
* *¿El DoD se respetó realmente?* El DoD técnico se cumplió al 100%, pero el DoD de negocio debe exigir que no se active ningún flag sin telemetría previa.

---

## 🛡️ 15. PROTOCOLO DE LIBERACIÓN SEGURA DE VALOR (SAFE RELEASE POLICY)

Para evitar incidentes en producción, toda liberación mediante Feature Flags sigue un protocolo estructurado en 4 fases:

```
[FASE 0: DARK LAUNCH] ──> [FASE 1: CANARY INTERNO] ──> [FASE 2: CANARY GRADUAL] ──> [FASE 3: GENERAL RELEASE]
   Toggle en OFF (0%)        Solo equipo / Staging        Rollout al 10% - 20%           Rollout al 100%
   Código en producción      Validación de contratos      Monitoreo de SLAs/Métricas     Retiro de Toggle en <14d
```

### 15.1. Cuadro de Mando de Observabilidad para Liberación
Antes de mover un Feature Toggle en ConfigCat, deben estar operativos los siguientes indicadores:
1. **Error Rate (5xx):** Umbral máximo permitido < 0.5%.
2. **Latencia P95:** Umbral máximo < 250 ms en los endpoints críticos.
3. **Health Check:** Monitoreo periódico cada 30 segundos (`/health` con código HTTP 200).
4. **Tasa de Abandono / Error de Negocio:** Disparador de alerta si se detectan anomalías funcionales.

### 15.2. Criterios de Parada y Rollback Instantáneo
* **Criterio de Éxito (100% ON):** Si tras 24 horas en FASE 2 la tasa de error es < 0.2%, la latencia se mantiene estable y la métrica de negocio es positiva, se eleva al 100% para todos los usuarios.
* **Criterio de Rollback Instantáneo:** Si en cualquier momento tras mover el toggle el Error Rate supera el 1.5% o el health check falla, **se apaga el toggle en ConfigCat inmediatamente (tiempo de reacción < 10 segundos)** sin esperar un redespliegue de código.

---

## 💼 16. RESOLUCIÓN TÉCNICA DEL CASO DE ESTUDIO
### *"La funcionalidad de 'Pagos Express' ya está en main, pero nadie se atreve a activarla"*

A partir de los 7 hechos problemáticos identificados en el Taller 6, el equipo estableció las siguientes resoluciones y acuerdos vinculantes:

| # | Hecho Problemático | Diagnóstico y Riesgo Asociado | Decisión y Plan de Acción Inmediato |
| :-: | :--- | :--- | :--- |
| **1** | **El PO quiere activar el toggle al 20% este viernes por presión de marketing.** | Lanzar un cambio financiero un viernes sin observabilidad viola las buenas prácticas de resiliencia y pone en riesgo los ingresos del negocio. | **Decisión: NO activar el viernes.** Se acuerda con el PO y Marketing posponer la activación al martes por la mañana (horario laboral protegido) tras completar las métricas de monitoreo durante el lunes. |
| **2** | **El último deploy falló el health check 11 min y requirió rollback manual.** | Un auto-deploy con health check fallido indica falta de pruebas de humo o un timeout en la conexión a la base de datos durante el arranque. | **Acción:** Corregir el endpoint de `/health` para incluir timeout de 2s a MongoDB. Configurar en Render reinicio automático controlado ante fallos de inicio para evitar rollbacks manuales. |
| **3** | **Hay 3 Feature Toggles antiguos con más de 45 días activos sin limpiar.** | Acumulación de deuda técnica de código (*Toggle Debt*), lógica condicional muerta y riesgo de efectos secundarios imprevistos. | **Acción:** Crear de inmediato 3 issues de refactorización para retirar los flags obsoletos (`cleanup-toggle-*`) en el próximo Sprint. Se establece regla estricta: ningún toggle vive más de 14 días tras llegar al 100%. |
| **4** | **En el Sprint actual solo se lograron 4 integraciones a main.** | Incumplimiento de la regla fundamental de TBD (mínimo 1 integración diaria por desarrollador). Causa: historias demasiado grandes. | **Acción:** Aplicar la técnica de Story Slicing en todas las historias del backlog. Ninguna historia podrá tener una estimación mayor a 1 día de desarrollo. |
| **5** | **Rama viva 4 días por un test flaky en CI.** | Los tests intermitentes destruyen la confianza del equipo en el pipeline y generan acumulación masiva de ramas. | **Acción: Política de Tolerancia Cero a Tests Flaky.** El test flaky se aisla en cuarentena inmediatamente (desactivado temporalmente con issue prioritario para corregirlo en <24h). La rama se desbloquea y fusiona. |
| **6** | **No existe métrica clara de conversión o error de pagos.** | Volar a ciegas. Si los pagos fallan, el equipo no lo sabrá hasta recibir quejas de clientes furiosos. | **Acción Obligatoria:** Implementar telemetría con contadores de transacciones exitosas vs. fallidas antes de permitir cualquier movimiento del toggle. Esta métrica se incorpora formalmente al Definition of Ready (DoR). |
| **7** | **Negocio anunció internamente que "Pagos Express ya está listo".** | Confusión entre "Código Desplegado (Deploy)" y "Funcionalidad Liberada (Release)". | **Acción:** Educar a los stakeholders de negocio en la distinción: *Deploy $\neq$ Release*. Un ítem solo está "Listo para el Usuario" cuando el toggle está al 100% y validado por el PO. |

---

## 🎯 17. CIERRE Y COMPROMISOS DEL TALLER 6

### 17.1. Checklist de Madurez en Continuous Deployment
- [x] Sprint Review adaptado a demostraciones en producción real mediante Feature Toggles.
- [x] Sprint Retrospective enfocada en salud de pipeline, disciplina TBD y flujo de valor.
- [x] Práctica de liberación segura de valor documentada y probada con ConfigCat y Render.
- [x] Políticas de contingencia, cuarentena de tests flaky y control de deuda de toggles formalizadas.
- [x] Scrum + TBD Playbook actualizado a la **Versión 3.0**.

### 17.2. Ronda Final del Equipo:
> **"En una frase: ¿Qué cambia en nuestro próximo Review y Retro después de este taller?"**  
> *"A partir de hoy, nuestro Sprint Review dejará de juzgar suposiciones locales para evaluar valor medible en producción con Feature Toggles, y nuestra Retrospectiva será el guardián científico de la salud de nuestro pipeline y la disciplina diaria de Trunk-Based Development."*



