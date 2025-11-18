// Generate optimized AVIF/WEBP/JPEG variants for sports images.
// Usage:
//   npm install
//   npm run images:optimize
// Outputs to assets/sports with filenames like img_1116-w800.webp

import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const root = new URL('../../', import.meta.url).pathname;
const SRC_DIR = path.join(root, 'src', 'sports');
const OUT_DIR = path.join(root, 'assets', 'sports');

// Focus on the slow-loading tail images first (as reported)
const TARGETS = [
  'img_1116.jpg', // Atmosphere
  'img_1128.jpg', // Tunnel
  'img_1165.jpg', // Tactics
  'img_1171.jpg', // Midfield
  'img_1175.jpg', // Net ripples
  'img_1194.jpg', // Officials
  'img_1208.jpg', // Crowd
  'img_1211.jpg'  // Youth
];

// Also include the hero image (improves LCP considerably)
const HERO = 'img_9050.jpg';

const WIDTHS = [480, 800, 1280, 1600];

async function ensureDir(p) {
  await fs.mkdir(p, { recursive: true });
}

async function generateVariants(file) {
  const srcPath = path.join(SRC_DIR, file);
  const base = path.parse(file).name; // e.g. img_1116

  const img = sharp(srcPath).rotate(); // respect EXIF orientation
  const meta = await img.metadata();

  await Promise.all(
    WIDTHS.map(async (w) => {
      const pipeline = sharp(srcPath).rotate().resize({ width: w, withoutEnlargement: true });
      // AVIF
      await pipeline
        .clone()
        .avif({ quality: 45, effort: 4 })
        .toFile(path.join(OUT_DIR, `${base}-w${w}.avif`));
      // WEBP
      await pipeline
        .clone()
        .webp({ quality: 70 })
        .toFile(path.join(OUT_DIR, `${base}-w${w}.webp`));
      // Optimized JPEG fallback (progressive)
      await pipeline
        .clone()
        .jpeg({ quality: 75, progressive: true, mozjpeg: true })
        .toFile(path.join(OUT_DIR, `${base}-w${w}.jpg`));
    })
  );

  return { base, width: meta.width, height: meta.height };
}

async function main() {
  await ensureDir(OUT_DIR);

  const images = [HERO, ...TARGETS];
  const results = [];
  for (const f of images) {
    try {
      const r = await generateVariants(f);
      results.push(r);
      console.log(`Optimized: ${f}`);
    } catch (e) {
      console.warn(`Skip ${f}: ${e.message}`);
    }
  }

  // Write a small manifest for future templating if needed
  await fs.writeFile(
    path.join(OUT_DIR, 'manifest.json'),
    JSON.stringify({ widths: WIDTHS, images: results }, null, 2),
    'utf8'
  );

  console.log(`\nDone. Generated responsive images in ${OUT_DIR}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
