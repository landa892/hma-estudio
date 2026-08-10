/* Copia este archivo como admin/config.js y pone los valores del proyecto.
   config.js NO entra al repositorio: asi el codigo no queda atado a una cuenta
   de Supabase y el dia que el proyecto se transfiera al estudio solo cambia
   ese archivo.

   Los dos valores son publicos por diseño: viajan al navegador en cada visita.
   Lo que impide que alguien con la clave anon borre las obras no es esconderla
   —no se puede—, es el RLS de la base. La clave service_role NUNCA va aca ni
   en ningun archivo del sitio: esa sortea el RLS por completo. */

window.HMA_CONFIG = {
  // Supabase -> Project Settings -> Data API -> Project URL
  SUPABASE_URL: 'https://xxxxxxxxxxxx.supabase.co',

  // Supabase -> Project Settings -> API Keys -> anon / public
  SUPABASE_ANON_KEY: 'eyJ...',
};
