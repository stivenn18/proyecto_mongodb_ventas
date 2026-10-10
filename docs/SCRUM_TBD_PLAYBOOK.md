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

### 13.4. Protocolo Oficial del Sprint Review (Caso Pagos Express)
* **Demostración transparente:** Se inicia la demo con el Feature Toggle `pagos-express-v1` en **OFF (estado real actual)**.
* **Activación controlada:** Se activa temporalmente **únicamente para el equipo o usuario de prueba** y se muestra el flujo funcional completo.
* **Declaración Oficial del Product Owner (PO):**
  > *"La funcionalidad está técnicamente lista y desplegada, pero todavía no la hemos liberado a usuarios reales porque necesitamos definir métricas de observación y resolver riesgos de estabilidad del pipeline. La campaña de marketing se pausará o se ajustará."*
* **Compromiso vinculante:** **Se evita terminantemente comprometer una fecha de activación al 20% en el Sprint Review.**

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
| 🟢 **Lo que funcionó bien en el flujo** | • CI de GitHub Actions ejecuta Pytest y Ruff en menos de 15s.<br>• Auto-deploy a Render funciona sin intervención manual tras el merge.<br>• Integración de ConfigCat permite cambiar el comportamiento de la app en menos de 5s sin hacer deploy.<br>• DoD de 3 dimensiones cumplido a nivel técnico. |
| 🟡 **Lo que generó fricción** | • Dependencia de aprobación externa en PRs atómicos retrasó integraciones.<br>• Falta de tablero de métricas de negocio para observar conversiones en tiempo real.<br>• Solo 4 integraciones a main en el sprint. |
| 🔴 **Lo que rompió el flujo o generó miedo** | • Presión de marketing para activar toggle un viernes sin observabilidad.<br>• Rama viva 4 días por culpa de un test flaky en CI.<br>• Fallo de health check de 11 minutos y rollback manual en deploy anterior.<br>• Deuda técnica de 3 toggles antiguos >45 días sin limpiar. |
| 🛠️ **Acciones de Mejora Acordadas (Solución Oficial)** | **Acción 1:** Arreglar el test flaky en las próximas 24 h (máxima prioridad).<br>**Acción 2:** Crear un dashboard mínimo de métricas de pagos (errores + conversión) antes de cualquier activación.<br>**Acción 3:** Limpiar o eliminar los 3 toggles antiguos en este mismo sprint. |

### 14.3. Acuerdo Vinculante del Equipo
> 📌 **Acuerdo de Estabilidad del Pipeline:**  
> **"No se activará ningún toggle nuevo a usuarios reales hasta que el health check no haya fallado en los últimos 7 deploys."**

### 14.4. Preguntas Guía del Facilitador
* *¿Qué nos impidió integrar más veces a main?* Historias demasiado grandes y bloqueo de 4 días por test flaky.
* *¿El auto-deploy nos dio más confianza o más miedo?* Confianza técnica en la rapidez, pero miedo cuando falta observabilidad o falló el health check.
* *¿Los Feature Toggles nos ayudaron o se volvieron deuda?* Ayudaron a desacoplar el deploy del release, pero los 3 toggles viejos demuestran acumulación de deuda técnica si no se limpian.
* *¿El DoD se respetó realmente?* Se cumplió a nivel técnico (código en main, tests en verde, deploy a Render), pero la experiencia madura exige que el DoD de negocio impida la activación sin telemetría.

---

## 🛡️ 15. ESTRATEGIA DE LIBERACIÓN SEGURA (DECISIÓN FINAL Y PLAN ACORDADO)

### 15.1. Decisión Final:
**NO SE ACTIVA EL 20% ESTE VIERNES.**

### 15.2. Plan Acordado de 5 Pasos:
1. **Resolver test flaky + limpiar toggles viejos** (*esta semana*).
2. **Implementar métricas básicas de error y conversión** (*máximo 3 días*).
3. **Activar primero solo para usuarios internos / equipo** (*1-2 días de observación*).
4. **Si todo está estable $\rightarrow$ subir al 5% $\rightarrow$ 20% con observación de 48 horas en cada paso.**
5. **Criterio de rollback automático:** **Cualquier aumento $> 0,5\%$ en errores de pago.**

