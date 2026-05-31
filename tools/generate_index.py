#!/usr/bin/env python3
"""
Generate hierarchical HTML catalog from available images.
Creates index.html files at each level: root → category → pack
"""

import sys
from pathlib import Path
from collections import defaultdict

# Repository configuration
BASE_URL = "https://kiwi-kaktu-corp.github.io/e-commecer-img/"
ASSETS_DIR = "assets"


def get_common_styles() -> str:
    """Return common CSS styles."""
    return """
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }

        header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 2rem;
            text-align: center;
        }

        header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        header p {
            opacity: 0.9;
        }

        .breadcrumb {
            background: #fff;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .breadcrumb a {
            color: #3498db;
            text-decoration: none;
        }

        .breadcrumb a:hover {
            text-decoration: underline;
        }

        .breadcrumb span {
            color: #888;
            margin: 0 0.5rem;
        }

        .breadcrumb .current {
            color: #2c3e50;
            font-weight: 600;
        }

        main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
        }

        .card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            color: inherit;
            display: block;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }

        .card .preview {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 4px;
            padding: 8px;
            background: #fafafa;
            height: 180px;
        }

        .card .preview img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: white;
            border-radius: 4px;
        }

        .card .info {
            padding: 1rem;
            border-top: 1px solid #ddd;
            background: #fff;
            position: relative;
            z-index: 10;
            box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        }

        .card .title {
            font-weight: 600;
            color: #2c3e50;
            font-size: 1.1rem;
        }

        .card .count {
            color: #888;
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }

        /* Image detail cards */
        .image-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .image-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .image-card img {
            width: 100%;
            height: 200px;
            object-fit: contain;
            background: #fafafa;
            padding: 1rem;
        }

        .image-card .info {
            padding: 1rem;
            border-top: 1px solid #ddd;
            background: #fff;
            position: relative;
            z-index: 10;
            box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        }

        .image-card .filename {
            font-weight: 600;
            color: #2c3e50;
            font-size: 0.9rem;
            word-break: break-all;
        }

        .image-card .path {
            color: #888;
            font-size: 0.75rem;
            margin-top: 0.25rem;
        }

        .copy-btn {
            display: block;
            width: 100%;
            margin-top: 0.75rem;
            padding: 0.5rem 1rem;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: background 0.2s;
        }

        .copy-btn:hover {
            background: #2980b9;
        }

        .copy-btn.copied {
            background: #27ae60;
        }

        .toast {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: #2c3e50;
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            opacity: 0;
            transition: transform 0.3s, opacity 0.3s;
            z-index: 1000;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }

        footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
            background: #fff;
            border-top: 1px solid #e0e0e0;
            margin-top: 2rem;
        }

        @media (max-width: 600px) {
            header h1 {
                font-size: 1.5rem;
            }

            main {
                padding: 1rem;
            }

            .grid {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 1rem;
            }

            .card .preview {
                height: 120px;
            }

            .image-card img {
                height: 150px;
            }
        }
"""


def get_copy_script() -> str:
    """Return JavaScript for copy functionality."""
    return f"""
        const BASE_URL = '{BASE_URL}';

        function copyUrl(btn, path) {{
            const url = BASE_URL + path;

            navigator.clipboard.writeText(url).then(() => {{
                btn.textContent = 'Copiado!';
                btn.classList.add('copied');

                const toast = document.getElementById('toast');
                toast.textContent = 'URL copiada: ' + url;
                toast.classList.add('show');

                setTimeout(() => {{
                    btn.textContent = 'Copiar URL';
                    btn.classList.remove('copied');
                    toast.classList.remove('show');
                }}, 2000);
            }}).catch(err => {{
                const textArea = document.createElement('textarea');
                textArea.value = url;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);

                btn.textContent = 'Copiado!';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = 'Copiar URL';
                    btn.classList.remove('copied');
                }}, 2000);
            }});
        }}
"""


def find_structure(root_dir: Path) -> dict:
    """
    Find all images and organize by category/pack structure.

    Returns:
        {
            'vinho': {
                'pack-01': [Path, Path, ...],
                'pack-02': [Path, Path, ...],
            }
        }
    """
    assets_dir = root_dir / ASSETS_DIR
    if not assets_dir.exists():
        return {}

    structure = defaultdict(lambda: defaultdict(list))

    for ext in ("*.webp", "*.png", "*.jpg", "*.jpeg"):
        for img_path in assets_dir.rglob(ext):
            rel_path = img_path.relative_to(assets_dir)
            parts = rel_path.parts

            if len(parts) >= 2:
                category = parts[0]  # e.g., 'vinho'
                pack = parts[1]      # e.g., 'pack-01'
                structure[category][pack].append(img_path)

    # Deduplicate (prefer WebP)
    result = {}
    for category, packs in structure.items():
        result[category] = {}
        for pack, images in packs.items():
            by_name = defaultdict(list)
            for img in images:
                by_name[img.stem].append(img)

            unique = []
            for stem, variants in by_name.items():
                webp = [v for v in variants if v.suffix.lower() == ".webp"]
                unique.append(webp[0] if webp else variants[0])

            result[category][pack] = sorted(unique, key=lambda p: p.stem)

    return result


def get_preview_images(images: list[Path], count: int = 4) -> list[Path]:
    """Get first N images for preview."""
    return images[:count]


