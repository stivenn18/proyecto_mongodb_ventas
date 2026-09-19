# DOCUMENTACIÓN TÉCNICA E INFORME DE ARQUITECTURA DE DATOS
## Parcial de Base de Datos - Primer Corte
### Sistema de Ventas OLTP/OLAP con MongoDB Atlas y Python

---

## 📋 INFORMACIÓN DEL PROYECTO
- **Materia:** Base de Datos (Primer Corte)
- **Tecnologías:** MongoDB Atlas (Replica Set distribuido M0), Python 3.14, PyMongo, Faker, python-dotenv, MongoDB Compass.
- **Clúster Atlas:** `cluster0.ms3andh.mongodb.net`
- **Base de Datos:** `ventas_db`

---

## 🎯 1. OBJETIVOS Y ALCANCE

1. **Arquitectura Distribuida:** Configuración y conexión segura mediante TLS/SRV a un clúster de base de datos distribuido en la nube (MongoDB Atlas Replica Set >= 3 nodos).
2. **Modelado Transaccional (OLTP):** Diseño e implementación de esquemas normalizados y optimizados para operaciones CRUD de alta concurrencia (`clientes`, `productos`, `ventas`).
3. **Pipeline de Ingesta Masiva (Faker):** Generación e inserción por lotes (*Batch Ingestion*) de más de 50,000 transacciones con datos sintéticos realistas contextualizados para Colombia.
4. **Transformación ETL (OLTP -> OLAP):** Procesamiento y desnormalización de datos hacia un Modelo Dimensional (Esquema en Estrella) en la colección `ventas_analiticas` mediante un **Aggregation Pipeline** nativo.
5. **Optimización e Indexación Compuesta:** Creación de índices compuestos para optimizar operaciones de filtrado (`$match`), ordenamiento (`$sort`) y agregación (`$group`), reduciendo la complejidad de O(N) a O(log N).
6. **Benchmarking de Rendimiento:** Medición de latencias y tiempos de respuesta de 5 consultas analíticas complejas sobre 149,655 registros analíticos.

---

## 🏗 2. ARQUITECTURA DE DATOS IMPLEMENTADA

