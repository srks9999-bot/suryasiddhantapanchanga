export type CityOption = {
  key: string;
  name: string;
  latitude: number;
  longitude: number;
};

// Seeded from `packages/panchanga/panchanga/models/settings.py` LOCATION_PRESETS
export const CITY_OPTIONS: CityOption[] = [
  { key: 'ist', name: 'IST Meridian (82.5°E)', latitude: 23.18, longitude: 82.5 },
  { key: 'ujjain', name: 'Ujjain', latitude: 23.2, longitude: 75.8 },
  { key: 'delhi', name: 'Delhi', latitude: 28.6, longitude: 77.2 },
  { key: 'mumbai', name: 'Mumbai', latitude: 19.1, longitude: 72.9 },
  { key: 'chennai', name: 'Chennai', latitude: 13.1, longitude: 80.3 },
  { key: 'kolkata', name: 'Kolkata', latitude: 22.6, longitude: 88.4 },
  { key: 'bengaluru', name: 'Bengaluru', latitude: 12.97, longitude: 77.59 },
  { key: 'hyderabad', name: 'Hyderabad', latitude: 17.4, longitude: 78.5 },
  { key: 'varanasi', name: 'Varanasi', latitude: 25.3, longitude: 83.0 },
  { key: 'lanka', name: 'Lanka (Equator, 82.5°E)', latitude: 0, longitude: 82.5 },
];

export const DEFAULT_CITY_KEY = 'ist';

export function getCityByKey(key: string): CityOption | undefined {
  return CITY_OPTIONS.find((c) => c.key === key);
}

