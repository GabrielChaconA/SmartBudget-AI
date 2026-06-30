<div align="center">
  <img src="frontend/public/smartbudget-logo.png" alt="SmartBudget Logo" width="300" />

  # SmartBudget-AI
  
  **AI-powered personal finance copilot** for budgeting, cash flow forecasting, expense analysis, OCR receipt processing, and smart financial insights.
  
  ---
</div>

## Fase de Planeación: Arquitectura y Tecnologías

Este documento formaliza la fase de diseño y planeación arquitectónica del proyecto **SmartBudget**. Para garantizar un rendimiento óptimo, mantenibilidad y escalabilidad a futuro, la aplicación se ha dividido estructuralmente en dos repositorios principales (Frontend y Backend), orquestados mediante **Docker**.

### Arquitectura General

El sistema adopta un modelo de aplicación SPA (Single Page Application) completamente desacoplada, la cual consume una API RESTful.

* **Frontend:** Responsable exclusivamente de la interfaz de usuario, enrutamiento del lado del cliente y visualización de gráficos interactivos.
* **Backend:** Responsable de la gestión de la base de datos, lógica de negocio, autenticación, cálculos financieros y servicios de inteligencia artificial.

---

### Frontend (Interfaz de Usuario)
Directorio: `/frontend`

El cliente web ha sido construido bajo un ecosistema moderno orientado al alto rendimiento.

* **Framework Core:** [Vue 3](https://vuejs.org/) (Composition API).
* **Lenguaje:** TypeScript para tipado estricto y seguridad en tiempo de compilación.
* **Bundler & Build Tool:** [Vite](https://vitejs.dev/) (para un rendimiento óptimo en desarrollo).
* **Enrutamiento:** Vue Router 4.
* **Estilos y Componentes UI:** 
  * [Tailwind CSS v3](https://tailwindcss.com/)
  * [shadcn-vue](https://www.shadcn-vue.com/) (Componentes de interfaz de usuario accesibles y parametrizables).
  * Diseño basado en una paleta de colores de alto contraste (Modo oscuro por defecto).
* **Manejo del Estado:** [Pinia](https://pinia.vuejs.org/)
* **Gráficos e Inteligencia de Negocios:** [Apache ECharts](https://echarts.apache.org/) (mediante `vue-echarts`) para el renderizado dinámico de métricas financieras.
* **Iconografía:** Lucide Icons.

---

### Backend (API RESTful y Lógica de Negocio)
Directorio: `/backend`

La API y orquestación de datos utiliza el ecosistema de PHP moderno, enfocado en concurrencia y seguridad.

* **Framework Core:** [Laravel 12](https://laravel.com/) (PHP 8.4).
* **Autenticación SPA:** Laravel Sanctum (Sesiones basadas en cookies stateful para máxima seguridad de la aplicación cliente).
* **Alto Rendimiento:** Laravel Octane (impulsado por RoadRunner o Swoole) para mantener la aplicación en memoria y lograr latencias mínimas.
* **Base de Datos:** MySQL 8.x.
* **Comunicación en Tiempo Real:** Laravel Reverb (Implementación de WebSockets para notificaciones y procesamiento de IA en tiempo real).
* **Tareas en Segundo Plano:** Laravel Queues y Scheduler (Gestión asíncrona para OCR de recibos, generación de reportes y sincronización).

---

### Entorno de Desarrollo (Docker)

El proyecto está diseñado para ser desplegado y ejecutado localmente sin necesidad de instalar dependencias globales a nivel de sistema operativo, gracias a la orquestación mediante Docker Compose.

* **Grupo Unificado (`smartbudget`)**: Todos los contenedores del ecosistema operan dentro de una misma red aislada, agrupados bajo el identificador `smartbudget`.
* **Contenedor Frontend**: Servidor de desarrollo Vite expuesto en el puerto `5173`.
* **Contenedores Backend (Sail)**: La API web, base de datos MySQL, y servicios de caché o colas (Redis), operando bajo la configuración predeterminada de Laravel Sail.

---

<div align="center">
  <i>Documento redactado durante la conclusión de la Fase de Planeación arquitectónica.</i>
</div>