```
+-----------------------------------------------------------------------------------+
|                            CAPA TRANSACCIONAL (OLTP)                              |
|                                                                                   |
|  +--------------------+    +--------------------+    +-------------------------+  |
|  |     clientes       |    |     productos      |    |         ventas          |  |
|  |--------------------|    |--------------------|    |-------------------------|  |
|  | _id (ObjectId)     |    | _id (ObjectId)     |    | _id (ObjectId)          |  |
|  | codigo_cliente     |    | sku (Unique Index) |    | numero_factura          |  |
|  | nombre             |    | nombre             |    | cliente_id (FK Ref)     |  |
|  | email (Unique Idx) |    | categoria          |    | fecha_venta (Index)     |  |
|  | telefono           |    | precio_unitario    |    | total                   |  |
|  | direccion (embed)  |    | stock              |    | metodo_pago             |  |
|  | fecha_registro     |    | proveedor          |    | estado                  |  |
|  | activo             |    | fecha_creacion     |    | items: [                |  |
|  +--------------------+    +--------------------+    |   {producto_id, cant,   |  |
|                                                      |    precio, subtotal}    |  |
|                                                      | ]                       |  |
|                                                      +-------------------------+  |
+-----------------------------------------------------------------------------------+
                                          |
                                          | Aggregation Pipeline ETL
                                          | ($lookup + $unwind + $project + $merge)
                                          v
+-----------------------------------------------------------------------------------+
|                             CAPA ANALÍTICA (OLAP)                                 |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                         ventas_analiticas (Fact Table)                      |  |
|  |-----------------------------------------------------------------------------|  |
|  | _id (ObjectId)                                                              |  |
|  | fecha_venta (ISODate) | anio (int) | mes (int) | dia (int)                   |  |
|  | cliente: { id, nombre, ciudad, segmento: ('Premium'|'Frecuente'|'Regular') }|  |
|  | producto: { id, nombre, categoria, marca }                                  |  |
|  | cantidad (int) | precio_unitario (float) | total_venta (float)               |  |
|  | ganancia_estimada (float: total_venta * 0.15)                                |  |
|  | numero_factura | metodo_pago | estado                                       |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 💡 3. JUSTIFICACIONES TÉCNICAS DE ARQUITECTURA

### 3.1. Ingesta Masiva por Lotes (Batch Insert)
> *"Se implementó el patrón de Batch Insert con tamaño de chunk de 1,000 documentos. Esta decisión arquitectónica reduce la sobrecarga de ida y vuelta de red (network round-trips) y el consumo de memoria RAM, alineándose con las mejores prácticas de procesamiento de datos a escala."*
- **Tolerancia a Duplicados:** Se configuró el parámetro `ordered=False` en `insert_many()`. Esto permite que si un documento genera una colisión en un índice único (`E11000`), el motor continúe insertando el resto de documentos del lote sin abortar la operación completa.

### 3.2. Transformación ETL con Aggregation Pipeline
> *"Se utilizó el Aggregation Pipeline nativo de MongoDB con las etapas `$lookup` (JOIN) y `$unwind` para transformar datos normalizados (OLTP) en un modelo dimensional desnormalizado (OLAP). Se habilitó `allowDiskUse: true` para garantizar escalabilidad en operaciones que superan los 100MB de RAM."*
- **Desnormalización Eficiente:** La etapa `$unwind` aplana los arrays embebidos de ítems, permitiendo que cada fila en la colección OLAP represente un grano atómico (producto vendido en una transacción específica).
- **Enriquecimiento al Vuelo:** Mediante expresiones condicionales `$cond`, se calculó la segmentación de clientes (`Premium` para ventas >= $5,000,000, `Frecuente` para >= $1,000,000 y `Regular` para inferiores).

### 3.3. Estrategia de Indexación Compuesta
> *"Se implementó una estrategia de Índices Compuestos (`idx_fecha`, `idx_categoria_venta`, `idx_segmento_ciudad`, `idx_estado_segmento_ciudad`) que permite resolver operaciones de filtrado y ordenamiento sin escaneos completos de colección, reduciendo la complejidad de O(N) a O(log N)."*
- **Estructura B-Tree:** Al indexar campos de filtrado y ordenamiento conjunto (como `estado` + `cliente.segmento` + `cliente.ciudad`), el motor utiliza el índice para resolver la consulta (*Covered Query / Index Scan*), evitando costosos *COLLSCAN* sobre cientos de miles de registros.

---

## 📊 4. RESULTADOS DE EJECUCIÓN Y MÉTRICAS REALES

### 4.1. Resumen de Ingesta y ETL
- **Tiempo de Ingesta OLTP:** `208.17 segundos`
  - Clientes insertados: `5,001`
  - Productos insertados: `998`
  - Ventas insertadas: `50,001`
- **Tiempo de Ejecución ETL:** `44.70 segundos`
  - Registros analíticos consolidados: `149,655 documentos`

### 4.2. Benchmarking de Consultas Analíticas

| # | Consulta Analítica | Pipeline Clave | Filas Retornadas | Latencia Medida | Cumplimiento (<500ms) |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | **Ventas totales mensuales** | `$group (anio, mes)` + `$sort` | 13 | **225.10 ms** | ✅ Óptimo |
| **2** | **Top 5 Productos por Categoría** | `$group` + `$sort` + `$push` + `$slice` | 6 | **292.61 ms** | ✅ Óptimo |
| **3** | **Rendimiento por Segmento y Ciudad** | `$match (Completada)` + `$group` + `$sort` | 2,473 | **702.60 ms** | ⚠️ Gran volumen |
| **4** | **Ticket Promedio por Método de Pago** | `$match` + `$group ($avg)` + `$sort` | 6 | **307.59 ms** | ✅ Óptimo |
| **5** | **Ventas por Día de la Semana** | `$addFields ($dayOfWeek)` + `$group` | 7 | **405.51 ms** | ✅ Óptimo |

- **Latencia Promedio Global:** **386.68 ms** (Objetivo general < 500 ms alcanzado con creces).
- **Volumen Analizado:** **149,655 registros**.

---

## 🛠 5. MANUAL DE OPERACIÓN Y COMANDOS ÚTILES

### 5.1. Ejecución de la Solución Paso a Paso
```bash
# 1. Instalar librerías requeridas
pip install -r requirements.txt

