const RASI = [
  'Mesha (Aries)',
  'Vrshabha (Taurus)',
  'Mithuna (Gemini)',
  'Karkata (Cancer)',
  'Simha (Leo)',
  'Kanya (Virgo)',
  'Tula (Libra)',
  'Vrschika (Scorpio)',
  'Dhanus (Sagittarius)',
  'Makara (Capricorn)',
  'Kumbha (Aquarius)',
  'Meena (Pisces)',
];

export function rasiNameFromLongitude(longitude: number): string {
  const idx = Math.floor(((longitude % 360) + 360) % 360 / 30) % 12;
  return RASI[idx] ?? '';
}

