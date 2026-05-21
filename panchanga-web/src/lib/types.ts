export type TithiEntry = {
  tithi?: number;
  name: string;
  day: number;
  paksa: string;
  sukla_krsna?: string;
  start_ahar?: number;
  end_ahar?: number;
  start_time?: [number, number];
  end_time?: [number, number];
  spans_sunrise?: boolean;
  starts_on_date?: boolean;
  tithi_for_day?: boolean;
  is_vriddhi?: boolean;
  is_kshaya?: boolean;
};

export type KaranaEntry = {
  karana_name: string;
  start_ahar?: number;
  end_ahar?: number;
  start_time?: [number, number];
  end_time?: [number, number];
};

export type PanchangaAtTimeResult = Record<string, unknown> & {
  client_id?: string;
  calculation_time?: [number, number];
  calculation_point_civil?: string;
  calculation_point_astronomical?: string;
  paksha_name?: string;
  tithi_name?: string;
  tithi_start_time?: [number, number];
  tithi_end_time?: [number, number];
  tithis?: TithiEntry[];
  weekday?: string;
  nakshatra?: string;
  nakshatra_start_time?: [number, number];
  nakshatra_end_time?: [number, number];
  yoga?: string;
  yoga_start_time?: [number, number];
  yoga_end_time?: [number, number];
  karana?: string;
  karana_start_time?: [number, number];
  karana_end_time?: [number, number];
  karanas?: KaranaEntry[];
  masa?: string;
  adhimasa?: string;
  jovian_year_north?: string;
  jovian_year_south?: string;
  year_kali?: number;
  sunrise?: [number, number];
  sunset?: [number, number];
  sun_longitude?: number;
  moon_longitude?: number;
  planets_detailed?: Record<string, Record<string, unknown>>;
};

