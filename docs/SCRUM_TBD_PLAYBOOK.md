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
