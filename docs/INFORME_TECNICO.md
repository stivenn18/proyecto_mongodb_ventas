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
