# Analytics API — Datalake Películas

API REST construida con **FastAPI** que ejecuta consultas analíticas sobre el datalake usando **AWS Athena**.

---

## Endpoints disponibles

### 🎬 Películas  `/api/peliculas`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/top-calificadas` | Top 10 películas mejor calificadas |
| GET | `/completa` | Vista completa con género y director (paginada) |
| GET | `/actores-top` | Top 10 actores con más películas |
| GET | `/generos` | Conteo de películas por género |
| GET | `/directores-top` | Directores con más películas |

### 👥 Usuarios  `/api/usuarios`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/por-pais` | Usuarios agrupados por país |
| GET | `/peliculas-vistas-top` | Usuarios con más películas vistas |
| GET | `/resumen` | Estadísticas generales de usuarios |

### 💬 Foros  `/api/foros`
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/mas-activos` | Top 10 foros por cantidad de mensajes |
| GET | `/actividad` | Vista completa con título, votos y mensajes (paginada) |
| GET | `/resumen` | Estadísticas globales de foros |
| GET | `/por-pelicula/{movie_id}` | Foros de una película específica |

---

## Deploy en la VM analítica

### Opción A — Docker (recomendado)

```bash
# 1. Copiar la carpeta a la VM analítica
scp -r analytics-api/ ubuntu@<IP_VM_ANALITICA>:~/

# 2. En la VM analítica
cd ~/analytics-api

# 3. Levantar
docker compose up -d --build

# 4. Verificar
curl http://localhost:8000/health
```

### Opción B — Sin Docker

```bash
cd ~/analytics-api
pip install -r requirements.txt

# Configurar variables de entorno
export ATHENA_DATABASE=glue_datalake
export ATHENA_S3_OUTPUT=s3://peliculas-datalake/athena-results/
export AWS_REGION=us-east-1

# Iniciar el servidor
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Credenciales AWS

La VM analítica necesita permisos para **Athena** y **S3**.  
Las dos formas de configurarlo:

### ✅ Opción recomendada — IAM Role (si la VM es una EC2)
Asigna un **Instance Profile** con esta política mínima a la EC2:
```json
{
  "Effect": "Allow",
  "Action": [
    "athena:StartQueryExecution",
    "athena:GetQueryExecution",
    "athena:GetQueryResults",
    "s3:GetObject",
    "s3:PutObject",
    "s3:ListBucket",
    "glue:GetTable",
    "glue:GetDatabase"
  ],
  "Resource": "*"
}
```

### Opción alternativa — Variables de entorno
Descomentar en `docker-compose.yml`:
```yaml
- AWS_ACCESS_KEY_ID=AKIA...
- AWS_SECRET_ACCESS_KEY=...
```

---

## Documentación interactiva

Una vez corriendo, accede a:  
- **Swagger UI**: `http://<IP_VM>:8000/docs`  
- **ReDoc**: `http://<IP_VM>:8000/redoc`

---

## Prerrequisitos en Athena

Antes de usar la API, asegúrate de haber creado las vistas en Athena:

```sql
-- Vista foros actividad
CREATE OR REPLACE VIEW glue_datalake.vista_foros_actividad AS
SELECT
    ms.threadid AS foro_id,
    COUNT(ms.id) AS total_mensajes
FROM glue_datalake.messages ms
GROUP BY ms.threadid;

-- Vista películas completa
CREATE OR REPLACE VIEW glue_datalake.vista_peliculas_completa AS
SELECT
    m.id AS movie_id, m.title, m.year, m.rating,
    g.name AS genero,
    d.name AS director
FROM glue_datalake.movies m
LEFT JOIN glue_datalake.movie_genres mg   ON m.id = mg.movie_id
LEFT JOIN glue_datalake.genres g          ON mg.genre_id = g.id
LEFT JOIN glue_datalake.movie_directors md ON m.id = md.movie_id
LEFT JOIN glue_datalake.directors d       ON md.director_id = d.id;
```