```
[PLAN DE 5 PASOS: LIBERACIÓN SEGURA]
[Paso 1: Test Flaky + Toggles Viejos] ──> [Paso 2: Métricas Error/Conversión (3d)]
                  │
                  ▼
[Paso 3: Usuarios Internos (1-2d)] ──> [Paso 4: Rollout Gradual: 5% (48h) ──> 20% (48h)]
                  │
                  ▼
[Paso 5: Rollback Automático Inmediato si Error Rate > 0.5%]
```

### 15.3. Resumen de la Decisión Madura:
> **Resumen Ejecutivo:** *Se protege la confianza del pipeline y la disciplina TBD por encima de la presión comercial de corto plazo. Se comunica con transparencia al stakeholder y se define un camino claro y seguro de liberación.*  
>  
> *Este caso combina presión de negocio, deuda técnica, fallos recientes de pipeline, falta de métricas y ruptura de disciplina TBD. Obliga al equipo a negociar, priorizar y aplicar todo lo aprendido en los cuatro talleres.*

---

## 💼 16. RESOLUCIÓN DETALLADA DE LOS 7 HECHOS PROBLEMÁTICOS
### *"La funcionalidad de 'Pagos Express' ya está en main, pero nadie se atreve a activarla"*

| # | Hecho Problemático | Diagnóstico y Riesgo | Decisión Madura y Acción Concreta |
| :-: | :--- | :--- | :--- |
| **1** | **El PO quiere activar el toggle al 20% este viernes por presión de campaña de marketing.** | Riesgo operativo y reputacional severo al liberar pasarela de pagos sin telemetría un fin de semana. | **NO ACTIVAR EL VIERNES.** El PO frena la campaña y comunica con transparencia: *"La funcionalidad está lista técnicamente pero no liberada a usuarios reales hasta definir métricas y estabilizar el pipeline"*. |
| **2** | **El último deploy falló el health check 11 min y requirió rollback manual.** | Pérdida de confianza en la resiliencia del auto-deploy en Render. | **ACUERDO VINCULANTE:** No se activará ningún toggle nuevo a usuarios reales hasta que el health check no haya fallado en los últimos 7 deploys. Se optimiza el health check con timeout seguro. |
| **3** | **Hay 3 Feature Toggles antiguos con más de 45 días activos sin limpiar.** | Deuda técnica acumulada, caminos de código muertos y complejidad innecesaria. | **ACCIÓN 3 DE LA RETRO:** Limpiar o eliminar los 3 toggles antiguos en este mismo sprint. |
| **4** | **En el sprint actual solo se lograron 4 integraciones a main.** | Ruptura de la disciplina básica de Trunk-Based Development. | **ACCIÓN:** Retomar Story Slicing estricto. Ramas efímeras con vida $< 24$ horas y micro-PRs atómicos. |
| **5** | **Rama viva 4 días por test flaky en CI.** | Los tests intermitentes bloquean la integración continua y generan miedo. | **ACCIÓN 1 DE LA RETRO (MÁXIMA PRIORIDAD):** Arreglar el test flaky en las próximas 24 horas. |
| **6** | **No existe ninguna métrica clara de conversión o error de pagos.** | Operación a ciegas que impide evaluar el impacto de la funcionalidad. | **ACCIÓN 2 DE LA RETRO:** Implementar dashboard mínimo de métricas de pagos (errores + conversión) en máximo 3 días antes de cualquier activación. |
| **7** | **Negocio anunció que "Pagos Express ya está listo".** | Confusión entre "Deploy" (despliegue técnico) y "Release" (liberación comercial). | **ACCIÓN:** Educación de stakeholders. Se aclara que el código está en producción protegido por toggle pero el release comercial requiere validación previa con usuarios internos. |

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



