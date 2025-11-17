import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

// Traducciones en español
const es = {
  translation: {
    // Navegación
    nav: {
      dashboard: 'Panel de Control',
      podcasts: 'Podcasts',
      episodes: 'Episodios',
      transcriptions: 'Transcripciones',
      distribution: 'Distribución',
      analytics: 'Analíticas',
      settings: 'Configuración',
      logout: 'Cerrar Sesión'
    },

    // Login
    login: {
      title: 'PodTranslate',
      subtitle: 'Inicia sesión en tu cuenta',
      email: 'Correo Electrónico',
      emailPlaceholder: 'tu@ejemplo.com',
      password: 'Contraseña',
      passwordPlaceholder: '••••••••',
      signIn: 'Iniciar Sesión',
      signingIn: 'Iniciando sesión...',
      demo: 'Credenciales de demostración:',
      emailRequired: 'El correo es requerido',
      emailInvalid: 'Correo electrónico inválido',
      passwordRequired: 'La contraseña es requerida',
      passwordMin: 'La contraseña debe tener al menos 6 caracteres'
    },

    // Dashboard
    dashboard: {
      title: 'Panel de Control',
      subtitle: 'Resumen de las analíticas de tu podcast',
      totalPodcasts: 'Podcasts Totales',
      episodes: 'Episodios',
      transcriptions: 'Transcripciones',
      languages: 'Idiomas',
      downloadsTrend: 'Tendencia de Descargas',
      languageDistribution: 'Distribución de Idiomas',
      recentJobs: 'Trabajos de Transcripción Recientes',
      viewAll: 'Ver todos',
      episode: 'Episodio',
      status: 'Estado',
      language: 'Idioma',
      time: 'Tiempo',
      // Estados
      completed: 'Completado',
      processing: 'Procesando',
      queued: 'En Cola',
      failed: 'Fallido'
    },

    // Podcasts
    podcasts: {
      title: 'Podcasts',
      subtitle: 'Administra tus programas de podcast',
      newPodcast: 'Nuevo Podcast',
      search: 'Buscar podcasts...',
      episodes: 'Episodios',
      subscribers: 'Suscriptores',
      created: 'Creado',
      analytics: 'Analíticas',
      viewEpisodes: 'Ver Episodios',
      noPodcasts: 'No se encontraron podcasts'
    },

    // Episodes
    episodes: {
      title: 'Episodios',
      subtitle: 'Administra los episodios de tu podcast',
      newEpisode: 'Nuevo Episodio',
      search: 'Buscar episodios...',
      allPodcasts: 'Todos los Podcasts',
      podcast: 'Podcast',
      duration: 'Duración',
      published: 'Publicado',
      downloads: 'Descargas',
      draft: 'Borrador',
      noEpisodes: 'No se encontraron episodios'
    },

    // Transcriptions
    transcriptions: {
      title: 'Transcripciones',
      subtitle: 'Administra trabajos de transcripción y traducción',
      uploadAudio: 'Subir Audio',
      totalJobs: 'Trabajos Totales',
      progress: 'Progreso',
      error: 'Error',
      download: 'Descargar',
      noJobs: 'Aún no hay trabajos de transcripción',
      uploadPrompt: 'Sube un archivo de audio para comenzar'
    },

    // Distribution
    distribution: {
      title: 'Distribución',
      subtitle: 'Administra publicación multiplataforma',
      publishEpisode: 'Publicar Episodio',
      totalDistributions: 'Distribuciones Totales',
      published: 'Publicado',
      connectedPlatforms: 'Plataformas Conectadas',
      connected: 'Conectado',
      recentDistributions: 'Distribuciones Recientes',
      platform: 'Plataforma',
      view: 'Ver'
    },

    // Analytics
    analytics: {
      title: 'Analíticas',
      subtitle: 'Información detallada de rendimiento',
      last7Days: 'Últimos 7 días',
      last30Days: 'Últimos 30 días',
      last90Days: 'Últimos 90 días',
      lastYear: 'Último año',
      totalDownloads: 'Descargas Totales',
      totalPlays: 'Reproducciones Totales',
      shares: 'Compartidos',
      countries: 'Países',
      newCountries: 'nuevos países',
      vsLastPeriod: 'vs período anterior',
      performanceOverTime: 'Rendimiento en el Tiempo',
      topCountries: 'Principales Países',
      languagePerformance: 'Rendimiento por Idioma',
      engagementRate: 'Tasa de Participación',
      Downloads: 'Descargas',
      Plays: 'Reproducciones',
      Shares: 'Compartidos'
    },

    // Settings
    settings: {
      title: 'Configuración',
      subtitle: 'Administra tu cuenta y preferencias',
      profile: 'Perfil',
      apiKeys: 'Claves API',
      notifications: 'Notificaciones',
      languages: 'Idiomas',
      profileSettings: 'Configuración de Perfil',
      fullName: 'Nombre Completo',
      email: 'Correo Electrónico',
      company: 'Empresa',
      saveChanges: 'Guardar Cambios',
      nameRequired: 'El nombre es requerido',
      emailRequired: 'El correo es requerido',
      apiKeysTitle: 'Claves API',
      apiKeysDesc: 'Usa claves API para autenticar solicitudes a la API de PodTranslate.',
      productionKey: 'Clave de Producción',
      active: 'Activa',
      regenerate: 'Regenerar',
      revoke: 'Revocar',
      generateNew: 'Generar Nueva Clave API',
      notificationPrefs: 'Preferencias de Notificación',
      transcriptionCompleted: 'Transcripción completada',
      episodePublished: 'Episodio publicado',
      weeklyReport: 'Reporte semanal de analíticas',
      errorNotifications: 'Notificaciones de error',
      supportedLanguages: 'Idiomas Soportados',
      supportedLanguagesDesc: 'Selecciona idiomas para transcripción y traducción automática.',
      interfaceLanguage: 'Idioma de la Interfaz'
    },

    // Común
    common: {
      loading: 'Cargando...',
      search: 'Buscar',
      filter: 'Filtrar',
      edit: 'Editar',
      delete: 'Eliminar',
      cancel: 'Cancelar',
      save: 'Guardar',
      close: 'Cerrar',
      actions: 'Acciones',
      name: 'Nombre',
      description: 'Descripción',
      date: 'Fecha',
      status: 'Estado',
      type: 'Tipo',
      size: 'Tamaño',
      user: 'Usuario'
    },

    // Idiomas
    languageNames: {
      en: 'Inglés',
      es: 'Español',
      fr: 'Francés',
      de: 'Alemán',
      it: 'Italiano',
      pt: 'Portugués',
      ru: 'Ruso',
      ja: 'Japonés',
      zh: 'Chino',
      ko: 'Coreano',
      ar: 'Árabe',
      hi: 'Hindi'
    }
  }
}

