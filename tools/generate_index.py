#!/usr/bin/env python3
"""
Generate index.html catalog from available images.
Scans the repository for WebP/PNG images and creates a visual catalog.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Repository configuration
BASE_URL = "https://kiwi-kaktu-corp.github.io/e-commecer-img/"
REPO_NAME = "e-commecer-img"


def find_images(root_dir: Path) -> dict[str, list[Path]]:
    """
    Find all images grouped by directory.

    Args:
        root_dir: Root directory to scan

    Returns:
        Dictionary mapping directory paths to list of image files
    """
    images = defaultdict(list)

    # Find all WebP and PNG files
    for ext in ("*.webp", "*.png", "*.jpg", "*.jpeg"):
        for img_path in root_dir.rglob(ext):
            # Skip hidden directories, tools, and .github
            parts = img_path.relative_to(root_dir).parts
            if any(part.startswith(".") or part in ("tools", "node_modules") for part in parts):
                continue

            rel_dir = str(img_path.parent.relative_to(root_dir))
            images[rel_dir].append(img_path)

    # Sort images within each directory and deduplicate (prefer WebP over PNG)
    result = {}
    for dir_path, img_list in images.items():
        # Group by base name
        by_name = defaultdict(list)
        for img in img_list:
            by_name[img.stem].append(img)

        # Prefer WebP, fallback to PNG/JPG
        unique_images = []
        for stem, variants in by_name.items():
            webp = [v for v in variants if v.suffix.lower() == ".webp"]
            if webp:
                unique_images.append(webp[0])
            else:
                unique_images.append(variants[0])

        result[dir_path] = sorted(unique_images, key=lambda p: p.stem)

    return result


def generate_image_card(img_path: Path, root_dir: Path) -> str:
    """Generate HTML for a single image card."""
    rel_path = img_path.relative_to(root_dir)
    filename = img_path.name
    dir_path = str(rel_path.parent) + "/"
    alt_name = img_path.stem

    # Use WebP extension for display, with fallback
    webp_path = rel_path.with_suffix(".webp")
    png_path = rel_path.with_suffix(".png")

    return f"""                <div class="image-card">
                    <img src="{webp_path}" alt="{alt_name}" loading="lazy" onerror="this.src=this.src.replace('.webp','.png')">
                    <div class="info">
                        <div class="filename">{webp_path.name}</div>
                        <div class="path">{dir_path}</div>
                        <button class="copy-btn" onclick="copyUrl(this, '{webp_path}')">Copiar URL</button>
                    </div>
                </div>"""


def generate_nav_links(categories: list[str]) -> str:
    """Generate navigation links."""
    links = []
    for cat in categories:
        cat_id = cat.replace("/", "-")
        links.append(f'        <a href="#{cat_id}">{cat}</a>')
    return "\n".join(links)


def generate_category_section(category: str, images: list[Path], root_dir: Path) -> str:
    """Generate HTML for a category section."""
    cat_id = category.replace("/", "-")
    cat_display = category.replace("/", " / ")

    cards = "\n".join(generate_image_card(img, root_dir) for img in images)

    return f"""        <section class="category" id="{cat_id}">
            <h2>{cat_display}</h2>
            <div class="image-grid">
{cards}
            </div>
        </section>"""


def generate_html(images_by_dir: dict[str, list[Path]], root_dir: Path) -> str:
    """Generate complete HTML catalog."""
    categories = sorted(images_by_dir.keys())
    nav_links = generate_nav_links(categories)
    sections = "\n\n".join(
        generate_category_section(cat, images_by_dir[cat], root_dir)
        for cat in categories
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Imagens - Kiwi Kaktu Corp</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}

        header {{
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 2rem;
            text-align: center;
        }}

        header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}

        header p {{
            opacity: 0.9;
        }}

        nav {{
            background: #fff;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        nav a {{
            color: #3498db;
            text-decoration: none;
            margin-right: 1rem;
        }}

        nav a:hover {{
            text-decoration: underline;
        }}

        main {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .category {{
            margin-bottom: 3rem;
        }}

        .category h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }}

        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
        }}

        .image-card {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .image-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}

        .image-card img {{
            width: 100%;
            height: 200px;
            object-fit: contain;
            background: #fafafa;
            padding: 1rem;
        }}

        .image-card .info {{
            padding: 1rem;
            border-top: 1px solid #eee;
        }}

        .image-card .filename {{
            font-weight: 600;
            color: #2c3e50;
            font-size: 0.9rem;
            word-break: break-all;
        }}

        .image-card .path {{
            color: #888;
            font-size: 0.75rem;
            margin-top: 0.25rem;
        }}

        .copy-btn {{
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
        }}

        .copy-btn:hover {{
            background: #2980b9;
        }}

        .copy-btn.copied {{
            background: #27ae60;
        }}

        .toast {{
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
        }}

        .toast.show {{
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }}

        footer {{
            text-align: center;
            padding: 2rem;
            color: #888;
            font-size: 0.9rem;
        }}

        @media (max-width: 600px) {{
            header h1 {{
                font-size: 1.5rem;
            }}

            main {{
                padding: 1rem;
            }}

            .image-grid {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 1rem;
            }}

            .image-card img {{
                height: 150px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Catálogo de Imagens</h1>
        <p>Kiwi Kaktu Corp - CDN de Imagens para E-commerce</p>
    </header>

    <nav>
{nav_links}
    </nav>

    <main>
{sections}
    </main>

    <footer>
        <p>Kiwi Kaktu Corp &copy; 2024</p>
    </footer>

    <div class="toast" id="toast">URL copiada!</div>

    <script>
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
    </script>
</body>
</html>"""


def main():
    root_dir = Path(__file__).parent.parent.resolve()
    output_path = root_dir / "index.html"

    print(f"Scanning for images in: {root_dir}")
    images_by_dir = find_images(root_dir)

    total_images = sum(len(imgs) for imgs in images_by_dir.values())
    print(f"Found {total_images} images in {len(images_by_dir)} categories")

    for cat, imgs in sorted(images_by_dir.items()):
        print(f"  {cat}: {len(imgs)} images")

    html = generate_html(images_by_dir, root_dir)

    output_path.write_text(html, encoding="utf-8")
    print(f"\nGenerated: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
