"""Create the bilingual Uala II project pages from the recovered WordPress data."""

from pathlib import Path
import json
import re

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SLUG = "uala-ii"

MEMORY_ES = [
    "El desafío de diseñar espacios de trabajo conlleva siempre una especial reflexión acerca del modo en que concebimos la actividad y el desarrollo del quehacer laboral. No cabe duda de que la arquitectura, en este sentido, tiene mucho para aportar a la calidad de vida del usuario. Con esta premisa asumimos el proyecto para las segundas oficinas de Ualá.",
    "El proyecto se estructura en dos grandes espacios unidos entre sí por un pasillo conector y un patio a modo de pulmón. A partir de las exigencias programáticas del cliente y de las condiciones inherentes al espacio a intervenir —un tinglado en pleno Palermo—, la superficie total se segmentó en dos niveles según las necesidades de uso. Se generó un área de recepción que hace de antesala a un gran espacio en doble altura, organizado por islas de trabajo.",
    "La estructura vista establece un equilibrio entre el antiguo edificio y la nueva intervención. La chapa negra acanalada contrasta, por su carácter contemporáneo, con el hormigón rústico. A su vez, la estructura del techo pintada de blanco se despega de lo existente mediante los tonos oscuros. Este cambio cromático permite reconocer el espacio entre lo existente y la nueva intervención.",
    "La sala principal alberga 60 puestos de trabajo, todos con visuales hacia un patio exterior con jardín vertical y abundante luz natural. Una gran piel de madera entablonada y teñida reviste muros y cubierta, y oculta vigas, mochetas e instalaciones eléctricas y termomecánicas.",
    "Al igual que la primera oficina, el edificio cuenta con un espacio para reuniones informales y descanso. Se diseñó como un muro de panal, cuyos intersticios forman ámbitos de uso definidos por tres materiales: madera, vidrio y hierro.",
    "La selección de revestimientos y mobiliario busca otorgar sencillez y calma visual mediante materiales nobles. Junto con el estudio de la iluminación directa, indirecta y natural, y de las condiciones termomecánicas, el conjunto logra el confort necesario para un espacio de trabajo.",
]

MEMORY_EN = [
    "Designing workspaces always requires reflecting on how activity and work are conceived. Architecture has much to contribute to users' quality of life. With this premise, we approached the project for Ualá's second offices.",
    "The project is organized into two large areas connected by a corridor and a courtyard that acts as a green lung. Based on the client's programmatic requirements and the inherent conditions of the site —a former industrial shed in Palermo—, the total area was divided into two levels according to use. A reception area leads into a large double-height workspace organized around work islands.",
    "The exposed structure establishes a balance between the old building and the new intervention. Black corrugated metal provides a contemporary contrast to the rough concrete, while the roof structure, painted white, is subtly separated from the existing fabric by darker tones. This chromatic shift makes the transition between old and new legible.",
    "The main room accommodates 60 workstations, all overlooking an outdoor courtyard with a vertical garden and abundant natural light. A continuous skin of stained timber boards wraps the walls and ceiling, concealing beams as well as electrical and mechanical services.",
    "As in the first office, the building includes an area for informal meetings and relaxation. It was designed as a honeycomb wall whose niches create usable spaces defined by three materials: wood, glass and iron.",
    "The selection of finishes and furniture seeks simplicity and visual calm through noble materials. Together with the study of direct, indirect and natural light, and the mechanical conditions, these decisions create the comfort required for a contemporary workplace.",
]


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def dimensions(path):
    with Image.open(path) as image:
        return image.size


def image_tag(path, alt, eager=False):
    width, height = dimensions(ROOT / path.lstrip("/"))
    priority = ' fetchpriority="high"' if eager else ""
    loading = "eager" if eager else "lazy"
    return (f'<img src="{path}" width="{width}" height="{height}" alt="{alt}" '
            f'loading="{loading}" decoding="async"{priority}>')


