#!/usr/bin/env python3
"""
Image optimization script for e-commerce CDN.
Converts PNG/JPG images to WebP format with configurable quality.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow>=10.0.0")
    sys.exit(1)


def convert_to_webp(
    input_path: Path,
    output_path: Path,
    quality: int = 85,
    max_width: int | None = None,
) -> bool:
    """
    Convert an image to WebP format.

    Args:
        input_path: Source image path
        output_path: Destination WebP path
        quality: WebP quality (1-100)
        max_width: Maximum width in pixels (maintains aspect ratio)

    Returns:
        True if conversion successful, False otherwise
    """
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for PNG with transparency, use RGBA)
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                # Keep alpha channel for transparent images
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            # Resize if max_width specified and image is larger
            if max_width and img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Save as WebP
            img.save(output_path, "WEBP", quality=quality)
            return True
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False


def process_directory(
    root_dir: Path,
    quality: int = 85,
    max_width: int | None = None,
    force: bool = False,
) -> tuple[int, int]:
    """
    Recursively process all images in a directory.

    Args:
        root_dir: Root directory to process
        quality: WebP quality (1-100)
        max_width: Maximum width in pixels
        force: Overwrite existing WebP files

    Returns:
        Tuple of (converted_count, skipped_count)
    """
    converted = 0
    skipped = 0

    # Find all PNG and JPG files
    extensions = ("*.png", "*.PNG", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG")
    image_files = []
    for ext in extensions:
        image_files.extend(root_dir.rglob(ext))

    for input_path in sorted(image_files):
        # Skip files in tools, .github, or hidden directories
        if any(part.startswith(".") or part == "tools" for part in input_path.parts):
            continue

        output_path = input_path.with_suffix(".webp")

        # Skip if WebP already exists and not forcing
        if output_path.exists() and not force:
            print(f"Skipping (exists): {input_path.relative_to(root_dir)}")
            skipped += 1
            continue

        print(f"Converting: {input_path.relative_to(root_dir)} -> {output_path.name}")
        if convert_to_webp(input_path, output_path, quality, max_width):
            converted += 1
        else:
            skipped += 1

    return converted, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Convert images to WebP format for CDN optimization"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Root directory to process (default: repository root)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="WebP quality 1-100 (default: 85)",
    )
    parser.add_argument(
        "--max-width",
        type=int,
        default=None,
        help="Maximum image width in pixels (maintains aspect ratio)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing WebP files",
    )

    args = parser.parse_args()

    root_dir = args.root.resolve()
    print(f"Processing images in: {root_dir}")
    print(f"Quality: {args.quality}%, Max width: {args.max_width or 'unlimited'}")
    print("-" * 50)

    converted, skipped = process_directory(
        root_dir,
        quality=args.quality,
        max_width=args.max_width,
        force=args.force,
    )

    print("-" * 50)
    print(f"Converted: {converted}, Skipped: {skipped}")

    return 0 if converted >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