def generate_root_index(structure: dict, root_dir: Path) -> str:
    """Generate root index.html showing categories."""
    cards = []

    for category in sorted(structure.keys()):
        packs = structure[category]
        total_images = sum(len(imgs) for imgs in packs.values())

        # Get preview images from first pack
        first_pack = sorted(packs.keys())[0]
        preview_imgs = get_preview_images(packs[first_pack])

        previews_html = ""
        for img in preview_imgs:
            rel_path = img.relative_to(root_dir)
            previews_html += f'<img src="{rel_path}" alt="" loading="lazy">'

        # Fill empty slots
        for _ in range(4 - len(preview_imgs)):
            previews_html += '<div style="background:#eee;border-radius:4px;"></div>'

        cards.append(f"""
            <a href="{ASSETS_DIR}/{category}/index.html" class="card">
                <div class="preview">
                    {previews_html}
                </div>
                <div class="info">
                    <div class="title">{category}</div>
                    <div class="count">{len(packs)} pack(s) · {total_images} imagens</div>
                </div>
            </a>
        """)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Imagens - Kiwi Kaktu Corp</title>
    <style>{get_common_styles()}</style>
</head>
<body>
    <header>
        <h1>Catálogo de Imagens</h1>
        <p>Kiwi Kaktu Corp - CDN de Imagens para E-commerce</p>
    </header>

    <div class="breadcrumb">
        <span class="current">Início</span>
    </div>

    <main>
        <div class="grid">
            {"".join(cards)}
        </div>
    </main>

    <footer>
        <p>Kiwi Kaktu Corp &copy; 2024</p>
    </footer>
</body>
</html>"""


def generate_category_index(category: str, packs: dict, root_dir: Path) -> str:
    """Generate category index.html showing packs."""
    cards = []

    for pack in sorted(packs.keys()):
        images = packs[pack]
        preview_imgs = get_preview_images(images)

        previews_html = ""
        for img in preview_imgs:
            rel_path = img.relative_to(root_dir / ASSETS_DIR / category)
            previews_html += f'<img src="{rel_path}" alt="" loading="lazy">'

        for _ in range(4 - len(preview_imgs)):
            previews_html += '<div style="background:#eee;border-radius:4px;"></div>'

        cards.append(f"""
            <a href="{pack}/index.html" class="card">
                <div class="preview">
                    {previews_html}
                </div>
                <div class="info">
                    <div class="title">{pack}</div>
                    <div class="count">{len(images)} imagens</div>
                </div>
            </a>
        """)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category} - Catálogo de Imagens</title>
    <style>{get_common_styles()}</style>
</head>
<body>
    <header>
        <h1>{category}</h1>
        <p>Selecione um pack para ver as imagens</p>
    </header>

    <div class="breadcrumb">
        <a href="../../index.html">Início</a>
        <span>›</span>
        <span class="current">{category}</span>
    </div>

    <main>
        <div class="grid">
            {"".join(cards)}
        </div>
    </main>

    <footer>
        <p>Kiwi Kaktu Corp &copy; 2024</p>
    </footer>
</body>
</html>"""


def generate_pack_index(category: str, pack: str, images: list[Path], root_dir: Path) -> str:
    """Generate pack index.html showing all images with copy buttons."""
    cards = []

    for img in images:
        full_rel_path = f"{ASSETS_DIR}/{category}/{pack}/{img.name}"
        webp_name = img.stem + ".webp"

        cards.append(f"""
            <div class="image-card">
                <img src="{img.name}" alt="{img.stem}" loading="lazy" onerror="this.src=this.src.replace('.webp','.png')">
                <div class="info">
                    <div class="filename">{webp_name}</div>
                    <div class="path">{ASSETS_DIR}/{category}/{pack}/</div>
                    <button class="copy-btn" onclick="copyUrl(this, '{ASSETS_DIR}/{category}/{pack}/{webp_name}')">Copiar URL</button>
                </div>
            </div>
        """)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{pack} - {category} - Catálogo de Imagens</title>
    <style>{get_common_styles()}</style>
</head>
<body>
    <header>
        <h1>{pack}</h1>
        <p>{len(images)} imagens disponíveis</p>
    </header>

    <div class="breadcrumb">
        <a href="../../../index.html">Início</a>
        <span>›</span>
        <a href="../index.html">{category}</a>
        <span>›</span>
        <span class="current">{pack}</span>
    </div>

    <main>
        <div class="grid">
            {"".join(cards)}
        </div>
    </main>

    <footer>
        <p>Kiwi Kaktu Corp &copy; 2024</p>
    </footer>

    <div class="toast" id="toast">URL copiada!</div>

    <script>{get_copy_script()}</script>
</body>
</html>"""


def main():
    root_dir = Path(__file__).parent.parent.resolve()

    print(f"Scanning for images in: {root_dir / ASSETS_DIR}")
    structure = find_structure(root_dir)

    if not structure:
        print("No images found in assets/ directory")
        return 1

    # Count totals
    total_categories = len(structure)
    total_packs = sum(len(packs) for packs in structure.values())
    total_images = sum(
        len(imgs) for packs in structure.values() for imgs in packs.values()
    )

    print(f"Found {total_images} images in {total_packs} packs across {total_categories} categories")

    for cat, packs in sorted(structure.items()):
        print(f"  {cat}/")
        for pack, imgs in sorted(packs.items()):
            print(f"    {pack}/: {len(imgs)} images")

    # Generate root index
    root_index = root_dir / "index.html"
    root_index.write_text(generate_root_index(structure, root_dir), encoding="utf-8")
    print(f"\nGenerated: {root_index}")

    # Generate category and pack indexes
    for category, packs in structure.items():
        cat_dir = root_dir / ASSETS_DIR / category

        # Category index
        cat_index = cat_dir / "index.html"
        cat_index.write_text(generate_category_index(category, packs, root_dir), encoding="utf-8")
        print(f"Generated: {cat_index}")

        # Pack indexes
        for pack, images in packs.items():
            pack_dir = cat_dir / pack
            pack_index = pack_dir / "index.html"
            pack_index.write_text(generate_pack_index(category, pack, images, root_dir), encoding="utf-8")
            print(f"Generated: {pack_index}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