// Traducciones en inglés
const en = {
  translation: {
    // Navigation
    nav: {
      dashboard: 'Dashboard',
      podcasts: 'Podcasts',
      episodes: 'Episodes',
      transcriptions: 'Transcriptions',
      distribution: 'Distribution',
      analytics: 'Analytics',
      settings: 'Settings',
      logout: 'Logout'
    },

    // Login
    login: {
      title: 'PodTranslate',
      subtitle: 'Sign in to your account',
      email: 'Email',
      emailPlaceholder: 'you@example.com',
      password: 'Password',
      passwordPlaceholder: '••••••••',
      signIn: 'Sign in',
      signingIn: 'Signing in...',
      demo: 'Demo credentials:',
      emailRequired: 'Email is required',
      emailInvalid: 'Invalid email address',
      passwordRequired: 'Password is required',
      passwordMin: 'Password must be at least 6 characters'
    },

    // Dashboard
    dashboard: {
      title: 'Dashboard',
      subtitle: 'Overview of your podcast analytics',
      totalPodcasts: 'Total Podcasts',
      episodes: 'Episodes',
      transcriptions: 'Transcriptions',
      languages: 'Languages',
      downloadsTrend: 'Downloads Trend',
      languageDistribution: 'Languages',
      recentJobs: 'Recent Transcription Jobs',
      viewAll: 'View all',
      episode: 'Episode',
      status: 'Status',
      language: 'Language',
      time: 'Time',
      // Status
      completed: 'Completed',
      processing: 'Processing',
      queued: 'Queued',
      failed: 'Failed'
    },

    // Podcasts
    podcasts: {
      title: 'Podcasts',
      subtitle: 'Manage your podcast shows',
      newPodcast: 'New Podcast',
      search: 'Search podcasts...',
      episodes: 'Episodes',
      subscribers: 'Subscribers',
      created: 'Created',
      analytics: 'Analytics',
      viewEpisodes: 'View Episodes',
      noPodcasts: 'No podcasts found'
    },

    // Episodes
    episodes: {
      title: 'Episodes',
      subtitle: 'Manage your podcast episodes',
      newEpisode: 'New Episode',
      search: 'Search episodes...',
      allPodcasts: 'All Podcasts',
      podcast: 'Podcast',
      duration: 'Duration',
      published: 'Published',
      downloads: 'Downloads',
      draft: 'Draft',
      noEpisodes: 'No episodes found'
    },

    // Transcriptions
    transcriptions: {
      title: 'Transcriptions',
      subtitle: 'Manage transcription and translation jobs',
      uploadAudio: 'Upload Audio',
      totalJobs: 'Total Jobs',
      progress: 'Progress',
      error: 'Error',
      download: 'Download',
      noJobs: 'No transcription jobs yet',
      uploadPrompt: 'Upload an audio file to get started'
    },

    // Distribution
    distribution: {
      title: 'Distribution',
      subtitle: 'Manage multi-platform publishing',
      publishEpisode: 'Publish Episode',
      totalDistributions: 'Total Distributions',
      published: 'Published',
      connectedPlatforms: 'Connected Platforms',
      connected: 'Connected',
      recentDistributions: 'Recent Distributions',
      platform: 'Platform',
      view: 'View'
    },

    // Analytics
    analytics: {
      title: 'Analytics',
      subtitle: 'Detailed performance insights',
      last7Days: 'Last 7 days',
      last30Days: 'Last 30 days',
      last90Days: 'Last 90 days',
      lastYear: 'Last year',
      totalDownloads: 'Total Downloads',
      totalPlays: 'Total Plays',
      shares: 'Shares',
      countries: 'Countries',
      newCountries: 'new countries',
      vsLastPeriod: 'vs last period',
      performanceOverTime: 'Performance Over Time',
      topCountries: 'Top Countries',
      languagePerformance: 'Language Performance',
      engagementRate: 'engagement rate',
      Downloads: 'Downloads',
      Plays: 'Plays',
      Shares: 'Shares'
    },

    // Settings
    settings: {
      title: 'Settings',
      subtitle: 'Manage your account and preferences',
      profile: 'Profile',
      apiKeys: 'API Keys',
      notifications: 'Notifications',
      languages: 'Languages',
      profileSettings: 'Profile Settings',
      fullName: 'Full Name',
      email: 'Email',
      company: 'Company',
      saveChanges: 'Save Changes',
      nameRequired: 'Name is required',
      emailRequired: 'Email is required',
      apiKeysTitle: 'API Keys',
      apiKeysDesc: 'Use API keys to authenticate requests to the PodTranslate API.',
      productionKey: 'Production Key',
      active: 'Active',
      regenerate: 'Regenerate',
      revoke: 'Revoke',
      generateNew: 'Generate New API Key',
      notificationPrefs: 'Notification Preferences',
      transcriptionCompleted: 'Transcription completed',
      episodePublished: 'Episode published',
      weeklyReport: 'Weekly analytics report',
      errorNotifications: 'Error notifications',
      supportedLanguages: 'Supported Languages',
      supportedLanguagesDesc: 'Select languages for automatic transcription and translation.',
      interfaceLanguage: 'Interface Language'
    },

    // Common
    common: {
      loading: 'Loading...',
      search: 'Search',
      filter: 'Filter',
      edit: 'Edit',
      delete: 'Delete',
      cancel: 'Cancel',
      save: 'Save',
      close: 'Close',
      actions: 'Actions',
      name: 'Name',
      description: 'Description',
      date: 'Date',
      status: 'Status',
      type: 'Type',
      size: 'Size',
      user: 'User'
    },

    // Language names
    languageNames: {
      en: 'English',
      es: 'Spanish',
      fr: 'French',
      de: 'German',
      it: 'Italian',
      pt: 'Portuguese',
      ru: 'Russian',
      ja: 'Japanese',
      zh: 'Chinese',
      ko: 'Korean',
      ar: 'Arabic',
      hi: 'Hindi'
    }
  }
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      es,
      en
    },
    fallbackLng: 'es', // Español como idioma predeterminado
    lng: 'es', // Forzar español al inicio
    interpolation: {
      escapeValue: false
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    }
  })

export default i18n