def main_markup(english=False):
    memory = MEMORY_EN if english else MEMORY_ES
    words = {
        "eyebrow": "Offices" if english else "Oficinas",
        "lede": ("Two connected work areas organized around a central courtyard inside a former industrial shed in Palermo."
                 if english else
                 "Dos áreas de trabajo conectadas por un pasillo y un patio central dentro de un antiguo tinglado de Palermo."),
        "status_label": "Status" if english else "Estado",
        "status": "Built" if english else "Obra concluida",
        "type_label": "Type" if english else "Tipo",
        "type": "Office" if english else "Oficinas",
        "location_label": "Location" if english else "Ubicación",
        "country_label": "Country" if english else "País",
        "country": "Argentina",
        "surface_label": "Area" if english else "Superficie",
        "year_label": "Year" if english else "Año",
        "team_label": "Team" if english else "Equipo",
        "photo_label": "Photography" if english else "Fotografía",
        "read_more": "Keep reading" if english else "Seguir leyendo",
        "read_less": "Read less" if english else "Leer menos",
        "gallery": "Gallery" if english else "Galería",
        "all_photos": "Gallery" if english else "Galería",
        "show": "View all 28 photos" if english else "Ver las 28 fotos",
        "hide": "Show fewer photos" if english else "Ver menos fotos",
        "portfolio": "Portfolio",
        "more": "More projects" if english else "Más proyectos",
        "all": "View all projects" if english else "Ver todos los proyectos",
    }
    prefix = "/en/projects" if english else "/proyectos"
    memory_html = "\n".join(f"          <p>{paragraph}</p>" for paragraph in memory)

    feature_numbers = [3, 11, 21]
    feature_texts = ([
        "A reception area leads to a double-height workspace organized around work islands.",
        "The existing structure and new materials define a clear dialogue between old and new.",
        "The central courtyard and vertical garden bring natural light into the work areas.",
    ] if english else [
        "La recepción da paso a un espacio de trabajo en doble altura organizado por islas.",
        "La estructura existente y los nuevos materiales construyen un diálogo claro entre lo antiguo y lo nuevo.",
        "El patio central y el jardín vertical llevan luz natural a las áreas de trabajo.",
    ])
    feature_rows = []
    for index, (number, caption) in enumerate(zip(feature_numbers, feature_texts)):
        reverse = " project-row--reverse" if index % 2 else ""
        photo = image_tag(f"/assets/gallery/{SLUG}/{number}.webp", f"Ualá II — photo {number}" if english else f"Ualá II — foto {number}", eager=index == 0)
        text = f'<div class="project-row__text"><p>{caption}</p></div>'
        media = f'<div class="project-row__photo">{photo}</div>'
        contents = media + "\n        " + text if reverse else text + "\n        " + media
        feature_rows.append(f'      <div class="project-row{reverse} reveal">\n        {contents}\n      </div>')

    gallery_items = []
    for number in range(1, 29):
        extra = " is-extra" if number > 6 else ""
        alt = f"Ualá II — photo {number}" if english else f"Ualá II — foto {number}"
        tag = image_tag(f"/assets/gallery/{SLUG}/{number}.webp", alt)
        gallery_items.append(f'          <figure class="gallery-grid__item{extra}">{tag}</figure>')
        if number == 6:
            for plan in range(1, 6):
                plan_alt = f"Ualá II — plan {plan}" if english else f"Ualá II — plano {plan}"
                plan_tag = image_tag(f"/assets/planos/{SLUG}/{plan}.webp", plan_alt)
                gallery_items.append(f'          <figure class="gallery-grid__item gallery-grid__item--plano">{plan_tag}</figure>')

    related = [
        ("uala-office", "Ualá", "Offices" if english else "Oficinas", "/assets/covers/uala-office.webp"),
        ("uala-gigena", "Ualá Gigena", "Offices" if english else "Oficinas", "/assets/gallery/uala-gigena/1.webp"),
        ("kavak-oficinas", "Kavak Oficinas", "Offices" if english else "Oficinas", "/assets/gallery/kavak-oficinas/14.webp"),
    ]
    related_html = []
    for slug, title, category, cover in related:
        width, height = dimensions(ROOT / cover.lstrip("/"))
        related_html.append(f'''          <a href="{prefix}/{slug}/" class="project-card" data-cat="oficinas" data-slug="{slug}">
            <span class="card-cat">{category}</span>
            <img src="{cover}" width="{width}" height="{height}" alt="{title}" loading="lazy" decoding="async">
            <div class="card-plate"><div class="p-name">{title}</div></div>
          </a>''')

    return f'''  <main id="main">
    <section class="hero-home pb-32">
      <div class="container">
        <span class="eyebrow">{words["eyebrow"]}</span>
        <h1 class="display-2 mt-14">Ualá II</h1>
        <p class="lede">{words["lede"]}</p>
        <div class="project-meta-row"><span>{words["type"]}</span><span>Buenos Aires</span></div>
        <dl class="project-specs">
          <div class="spec-row"><dt>{words["status_label"]}</dt><dd>{words["status"]}</dd></div>
          <div class="spec-row"><dt>{words["type_label"]}</dt><dd>{words["type"]}</dd></div>
          <div class="spec-row"><dt>{words["location_label"]}</dt><dd>Nicaragua 4680, Buenos Aires</dd></div>
          <div class="spec-row"><dt>{words["country_label"]}</dt><dd>{words["country"]}</dd></div>
          <div class="spec-row"><dt>{words["surface_label"]}</dt><dd>757 m²</dd></div>
          <div class="spec-row"><dt>{words["year_label"]}</dt><dd>2019–2020</dd></div>
          <div class="spec-row spec-row--team"><dt>{words["team_label"]}</dt><dd>{"Arch." if english else "Arq."} Fernando Hitzig<br>{"Arch." if english else "Arq."} Leonardo Militello<br>{"Arch." if english else "Arq."} Florencia Baserga<br>{"Arch." if english else "Arq."} Ailen Aljadeff</dd></div>
          <div class="spec-row"><dt>{words["photo_label"]}</dt><dd>Federico Kulekdjian</dd></div>
        </dl>
      </div>
    </section>

    <section class="project-memoria">
      <div class="container">
        <div class="memoria-cuerpo reveal">
{memory_html}
        </div>
        <button class="memoria-more gallery-more" type="button" data-mas="{words["read_more"]}" data-menos="{words["read_less"]}" aria-expanded="false">{words["read_more"]}</button>
      </div>
    </section>

    <section class="project-gallery">
{chr(10).join(feature_rows)}
    </section>

    <section class="section no-border" id="galeria">
      <div class="container">
        <div class="section-head"><div><span class="eyebrow">{words["gallery"]}</span><h2 class="display-3 mt-10">{words["all_photos"]}</h2></div></div>
        <div class="gallery-grid reveal">
{chr(10).join(gallery_items)}
        </div>
        <button type="button" class="btn gallery-more" data-total="28" data-mas="{words["show"]}" data-menos="{words["hide"]}" aria-expanded="false">{words["show"]}</button>
      </div>
    </section>

    <section class="section no-border">
      <div class="container">
        <div class="section-head">
          <div><span class="eyebrow">{words["portfolio"]}</span><h2 class="display-3 mt-10">{words["more"]}</h2></div>
          <a href="{prefix}/" class="btn link-arrow">{words["all"]}</a>
        </div>
        <div class="related-projects reveal">
{chr(10).join(related_html)}
        </div>
      </div>
    </section>
  </main>'''


