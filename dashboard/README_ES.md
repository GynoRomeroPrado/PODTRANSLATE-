# Panel de Administración PodTranslate

Panel de administración moderno para la plataforma PodTranslate con soporte multiidioma (Español/Inglés).

## Características

- **Multiidioma**: Soporte completo para Español (predeterminado) e Inglés
- **Selector de Idioma**: Cambio fácil entre idiomas en tiempo real
- **Panel de Control**: Métricas en tiempo real, gráficos y actividad reciente
- **Podcasts**: Crear, editar y administrar programas de podcast
- **Episodios**: Seguimiento de estado de episodios y metadatos
- **Transcripciones**: Monitoreo de trabajos de transcripción con progreso en vivo
- **Distribución**: Estado de publicación multiplataforma
- **Analíticas**: Información detallada de rendimiento con Recharts
- **Configuración**: Perfil de usuario, claves API, notificaciones, idiomas

## Stack Tecnológico

- React 18 con hooks
- Vite para builds rápidos
- TailwindCSS para estilos
- TanStack Query para obtención de datos
- Zustand para gestión de estado
- React Router para navegación
- Recharts para visualizaciones
- react-i18next para internacionalización

## Instalación

```bash
cd dashboard
npm install
```

## Desarrollo

```bash
npm run dev
```

El dashboard estará disponible en http://localhost:5173

## Cambio de Idioma

El idioma se puede cambiar de dos formas:

1. **Selector de Idioma**: Haz clic en el selector de idioma en la esquina inferior izquierda del sidebar o en la página de login
2. **Preferencia del Navegador**: El sistema detecta automáticamente el idioma del navegador

El idioma predeterminado es **Español**.

##  Idiomas Soportados

- 🇪🇸 Español (Predeterminado)
- 🇺🇸 English

## Construcción

```bash
npm run build
```

La salida estará en el directorio `dist/`.

## Variables de Entorno

Crea un archivo `.env`:

```env
VITE_API_URL=http://localhost:3000/api/v1
```

## Estructura del Proyecto

```
dashboard/
├── public/              # Recursos estáticos
├── src/
│   ├── components/      # Componentes reutilizables
│   │   ├── Layout.jsx           # Layout principal con sidebar
│   │   └── LanguageSelector.jsx # Selector de idioma
│   ├── lib/             # Utilidades y cliente API
│   │   ├── api.js       # Métodos API
│   │   └── utils.js     # Funciones auxiliares
│   ├── pages/           # Componentes de página
│   │   ├── Dashboard.jsx
│   │   ├── Podcasts.jsx
│   │   ├── Episodes.jsx
│   │   ├── Transcriptions.jsx
│   │   ├── Distribution.jsx
│   │   ├── Analytics.jsx
│   │   ├── Settings.jsx
│   │   └── Login.jsx
│   ├── stores/          # Stores de Zustand
│   │   └── authStore.js
│   ├── i18n.js          # Configuración de internacionalización
│   ├── App.jsx          # Componente App con rutas
│   ├── main.jsx         # Punto de entrada
│   └── index.css        # Estilos globales
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Integración con API

El dashboard se integra con la API de PodTranslate:

- `/api/v1/auth/*` - Autenticación
- `/api/v1/podcasts/*` - Gestión de podcasts
- `/api/v1/episodes/*` - Gestión de episodios
- `/api/v1/transcriptions/*` - Trabajos de transcripción
- `/api/v1/distribution/*` - Gestión de distribución
- `/api/v1/analytics/*` - Datos de analíticas

## Autenticación

El dashboard usa autenticación JWT:

1. Login con email/contraseña
2. Token almacenado en localStorage vía Zustand
3. Token enviado en el header Authorization
4. Redirección automática al login en 401

Credenciales de demostración:
- Email: `admin@podtranslate.com`
- Contraseña: `password`

## Agregar un Nuevo Idioma

Para agregar un nuevo idioma (por ejemplo, Francés):

1. **Actualizar `src/i18n.js`**:

```javascript
const fr = {
  translation: {
    nav: {
      dashboard: 'Tableau de Bord',
      podcasts: 'Podcasts',
      // ... más traducciones
    }
  }
}

i18n.init({
  resources: {
    es,
    en,
    fr  // Agregar el nuevo idioma
  }
})
```

2. **Actualizar `LanguageSelector.jsx`**:

```javascript
const languages = [
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' }  // Nuevo idioma
]
```

## Despliegue

### Docker

```bash
# Construcción
docker build -t podtranslate/dashboard .

# Ejecutar
docker run -p 80:80 podtranslate/dashboard
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dashboard
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: dashboard
        image: podtranslate/dashboard:latest
        ports:
        - containerPort: 80
```

## Capturas de Pantalla

### Panel de Control en Español
![Dashboard ES](docs/images/dashboard-es.png)

### Selector de Idioma
![Language Selector](docs/images/language-selector.png)

### Vista de Analíticas
![Analytics](docs/images/analytics-es.png)

## Contribuir

Para contribuir con traducciones o nuevas funcionalidades:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

MIT

## Soporte

Para problemas o preguntas:
- GitHub Issues: https://github.com/podtranslate/podtranslate/issues
- Documentación: https://docs.podtranslate.com
- Email: soporte@podtranslate.com
