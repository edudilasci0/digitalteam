# Configuración del Motor de Decisión

Este directorio contiene los archivos de configuración del Motor de Decisión.

## Archivos de configuración

- `config.yaml`: Archivo principal de configuración con todos los parámetros del sistema.
- `credentials.json`: Credenciales para la integración con Google Sheets (no incluido en el repositorio por seguridad).

## Configuración de Google Sheets

Para configurar la integración con Google Sheets:

1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita la API de Google Sheets
3. Crea una cuenta de servicio y descarga las credenciales en formato JSON
4. Guarda el archivo como `credentials.json` en este directorio
5. Comparte las hojas de cálculo con la dirección de correo de la cuenta de servicio

## Personalización

Puedes personalizar la configuración editando el archivo `config.yaml`. Los principales parámetros que puedes ajustar son:

- Rutas de directorios para datos y salidas
- Parámetros de análisis (frecuencia, periodos mínimos)
- Configuración de modelos y simulaciones
- Opciones de visualización
- Configuración de integración con Google Sheets y Power BI

## Seguridad

Por razones de seguridad, los archivos de credenciales (`credentials.json` y `token.json`) no deben incluirse en el control de versiones. Asegúrate de añadirlos a tu archivo `.gitignore`. 