# 2. Validar conexión con Atlas
python conexion.py

# 3. Crear esquema e índices transaccionales
python scripts/crear_estructura.py

# 4. Ingesta masiva sintética (50,000+ ventas)
python scripts/generar_datos_masivos.py

# 5. Ejecutar pipeline ETL a modelo estrella
python scripts/transformar_oltp_a_olap.py

# 6. Ejecutar benchmarking de rendimiento
python scripts/benchmarking_consultas.py
```

### 5.2. Comandos de Verificación en MongoDB Compass / Shell (mongosh)
```javascript
// Ver colecciones
show collections

// Contar registros de cada colección
db.clientes.countDocuments({})
db.productos.countDocuments({})
db.ventas.countDocuments({})
db.ventas_analiticas.countDocuments({})

// Inspeccionar índices creados
db.ventas.getIndexes()
db.ventas_analiticas.getIndexes()

// Analizar plan de ejecución de una consulta
db.ventas_analiticas.find({
  "estado": "Completada",
  "cliente.segmento": "Premium"
}).explain("executionStats")
```

---

## ✅ 6. CHECKLIST DE ENTREGABLES CUMPLIDOS

- [x] Cluster de base de datos distribuida operativo (>= 3 nodos - Atlas Replica Set).
- [x] Modelo de datos transaccional (OLTP) y analítico (OLAP).
- [x] Pipeline de ingesta de datos (generación masiva con Faker >= 50,000 ventas).
- [x] Procesamiento de datos (Aggregation Pipeline ETL con `$lookup`, `$unwind`, `$project`, `$merge`).
- [x] Consultas analíticas optimizadas con benchmarking de latencia.
- [x] Estrategia de indexación compuesta (O(N) -> O(log N)).
- [x] Documentación técnica e informe arquitectónico completado.
- [x] Pipeline de Integración y Entrega Continua (CI/CD) con GitHub Actions.
- [x] Estrategia de Trunk-Based Development (TBD) con protección de rama `main` (Rulesets).
- [x] Contenedorización con Docker y publicación automatizada en GitHub Container Registry (GHCR).

---

## 🚀 7. IMPLEMENTACIÓN DE CI/CD Y TRUNK-BASED DEVELOPMENT (TBD)

### 7.1. Fundamentos y Filosofía de Trunk-Based Development
En este proyecto se implementó el modelo de ramificación **Trunk-Based Development (TBD)**. A diferencia de modelos tradicionales con ramas de larga duración (como GitFlow), TBD promueve:
- **Tronco Principal (`main`):** La rama `main` se mantiene en todo momento en un estado desplegable y estable (*always releasable*).
- **Ramas Efímeras de Corta Duración (*Short-Lived Branches*):** Cualquier cambio, corrección o funcionalidad se desarrolla en ramas temporales (`test/*` o `feat/*`) cuya vida útil no supera unas pocas horas o un día.
- **Validación Rápida y Fusión Frecuente:** El código se valida automáticamente mediante pipelines de CI antes de integrarse al tronco principal mediante Pull Requests pequeños y atómicos.

```
Trunk-Based Development Workflow:
-------------------------------------------------------------------------------------
[main] ────────────────●───────────────────────────────────● (Deploy GHCR) ─────────>
                       \                                  /
                        \                                / Pull Request + Status Checks (test)
  [short-lived branch]   ●───────● (Commit & Push) ─────●
                                 |
                                 v
                          [Job: test (ruff + pytest)]
```

---

### 7.2. Pipeline de CI/CD en GitHub Actions (`.github/workflows/ci.yaml`)

Se diseñó un pipeline modular dividido en **dos etapas (Jobs)** con el principio de separación de responsabilidades y mínimo privilegio:

```yaml
name: Test and Build

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest

      - name: Run ruff linter
        run: |
          pip install ruff==0.8.1
          ruff check .

      - name: Run tests
        run: |
          pytest tests.py

  build_and_push:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write # <-- Permiso para subir a GHCR

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v7
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
```

#### Justificación Arquitectónica del Pipeline:
1. **Job `test` (Feedback Inmediato):** Se ejecuta en **todos los Pull Requests** y pushes hacia cualquier rama vinculada. Realiza análisis estático de código con `ruff` y ejecuta la suite de pruebas unitarias (`pytest`). Si este job falla, la integración se bloquea de inmediato.
2. **Job `build_and_push` (Despliegue Continuo Condicional):** Cuenta con la condición `needs: test` e `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`. Solo se dispara cuando el código ha sido aprobado y fusionado en `main`, evitando compilar o subir imágenes Docker innecesarias provenientes de ramas secundarias o pruebas fallidas.
3. **Mínimo Privilegio de Seguridad:** El permiso `packages: write` se configuró exclusivamente a nivel del job `build_and_push`, mientras que el job `test` opera únicamente con `contents: read`.

---

### 7.3. Suite de Pruebas Unitarias y Calidad de Código

* **Pruebas Automatizadas ([`tests.py`](file:///c:/Users/stive/Downloads/proyecto_mongodb_ventas/tests.py)):** Se implementó una suite con `unittest.mock` para simular las respuestas del motor MongoDB Atlas, asegurando que las funciones críticas del sistema se validen de forma aislada y determinista sin requerir conectividad externa en el runner de CI.
* **Control de Calidad y Linting ([`pyproject.toml`](file:///c:/Users/stive/Downloads/proyecto_mongodb_ventas/pyproject.toml)):** Se estandarizó el formato PEP 8 y se configuró el linter `ruff` para auditar la sintaxis, imports ordenados al inicio de archivo y eliminación de variables huérfanas en todos los módulos del repositorio.
* **Contenedorización ([`Dockerfile`](file:///c:/Users/stive/Downloads/proyecto_mongodb_ventas/Dockerfile)):** Construcción ligera basada en `python:3.11-slim` que empaqueta la aplicación lista para su ejecución en entornos de producción y despliegue a GHCR.

---

### 7.4. Estrategia de Protección de Ramas (GitHub Rulesets)

Para forzar el cumplimiento del flujo Trunk-Based Development, se configuró un **Ruleset / Branch Protection** en GitHub sobre la rama `main` con las siguientes políticas:

| Regla Configurada | Objetivo / Impacto |
| :--- | :--- |
| **Require a pull request before merging** | Prohíbe los commits directos a `main`, forzando la creación de PRs y revisión formal. |
| **Require status checks to pass (`test`)** | Exige que el job de análisis y pruebas (`test`) pase satisfactoriamente antes de permitir el merge. |
| **Require branches to be up to date** | Garantiza que la rama secundaria contenga el último estado de `main` antes de integrarse. |
| **Block force pushes** | Evita la sobreescritura destructiva o alteración del historial en el tronco principal. |
| **Bypass List (Repository Admin)** | Permite al administrador del repositorio realizar la fusión documentada para mantener la fluidez operativa. |

---

### 7.5. Verificación Práctica y Evidencia de Ejecución

1. **Creación de Rama de Verificación:**
   ```bash
   git checkout -b test/verificar-branch-protection
   ```
2. **Commit y Push:** Se introdujo un cambio controlado en `conexion.py` y se publicó la rama en GitHub.
3. **Bloqueo y Aislamiento en Pull Request:**
   - Al abrir el PR, GitHub activó el job `test` y omitió (*skipped*) el job `build_and_push`.
   - La interfaz de GitHub bloqueó el botón de merge directo, validando el cumplimiento estricto del Ruleset.
4. **Fusión y Limpieza (*Housekeeping*):**
   - Se completó el merge a `main`.
   - Se verificó el disparo automático de `build_and_push` publicando la imagen en `ghcr.io`.
   - Se eliminó la rama efímera local y remotamente para mantener el repositorio limpio:
     ```bash
     git checkout main
     git pull origin main
     git branch -D test/verificar-branch-protection
     git push origin --delete test/verificar-branch-protection
     ```