def build_page(english=False):
    template_path = ROOT / ("en/projects/uala-office/index.html" if english else "proyectos/uala-office/index.html")
    content = read(template_path)
    old_url = "/en/projects/uala-office/" if english else "/proyectos/uala-office/"
    new_url = "/en/projects/uala-ii/" if english else "/proyectos/uala-ii/"
    content = content.replace(old_url, new_url)
    description = ("Ualá's second offices in Palermo: 757 m² organized around a central courtyard and vertical garden."
                   if english else
                   "Segundas oficinas de Ualá en Palermo: 757 m² organizados alrededor de un patio central y jardín vertical.")
    content = re.sub(r'<title>.*?</title>', '<title>Ualá II | Hitzig Militello Arquitectos</title>', content, count=1)
    content = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{description}">', content, count=1)
    content = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Ualá II | Hitzig Militello Arquitectos">', content, count=1)
    content = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{description}">', content, count=1)
    content = content.replace('/assets/covers/uala-office.webp', '/assets/covers/uala-ii.webp', 1)
    content = re.sub(r'  <main id="main">.*?  </main>', main_markup(english), content, count=1, flags=re.S)
    output = ROOT / ("en/projects/uala-ii/index.html" if english else "proyectos/uala-ii/index.html")
    write(output, content)


