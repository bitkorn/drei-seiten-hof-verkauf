import os
import datetime
from PIL import Image

# Pfade konfigurieren
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
THUMB_DIR = os.path.join(ASSETS_DIR, "thumb")
INDEX_FILE = os.path.join(PROJECT_DIR, "index.html")
THUMB_WIDTH = 300
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')

def generate_gallery():
    if not os.path.exists(ASSETS_DIR):
        print(f"Fehler: Ordner {ASSETS_DIR} nicht gefunden.")
        return

    os.makedirs(THUMB_DIR, exist_ok=True)

    # Bilddateien sammeln
    bilder = []
    for f in os.listdir(ASSETS_DIR):
        full_path = os.path.join(ASSETS_DIR, f)
        if os.path.isfile(full_path) and f.lower().endswith(IMAGE_EXTENSIONS):
            bilder.append(f)

    # Nach Dateinamen sortieren
    bilder.sort()

    html_blocks = []

    for bild_name in bilder:
        bild_pfad = os.path.join(ASSETS_DIR, bild_name)
        thumb_pfad = os.path.join(THUMB_DIR, bild_name)
        
        # Thumbnail generieren falls nicht vorhanden
        if not os.path.exists(thumb_pfad):
            try:
                with Image.open(bild_pfad) as img:
                    img.thumbnail((THUMB_WIDTH, THUMB_WIDTH))
                    img.save(thumb_pfad)
                    print(f"Thumbnail erstellt: {bild_name}")
            except Exception as e:
                print(f"Fehler bei Thumbnail für {bild_name}: {e}")
                continue

        # Titel/Caption bestimmen
        base_name = os.path.splitext(bild_name)[0]
        txt_pfad = os.path.join(ASSETS_DIR, base_name + ".txt")
        
        if os.path.exists(txt_pfad):
            with open(txt_pfad, 'r', encoding='utf-8') as f:
                caption = f.read().strip()
        else:
            # Fallback: Dateidatum im Format YYYY.MM.DD
            mtime = os.path.getmtime(bild_pfad)
            caption = datetime.datetime.fromtimestamp(mtime).strftime('%Y.%m.%d')

        # HTML Block generieren
        safe_caption = caption.replace('"', '&quot;')
        block = f'''
        <div class="thumb">
            <a href="assets/{bild_name}" data-lightbox="galerie" data-title="{safe_caption}">
                <img src="assets/thumb/{bild_name}" alt="{safe_caption}">
            </a>
            <div class="caption">{caption}</div>
        </div>'''
        html_blocks.append(block)

    full_gallery_html = "\n".join(html_blocks)
    
    # In eine Referenzdatei schreiben
    with open("gallery_fragment.html", "w", encoding="utf-8") as f:
        f.write(full_gallery_html)
    
    print("\n--- HTML GENERIERT ---")
    print(f"{len(bilder)} Bilder verarbeitet.")
    print("Der HTML-Code wurde in 'gallery_fragment.html' gespeichert.")
    print("----------------------\n")

    # Optional: Automatische Ersetzung in index.html versuchen
    update_index(full_gallery_html)

def update_index(new_html):
    if not os.path.exists(INDEX_FILE):
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Suche nach dem grid-Container
    start_tag = '<div class="grid">'
    end_tag = '</div>'
    
    start_pos = content.find(start_tag)
    if start_pos == -1:
        print("Konnte <div class='grid'> in index.html nicht finden.")
        return

    # Wir suchen das schließende </div> NACH dem start_tag
    # Da es oft verschachtelt sein kann, suchen wir das Ende der Galerie Sektion vor der nächsten Sektion
    # Für dieses Projekt ist die Struktur: <div class="grid"> ... </div> <div class="w3-container">
    next_section = content.find('<div class="w3-container">', start_pos + len(start_tag))
    end_pos = content.rfind('</div>', start_pos, next_section)
    
    if end_pos == -1:
        # Fallback auf einfache Suche
        end_pos = content.find('</div>', start_pos + len(start_tag))

    if start_pos != -1 and end_pos != -1:
        new_content = content[:start_pos + len(start_tag)] + "\n" + new_html + "\n    " + content[end_pos:]
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("index.html wurde automatisch aktualisiert.")

if __name__ == "__main__":
    generate_gallery()
