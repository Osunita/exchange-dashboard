# Dashboard de Tipos de Cambio

Dashboard web interactivo para explorar la evolución histórica de tipos de cambio entre divisas.
Construido con **pandas** (procesamiento) y **Streamlit** (interfaz), consumiendo la API pública
de [Frankfurter](https://frankfurter.dev/) (tasas de referencia del BCE, sin autenticación).

> No convierte importes entre divisas, no da recomendaciones financieras y no tiene usuarios ni
> autenticación: es una herramienta de exploración y visualización.

## Estructura

```
.
├── app.py                      # Punto de entrada Streamlit (interfaz)
├── src/
│   ├── frankfurter_client.py   # Llamadas HTTP a la API de Frankfurter
│   └── data.py                 # Parseo a pandas + caché en memoria (TTL 6 h)
├── tests/
│   ├── test_frankfurter_client.py
│   └── test_data.py
├── requirements.txt            # Dependencias de producción
├── requirements-dev.txt        # Dependencias de desarrollo (pytest)
├── .streamlit/config.toml      # (opcional) tema visual
└── README.md
```

No hay base de datos ni escritura en disco: los datos se cachean en memoria con
`st.cache_data(ttl=21600)` (6 horas), compatible con el sistema de archivos efímero de
Streamlit Community Cloud.

## Ejecución local

Requisito: Python 3.9+ (probado con 3.13).

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

streamlit run app.py
```

La app abre en <http://localhost:8501> con valores por defecto: divisa base **EUR**,
comparación **USD** y **GBP**, rango de los **últimos 90 días**.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Los tests mockean la red: no se necesita conexión para ejecutarlos.

## Despliegue en Streamlit Community Cloud

1. Sube este repositorio a GitHub (incluye `requirements.txt` en la raíz).
2. Ve a <https://share.streamlit.io> → **New app**.
3. Selecciona el repositorio, la rama (p. ej. `main`) y el archivo de la app: `app.py`.
4. **Deploy**.

No se necesita ninguna configuración adicional, variables de entorno ni secrets: la API de
Frankfurter no requiere autenticación.

## Notas de uso

- **API no disponible**: se muestra un mensaje de error y la app sigue funcionando.
- **Divisa no soportada**: se muestra un aviso.
- **Sin divisas de comparación seleccionadas**: se pide seleccionar al menos una.
- **Sin datos en el rango elegido**: se muestra un aviso informativo.

## Limitaciones (fuera de alcance deliberado)

- Conversión de importes entre divisas.
- Predicciones o análisis de tendencias.
- Autenticación o guardado de configuración por usuario.
