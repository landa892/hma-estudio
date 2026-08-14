// Permanent redirects for project URLs retained from the previous WordPress.
const SLUGS = {
  '8': 'dos-casas-conde',
  '9': 'galeria-objeto-a',
  '10': 'ph-loft-arias',
  '21': 'bolivar',
  '22': 'oficina-casa-luna',
  '24': 'atelier-vilela',
  '25': 'victoria-brown',
  '28': 'tostado',
  '31': 'tostado',
  '32': 'luccianos-caballito',
  '33': 'luccianos-olivos',
  '34': 'tostado',
  '35': 'goodsten',
  '36': 'the-birra',
  '37': 'casa-olmo',
  '46': 'nim-bar',
  '48': 'mamba-bar',
  '50': 'elyaki',
  '51': 'uala-office',
  '52': 'tostado',
  '54': 'iguanafix',
  '55': 'cafe-artois',
  '59': 'novotel',
  '61': 'clasico-quilmes',
  '6977': 'fogon',
  '6988': 'clasico-quilmes',
  '7167-burger': 'burger-7167',
  'a2553': 'ph-loft-arias',
  'a757': 'araoz',
  'abasto-shopping-food-court': 'abasto-patio-comidas',
  'antiche-devoto': 'antiche',
  'b1763': 'bolivar',
  'c428': 'dos-casas-conde',
  'cafeteria-osten-casa-foa': 'osten-foa',
  'carbon': 'fogon',
  'design-technial-summit': 'novotel',
  'edificio-malabia': 'malabia',
  'el-clasico-de-quilmes': 'clasico-quilmes',
  'elaki': 'elyaki',
  'es4633': 'ph-el-salvador',
  'food-court-abasto-mall': 'abasto-patio-comidas',
  'hyatt-ziva-barbados': 'hyatt-ziva',
  'kavak-hub-2': 'kavak-hub',
  'kavak-office': 'kavak-oficinas',
  'kavak-oficina': 'kavak-oficinas',
  'l250': 'oficina-casa-luna',
  'malita-bar': 'malita',
  'manduca-market': 'manduca',
  'mercado-manduca': 'manduca',
  'moshu-treehouse': 'moshu',
  'nv5181': 'galeria-objeto-a',
  'osten-coffee-shop-casa-foa': 'osten-foa',
  'patio-comidas-abasto-shopping': 'abasto-patio-comidas',
  'sinapsis': 'bienal-venecia',
  'the-nim-bar': 'nim-bar',
  'tostado-belgrano': 'tostado',
  'tostado-callao': 'tostado',
  'tostado-fast': 'tostado',
  'tostado-fast-2': 'tostado',
  'tostado-microcentro': 'tostado',
  'tostado-tribunales': 'tostado',
  'uala': 'uala-office',
  'v2793': 'atelier-vilela',
  'willamsburg': 'williamsburg'
};

const REMOVED = new Set([
  '13',
  '26',
  '30',
  'areatres',
  'comedor-dario',
  'comedor-diario',
  'fuego-birra',
  'hill-of-arts',
  'hotel-own',
  'river-side'
]);

export default function handler(req, res) {
  const rawSlug = Array.isArray(req.query.slug) ? req.query.slug[0] : req.query.slug;
  const language = req.query.lang === 'en' ? 'en' : 'es';
  const slug = String(rawSlug || '').trim().toLowerCase();
  const base = language === 'en' ? '/en/projects/' : '/proyectos/';

  if (!slug || REMOVED.has(slug)) {
    res.setHeader('Location', base);
    return res.status(308).end();
  }

  const currentSlug = SLUGS[slug] || slug;
  res.setHeader('Location', `${base}${encodeURIComponent(currentSlug)}/`);
  return res.status(308).end();
}
