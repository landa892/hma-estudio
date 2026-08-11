/* LOCAL — no entra al repo (esta en .gitignore).

   Proyecto de Supabase del estudio: hma-autogestion, creado el 11/08/2026 en la
   cuenta hitzig.militello@gmail.com.

   Los dos valores son publicos por diseño: viajan al navegador en cada visita
   del panel. Lo que impide que alguien con esta clave borre las obras no es
   esconderla —no se puede—, es el RLS de la base. La clave service_role / secret
   NUNCA va aca: esa sortea el RLS por completo y vive solo en las variables de
   entorno de Vercel. */
window.HMA_CONFIG = {
  SUPABASE_URL: 'https://gbxtssedongadgorpxxs.supabase.co',

  // Formato nuevo de Supabase (sb_publishable_...), equivalente a la vieja
  // clave anon.
  SUPABASE_ANON_KEY: 'sb_publishable_l0BQKZAc5zuMQqT_p-JDcw_8lByh0wG',
};