def card_markup(english=False, list_view=False):
    prefix = "/en/projects" if english else "/proyectos"
    label = "Built" if english else "Obra"
    category = "Offices" if english else "Oficinas"
    program = "Office interior design" if english else "Diseño interior de oficinas"
    width, height = dimensions(ROOT / f"assets/covers/{SLUG}.webp")
    if list_view:
        return f'''          <a href="{prefix}/{SLUG}/" class="project-list-row" data-cat="oficinas" data-slug="{SLUG}" data-estado="obra">
            <div class="plr-thumb"><img src="/assets/covers/{SLUG}.webp" width="{width}" height="{height}" alt="" loading="lazy"></div>
            <div><div class="plr-name">Ualá II</div><div class="plr-meta"><span>{program}</span><span>Buenos Aires</span><span>757 m²</span><span>2019–2020</span></div></div>
            <div class="plr-cat">{category}</div><div class="plr-loc">2019–2020</div>
          </a>'''
    return f'''          <a href="{prefix}/{SLUG}/" class="project-card" data-cat="oficinas" data-slug="{SLUG}" data-estado="obra">
            <span class="card-estado card-estado--obra">{label}</span><span class="card-cat">{category}</span>
            <img src="/assets/covers/{SLUG}.webp" width="{width}" height="{height}" alt="Ualá II" loading="lazy" decoding="async">
            <div class="card-plate"><div class="p-name">Ualá II</div><div class="p-meta"><span>{program}</span><span>Buenos Aires</span><span>757 m²</span><span>2019–2020</span></div></div>
          </a>'''


def update_listing(english=False):
    path = ROOT / ("en/projects/index.html" if english else "proyectos/index.html")
    content = read(path)
    if f'data-slug="{SLUG}"' in content:
        return
    grid_marker = '          <a href="/en/projects/uala-office/" class="project-card"' if english else '          <a href="/proyectos/uala-office/" class="project-card"'
    list_marker = '          <a href="/en/projects/uala-office/" class="project-list-row"' if english else '          <a href="/proyectos/uala-office/" class="project-list-row"'
    content = content.replace(grid_marker, card_markup(english) + "\n" + grid_marker, 1)
    content = content.replace(list_marker, card_markup(english, True) + "\n" + list_marker, 1)
    write(path, content)


def update_search(english=False):
    path = ROOT / ("scripts/search-index-en.js" if english else "scripts/search-index.js")
    content = read(path)
    if '"url": "/en/projects/uala-ii/"' in content or '"url": "/proyectos/uala-ii/"' in content:
        return
    prefix = "/en/projects" if english else "/proyectos"
    entry = {
        "tipo": "Project" if english else "Proyecto",
        "titulo": "Ualá II",
        "sub": "Offices" if english else "Oficinas",
        "desc": ("Office interior design · Buenos Aires · 757 m² · 2019–2020" if english else
                 "Diseño interior de oficinas · Buenos Aires · 757 m² · 2019–2020"),
        "url": f"{prefix}/{SLUG}/",
        "img": f"/assets/covers/{SLUG}.webp",
    }
    insertion = json.dumps(entry, ensure_ascii=False, indent=1) + ",\n "
    content = content.replace("window.HMA_SEARCH_INDEX = [\n ", "window.HMA_SEARCH_INDEX = [\n " + insertion, 1)
    write(path, content)


def main():
    for english in (False, True):
        build_page(english)
        update_listing(english)
        update_search(english)
    print("Uala II: bilingual pages, listings and search index created.")


if __name__ == "__main__":
    main()
