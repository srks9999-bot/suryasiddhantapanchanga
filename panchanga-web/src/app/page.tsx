'use client';

import { Fragment, useEffect, useMemo, useState } from 'react';
import { CITY_OPTIONS, DEFAULT_CITY_KEY, getCityByKey } from '@/lib/cities';
import { rasiNameFromLongitude } from '@/lib/rasi';
import type { PanchangaAtTimeResult } from '@/lib/types';

type Entry = {
  id: string;
  cityKey: string;
  dateTime: string; // datetime-local string (for modern dates)
  latitude: string;
  longitude: string;
  useCustomDate: boolean; // toggle between datetime-local and custom fields
  customYear: string;
  customMonth: string;
  customDay: string;
  customHour: string;
  customMinute: string;
};

function formatTime(t?: [number, number]) {
  if (!t) return '—';
  const [h, m] = t;
  const hh = String(h).padStart(2, '0');
  const mm = String(m).padStart(2, '0');
  return `${hh}:${mm}`;
}

function newId() {
  return `e_${Math.random().toString(16).slice(2)}_${Date.now()}`;
}

function nowLocalDateTime() {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(
    d.getMinutes(),
  )}`;
}

function todayAt6AM() {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T06:00`;
}

type DatePayload =
  | { date_time: string }
  | { year: number; month: number; day: number; hour: number; minute: number };

function buildDatePayload(entry: Entry): DatePayload {
  if (!entry.useCustomDate) {
    // Use datetime-local value (YYYY-MM-DDTHH:mm format) for modern dates
    return { date_time: entry.dateTime + ':00' };
  }
  // Use separate fields for BCE dates (negative years)
  return {
    year: parseInt(entry.customYear, 10) || 0,
    month: parseInt(entry.customMonth, 10) || 1,
    day: parseInt(entry.customDay, 10) || 1,
    hour: parseInt(entry.customHour, 10) || 0,
    minute: parseInt(entry.customMinute, 10) || 0,
  };
}

function buildRangePayload(entry: Entry, days: number, useDrikSunrise: boolean, useSunriseForTithi: boolean) {
  const payload: Record<string, unknown> = { days };

  if (!entry.useCustomDate) {
    // Parse local datetime-local value to year/month/day
    const dt = new Date(entry.dateTime);
    payload.year = dt.getFullYear();
    payload.month = dt.getMonth() + 1;
    payload.day = dt.getDate();
  } else {
    payload.year = parseInt(entry.customYear, 10) || 0;
    payload.month = parseInt(entry.customMonth, 10) || 1;
    payload.day = parseInt(entry.customDay, 10) || 1;
  }

  payload.location = { latitude: Number(entry.latitude), longitude: Number(entry.longitude) };
  payload.settings = {
    use_drik_sunrise_sunset: useDrikSunrise,
    use_sunrise_for_tithi: useSunriseForTithi,
  };
  return payload;
}

function planetMean(detail: Record<string, unknown> | undefined): number | null {
  if (!detail) return null;
  const v =
    (detail['mean_longitude'] as number | undefined) ??
    (detail['planet_mean'] as number | undefined) ??
    (detail['mean_sun'] as number | undefined);
  return typeof v === 'number' ? v : null;
}

function planetTrue(detail: Record<string, unknown> | undefined): number | null {
  if (!detail) return null;
  const v = detail['true_longitude'] as number | undefined;
  return typeof v === 'number' ? v : null;
}

type TithiDisplayRow = {
  name: string;
  startTime?: [number, number];
  endTime?: [number, number];
  badge?: 'Kshaya' | 'Vriddhi';
};

type KaranaDisplayRow = {
  name: string;
  startTime?: [number, number];
  endTime?: [number, number];
};

function getTithiDisplayRows(r: PanchangaAtTimeResult | undefined): TithiDisplayRow[] {
  if (!r) return [{ name: '—' }];
  const tithis = r.tithis as Array<{
    name: string;
    start_time?: [number, number];
    end_time?: [number, number];
    tithi_for_day?: boolean;
    spans_sunrise?: boolean;
    is_vriddhi?: boolean;
    is_kshaya?: boolean;
  }> | undefined;
  if (Array.isArray(tithis) && tithis.length > 0) {
    const ruling = tithis.find((t) => t.tithi_for_day || t.spans_sunrise);
    const rows: TithiDisplayRow[] = [];
    if (ruling) {
      rows.push({
        name: ruling.name,
        startTime: ruling.start_time,
        endTime: ruling.end_time,
        badge: ruling.is_vriddhi ? 'Vriddhi' : undefined,
      });
    }
    for (const t of tithis) {
      if (t === ruling) continue;
      if (t.is_kshaya || t.is_vriddhi) {
        rows.push({
          name: t.name,
          startTime: t.start_time,
          endTime: t.end_time,
          badge: t.is_kshaya ? 'Kshaya' : 'Vriddhi',
        });
      }
    }
    if (rows.length > 0) return rows;
  }
  return [
    {
      name: (r.tithi_name as string) ?? '—',
      startTime: r.tithi_start_time as [number, number] | undefined,
      endTime: r.tithi_end_time as [number, number] | undefined,
    },
  ];
}

function getKaranaDisplayRows(r: PanchangaAtTimeResult | undefined): KaranaDisplayRow[] {
  if (!r) return [{ name: '—' }];
  const karanas = r.karanas as Array<{
    karana_name: string;
    start_time?: [number, number];
    end_time?: [number, number];
  }> | undefined;
  
  // Always use karanas list if available (even if it has only 1 item)
  if (Array.isArray(karanas)) {
    if (karanas.length > 0) {
      return karanas.map((k) => ({
        name: k.karana_name,
        startTime: k.start_time,
        endTime: k.end_time,
      }));
    }
    // If karanas is an empty array, fall back to single karana
  }
  
  // Fallback to single karana field
  return [
    {
      name: (r.karana as string) ?? '—',
      startTime: r.karana_start_time as [number, number] | undefined,
      endTime: r.karana_end_time as [number, number] | undefined,
    },
  ];
}

function renderPanchangaSection(r: PanchangaAtTimeResult | undefined, showTithiQualifiers: boolean) {
  const planets = r?.planets_detailed ?? {};
  const navagraha = [
    ['sun', 'Surya (Sun)'],
    ['moon', 'Chandra (Moon)'],
    ['mars', 'Mangala (Mars)'],
    ['mercury', 'Budha (Mercury)'],
    ['jupiter', 'Guru (Jupiter)'],
    ['venus', 'Sukra (Venus)'],
    ['saturn', 'Sani (Saturn)'],
    ['rahu', 'Rahu (N.Node)'],
    ['ketu', 'Ketu (S.Node)'],
  ] as const;

  return (
    <>
      <div className="mt-4 rounded-xl bg-orange-50 p-3">
        <div className="text-xs font-semibold text-gray-700">Panchanga</div>
        <div className="mt-2 grid grid-cols-[auto_1fr_auto] gap-x-2 gap-y-1 text-sm items-baseline">
          <div className="text-gray-600">Paksham</div>
          <div></div>
          <div className="font-semibold text-gray-900">{r?.paksha_name ?? '—'}</div>

          {getTithiDisplayRows(r).map((row, i) => (
            <Fragment key={`tithi-${i}`}>
              <div className="text-gray-600">{i === 0 ? 'Tithi' : ''}</div>
              <div className="text-xs text-gray-500 text-right">
                {row.startTime || row.endTime
                  ? `${formatTime(row.startTime)}→${formatTime(row.endTime)}`
                  : ''}
              </div>
              <div className="font-semibold text-gray-900">
                {row.name}
                {showTithiQualifiers && row.badge ? (
                  <span className="ml-1 text-xs font-normal text-amber-700">
                    ({row.badge})
                  </span>
                ) : null}
              </div>
            </Fragment>
          ))}

          <div className="text-gray-600">Varam</div>
          <div></div>
          <div className="font-semibold text-gray-900">{r?.weekday ?? '—'}</div>

          <div className="text-gray-600">Nakshatra</div>
          <div className="text-xs text-gray-500 text-right">
            {r?.nakshatra_start_time || r?.nakshatra_end_time
              ? `${formatTime(r?.nakshatra_start_time)}→${formatTime(r?.nakshatra_end_time)}`
              : ''}
          </div>
          <div className="font-semibold text-gray-900">{r?.nakshatra ?? '—'}</div>

          <div className="text-gray-600">Yoga</div>
          <div className="text-xs text-gray-500 text-right">
            {r?.yoga_start_time || r?.yoga_end_time
              ? `${formatTime(r?.yoga_start_time)}→${formatTime(r?.yoga_end_time)}`
              : ''}
          </div>
          <div className="font-semibold text-gray-900">{r?.yoga ?? '—'}</div>

          {getKaranaDisplayRows(r).map((row, i) => (
            <Fragment key={`karana-${i}`}>
              <div className="text-gray-600">{i === 0 ? 'Karana' : ''}</div>
              <div className="text-xs text-gray-500 text-right">
                {row.startTime || row.endTime
                  ? `${formatTime(row.startTime)}→${formatTime(row.endTime)}`
                  : ''}
              </div>
              <div className="font-semibold text-gray-900">{row.name}</div>
            </Fragment>
          ))}

          <div className="text-gray-600">Masa</div>
          <div></div>
          <div className="font-semibold text-gray-900">
            {r?.adhimasa ? `${r.adhimasa}${r?.masa ?? ''}` : r?.masa ?? '—'}
          </div>

          <div className="text-gray-600">Year Name</div>
          <div></div>
          <div className="font-semibold text-gray-900">{r?.jovian_year_south ?? '—'}</div>

          <div className="text-gray-600">Kali Year</div>
          <div></div>
          <div className="font-semibold text-gray-900">{r?.year_kali ?? '—'}</div>

          <div className="text-gray-600">Sunrise</div>
          <div></div>
          <div className="font-semibold text-gray-900">{formatTime(r?.sunrise)}</div>

          <div className="text-gray-600">Sunset</div>
          <div></div>
          <div className="font-semibold text-gray-900">{formatTime(r?.sunset)}</div>
        </div>
      </div>

      <div className="mt-4">
        <div className="flex items-baseline justify-between">
          <div className="text-xs font-semibold text-gray-700">Navagraha</div>
          <div className="text-[11px] text-gray-500">
            Sun/Moon + 7 planets + Rahu/Ketu
          </div>
        </div>

        <div className="mt-2 overflow-x-auto rounded-xl border border-gray-100">
          <table className="min-w-full w-full table-auto text-left text-xs">
            <thead className="bg-gray-50 text-gray-700">
              <tr>
                <th className="px-3 py-2 font-semibold">Planet</th>
                <th className="px-3 py-2 font-semibold">Mean</th>
                <th className="px-3 py-2 font-semibold">True</th>
                <th className="px-3 py-2 font-semibold">Rasi</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {navagraha.map(([key, label]) => {
                const detail = planets[key] as Record<string, unknown> | undefined;
                const mean = planetMean(detail);
                const tru = planetTrue(detail);
                const rasi = typeof tru === 'number' ? rasiNameFromLongitude(tru) : '—';
                return (
                  <tr key={key} className="bg-white">
                    <td className="px-3 py-2 font-semibold text-gray-900">{label}</td>
                    <td className="px-3 py-2 text-gray-700">
                      {typeof mean === 'number' ? `${mean.toFixed(2)}°` : '—'}
                    </td>
                    <td className="px-3 py-2 text-gray-700">
                      {typeof tru === 'number' ? `${tru.toFixed(2)}°` : '—'}
                    </td>
                    <td className="px-3 py-2 text-gray-500">
                      {rasi.split(' ')[0] || rasi}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

export default function HomePage() {
  const [isMounted, setIsMounted] = useState(false);
  const [entries, setEntries] = useState<Entry[]>(() => {
    // Fixed initial state for SSR (will be replaced on client)
    const ujjain = getCityByKey(DEFAULT_CITY_KEY)!;
    return [
      {
        id: 'initial',
        cityKey: DEFAULT_CITY_KEY,
        dateTime: '2026-01-01T06:00',
        latitude: String(ujjain.latitude),
        longitude: String(ujjain.longitude),
        useCustomDate: false,
        customYear: '2026',
        customMonth: '1',
        customDay: '1',
        customHour: '6',
        customMinute: '0',
      },
    ];
  });

  // Track if initial calculation is done
  const [initialCalcDone, setInitialCalcDone] = useState(false);

  // Update with dynamic values after mount (client-side only)
  useEffect(() => {
    const ujjain = getCityByKey(DEFAULT_CITY_KEY)!;
    const now = new Date();
    setEntries([
      {
        id: newId(),
        cityKey: DEFAULT_CITY_KEY,
        dateTime: todayAt6AM(),
        latitude: String(ujjain.latitude),
        longitude: String(ujjain.longitude),
        useCustomDate: false,
        customYear: String(now.getFullYear()),
        customMonth: String(now.getMonth() + 1),
        customDay: String(now.getDate()),
        customHour: '6',
        customMinute: '0',
      },
    ]);
    setIsMounted(true);
  }, []);

  const [resultsById, setResultsById] = useState<Record<string, PanchangaAtTimeResult | undefined>>({});
  const [rangeResultsById, setRangeResultsById] = useState<Record<string, PanchangaAtTimeResult[] | undefined>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [loadingIds, setLoadingIds] = useState<Set<string>>(new Set());
  const [rangeLoadingIds, setRangeLoadingIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [showTithiQualifiers, setShowTithiQualifiers] = useState(false);
  const [useDrikSunrise, setUseDrikSunrise] = useState(true);
  const [useSunriseForTithi, setUseSunriseForTithi] = useState(false);

  const requestPayload = useMemo(() => {
    return {
      entries: entries.map((e) => ({
        client_id: e.id,
        ...buildDatePayload(e),
        location: { latitude: Number(e.latitude), longitude: Number(e.longitude) },
        settings: {
          use_drik_sunrise_sunset: useDrikSunrise,
          use_sunrise_for_tithi: useSunriseForTithi,
        },
      })),
    };
  }, [entries, useDrikSunrise, useSunriseForTithi]);

  // Auto-calculate on initial mount
  useEffect(() => {
    if (isMounted && !initialCalcDone && entries.length > 0 && entries[0].id !== 'initial') {
      setInitialCalcDone(true);
      // Trigger calculation for initial entry
      (async () => {
        const entry = entries[0];
        setLoadingIds((prev) => new Set(prev).add(entry.id));
        try {
          const payload = {
            entries: [
              {
                client_id: entry.id,
                ...buildDatePayload(entry),
                location: { latitude: Number(entry.latitude), longitude: Number(entry.longitude) },
                settings: {
                  use_drik_sunrise_sunset: useDrikSunrise,
                  use_sunrise_for_tithi: useSunriseForTithi,
                },
              },
            ],
          };
          const res = await fetch('/api/panchanga/calculate_many', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify(payload),
          });
          const data = (await res.json()) as unknown;
          if (res.ok && Array.isArray(data)) {
            for (const item of data) {
              const r = item as PanchangaAtTimeResult;
              if (r.client_id) {
                setResultsById((prev) => ({ ...prev, [r.client_id!]: r }));
              }
            }
          }
        } catch {
          // Silently fail on initial load - user can click Calculate manually
        } finally {
          setLoadingIds((prev) => {
            const next = new Set(prev);
            next.delete(entry.id);
            return next;
          });
        }
      })();
    }
  }, [isMounted, initialCalcDone, entries]);

  async function calculateAll() {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/panchanga/calculate_many', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(requestPayload),
      });
      const data = (await res.json()) as unknown;

      if (!res.ok) {
        let msg = `Request failed (${res.status})`;
        if (typeof data === 'object' && data && 'detail' in data) {
          const detail = (data as { detail: unknown }).detail;
          msg = typeof detail === 'string' ? detail : JSON.stringify(detail, null, 2);
        } else if (typeof data === 'object' && data && 'error' in data) {
          const err = (data as { error: unknown }).error;
          msg = typeof err === 'string' ? err : JSON.stringify(err, null, 2);
        }
        
        // Add helpful message for 400 errors about year range
        if (res.status === 400) {
          msg += '\n\nNote: Supported year range is -100,000 to +100,000. Dates outside this range may cause calculation errors.';
        }
        
        throw new Error(msg);
      }

      if (!Array.isArray(data)) throw new Error('Unexpected response shape from API');

      const next: Record<string, PanchangaAtTimeResult> = {};
      for (const item of data) {
        const r = item as PanchangaAtTimeResult;
        if (r.client_id) next[r.client_id] = r;
      }
      setResultsById(next);
    } catch (e) {
      const msg = e instanceof Error ? e.message : typeof e === 'string' ? e : 'Unknown error';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }

  async function calculateSingle(entryId: string) {
    const entry = entries.find((e) => e.id === entryId);
    if (!entry) return;

    setLoadingIds((prev) => new Set(prev).add(entryId));
    setError(null);

    try {
      const payload = {
        entries: [
          {
            client_id: entry.id,
            ...buildDatePayload(entry),
            location: { latitude: Number(entry.latitude), longitude: Number(entry.longitude) },
            settings: {
              use_drik_sunrise_sunset: useDrikSunrise,
              use_sunrise_for_tithi: useSunriseForTithi,
            },
          },
        ],
      };

      const res = await fetch('/api/panchanga/calculate_many', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = (await res.json()) as unknown;

      if (!res.ok) {
        let msg = 'Calculation failed';
        if (typeof data === 'object' && data && 'detail' in data) {
          const detail = (data as { detail: unknown }).detail;
          msg = typeof detail === 'string' ? detail : JSON.stringify(detail, null, 2);
        } else if (typeof data === 'object' && data && 'error' in data) {
          const err = (data as { error: unknown }).error;
          msg = typeof err === 'string' ? err : JSON.stringify(err, null, 2);
        }
        
        // Add helpful message for 400 errors about year range
        if (res.status === 400) {
          msg += '\n\nNote: Supported year range is -100,000 to +100,000. Dates outside this range may cause calculation errors.';
        }
        
        setError(msg);
        return;
      }

      if (!Array.isArray(data)) {
        setError('Unexpected response format');
        return;
      }

      for (const item of data) {
        const r = item as PanchangaAtTimeResult;
        if (r.client_id) {
          setResultsById((prev) => ({ ...prev, [r.client_id!]: r }));
        }
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : typeof e === 'string' ? e : 'Unknown error';
      setError(msg);
    } finally {
      setLoadingIds((prev) => {
        const next = new Set(prev);
        next.delete(entryId);
        return next;
      });
    }
  }

  async function calculateRange(entryId: string, days: number = 30) {
    const entry = entries.find((e) => e.id === entryId);
    if (!entry) return;

    setRangeLoadingIds((prev) => new Set(prev).add(entryId));
    setError(null);

    try {
      const payload = buildRangePayload(entry, days, useDrikSunrise, useSunriseForTithi);
      const res = await fetch('/api/panchanga/calculate_range', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = (await res.json()) as unknown;

      if (!res.ok) {
        let msg = 'Calculation failed';
        if (typeof data === 'object' && data && 'detail' in data) {
          const detail = (data as { detail: unknown }).detail;
          msg = typeof detail === 'string' ? detail : JSON.stringify(detail, null, 2);
        } else if (typeof data === 'object' && data && 'error' in data) {
          const err = (data as { error: unknown }).error;
          msg = typeof err === 'string' ? err : JSON.stringify(err, null, 2);
        }
        
        if (res.status === 400) {
          msg += '\n\nNote: Supported year range is -100,000 to +100,000. Dates outside this range may cause calculation errors.';
        }

        setError(msg);
        return;
      }

      if (!Array.isArray(data)) {
        setError('Unexpected response format');
        return;
      }

      setRangeResultsById((prev) => ({ ...prev, [entryId]: data as PanchangaAtTimeResult[] }));
    } catch (e) {
      const msg = e instanceof Error ? e.message : typeof e === 'string' ? e : 'Unknown error';
      setError(msg);
    } finally {
      setRangeLoadingIds((prev) => {
        const next = new Set(prev);
        next.delete(entryId);
        return next;
      });
    }
  }

  function updateEntry(id: string, patch: Partial<Entry>) {
    setEntries((prev) => prev.map((e) => (e.id === id ? { ...e, ...patch } : e)));
  }

  function addEntry() {
    const ujjain = getCityByKey(DEFAULT_CITY_KEY)!;
    const now = new Date();
    setEntries((prev) => [
      ...prev,
      {
        id: newId(),
        cityKey: DEFAULT_CITY_KEY,
        dateTime: todayAt6AM(),
        latitude: String(ujjain.latitude),
        longitude: String(ujjain.longitude),
        useCustomDate: false,
        customYear: String(now.getFullYear()),
        customMonth: String(now.getMonth() + 1),
        customDay: String(now.getDate()),
        customHour: '6',
        customMinute: '0',
      },
    ]);
  }

  function duplicateEntry(id: string) {
    setEntries((prev) => {
      const src = prev.find((e) => e.id === id);
      if (!src) return prev;
      return [...prev, { ...src, id: newId() }];
    });
  }

  function removeEntry(id: string) {
    setEntries((prev) => prev.filter((e) => e.id !== id));
    setResultsById((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-100">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Surya Siddhanta Pure Panchanga</h1>
            <p className="text-sm text-gray-600">
              Calculations done by <br/>
            <b>Dakshinamnaya Sringeri Asthana Jyotirvidwansulu</b> <br/>
            <b>Dr.Sankaramanchi Ramakrishna Sastry PhD</b> <br/>
             And <br/>
            <b>Dr.Sankaramanchi Shiva Siddhanti PhD</b> <br/>
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={showTithiQualifiers}
                onChange={(e) => setShowTithiQualifiers(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              Show tithi qualifiers (Kshaya, Vriddhi)
            </label>

            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={useDrikSunrise}
                onChange={(e) => setUseDrikSunrise(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              Use Drik sunrise/sunset (more accurate)
            </label>

            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={useSunriseForTithi}
                onChange={(e) => setUseSunriseForTithi(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              Calculate tithi at sunrise
            </label>

            <button
              type="button"
              onClick={addEntry}
              className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow hover:shadow-md"
            >
              Add entry
            </button>
            <button
              type="button"
              onClick={calculateAll}
              disabled={isLoading || entries.length === 0}
              className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-primary-700 disabled:opacity-60"
            >
              {isLoading ? 'Calculating…' : 'Calculate all'}
            </button>
          </div>
        </div>

        {error ? (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 whitespace-pre-line">
            {error}
          </div>
        ) : null}

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {entries.map((e) => {
            const city = getCityByKey(e.cityKey);
            const r = resultsById[e.id];
            const planets = r?.planets_detailed ?? {};

            const navagraha = [
              ['sun', 'Surya (Sun)'],
              ['moon', 'Chandra (Moon)'],
              ['mars', 'Mangala (Mars)'],
              ['mercury', 'Budha (Mercury)'],
              ['jupiter', 'Guru (Jupiter)'],
              ['venus', 'Sukra (Venus)'],
              ['saturn', 'Sani (Saturn)'],
              ['rahu', 'Rahu (N.Node)'],
              ['ketu', 'Ketu (S.Node)'],
            ] as const;

            const isCardLoading = loadingIds.has(e.id);

            return (
              <div key={e.id} className="rounded-2xl bg-white p-4 shadow-lg">
                <div className="flex flex-col gap-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-semibold text-gray-900 truncate">
                        {city?.name ?? 'Custom'}
                      </div>
                      <div className="text-xs text-gray-500 truncate">ID: {e.id.slice(0, 20)}...</div>
                    </div>
                    <div className="flex flex-wrap gap-1 shrink-0">
                      <button
                        type="button"
                        onClick={() => duplicateEntry(e.id)}
                        className="rounded border border-gray-200 px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50"
                        title="Duplicate"
                      >
                        📋
                      </button>
                      <button
                        type="button"
                        onClick={() => removeEntry(e.id)}
                        className="rounded border border-gray-200 px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50"
                        title="Remove"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <button
                      type="button"
                      onClick={() => calculateSingle(e.id)}
                      disabled={isCardLoading}
                      className="w-full rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-semibold text-white shadow hover:bg-primary-700 disabled:opacity-60"
                    >
                      {isCardLoading ? 'Calculating…' : 'Calculate'}
                    </button>
                    <button
                      type="button"
                      onClick={() => calculateRange(e.id)}
                      disabled={rangeLoadingIds.has(e.id)}
                      className="w-full rounded-lg bg-white px-3 py-1.5 text-xs font-semibold text-primary-600 shadow hover:bg-primary-50 disabled:opacity-60"
                    >
                      {rangeLoadingIds.has(e.id) ? 'Calculating 30d…' : 'Calculate 30-day range'}
                    </button>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-1 gap-3">
                  <div className="grid gap-1 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-gray-700">Date & time</span>
                      <button
                        type="button"
                        onClick={() => updateEntry(e.id, { useCustomDate: !e.useCustomDate })}
                        className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                      >
                        {e.useCustomDate ? 'Use calendar picker' : 'Use custom fields (for BCE)'}
                      </button>
                    </div>

                    {!e.useCustomDate ? (
                      <input
                        type="datetime-local"
                        value={e.dateTime}
                        onChange={(ev) => updateEntry(e.id, { dateTime: ev.target.value })}
                        className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
                      />
                    ) : (
                      <>
                      <div className="grid grid-cols-5 gap-2">
                        <label className="grid gap-1">
                          <span className="text-xs text-gray-600">Year</span>
                          <input
                            type="number"
                            value={e.customYear}
                            onChange={(ev) => updateEntry(e.id, { customYear: ev.target.value })}
                            placeholder="-3101"
                            className="w-full rounded-lg border border-gray-200 px-2 py-2 text-sm"
                          />
                        </label>
                        <label className="grid gap-1">
                          <span className="text-xs text-gray-600">Month</span>
                          <input
                            type="number"
                            min="1"
                            max="12"
                            value={e.customMonth}
                            onChange={(ev) => updateEntry(e.id, { customMonth: ev.target.value })}
                            className="w-full rounded-lg border border-gray-200 px-2 py-2 text-sm"
                          />
                        </label>
                        <label className="grid gap-1">
                          <span className="text-xs text-gray-600">Day</span>
                          <input
                            type="number"
                            min="1"
                            max="31"
                            value={e.customDay}
                            onChange={(ev) => updateEntry(e.id, { customDay: ev.target.value })}
                            className="w-full rounded-lg border border-gray-200 px-2 py-2 text-sm"
                          />
                        </label>
                        <label className="grid gap-1">
                          <span className="text-xs text-gray-600">Hour</span>
                          <input
                            type="number"
                            min="0"
                            max="23"
                            value={e.customHour}
                            onChange={(ev) => updateEntry(e.id, { customHour: ev.target.value })}
                            className="w-full rounded-lg border border-gray-200 px-2 py-2 text-sm"
                          />
                        </label>
                        <label className="grid gap-1">
                          <span className="text-xs text-gray-600">Min</span>
                          <input
                            type="number"
                            min="0"
                            max="59"
                            value={e.customMinute}
                            onChange={(ev) => updateEntry(e.id, { customMinute: ev.target.value })}
                            className="w-full rounded-lg border border-gray-200 px-2 py-2 text-sm"
                          />
                        </label>
                      </div>
                      <button
                        type="button"
                        onClick={() =>
                          updateEntry(e.id, {
                            customYear: '-3101',
                            customMonth: '2',
                            customDay: '18',
                            customHour: '0',
                            customMinute: '0',
                          })
                        }
                        className="mt-1 text-xs text-primary-600 hover:text-primary-700 font-medium"
                      >
                        📅 Set Kali Epoch (-3101-02-18, 00:00)
                      </button>
                      </>
                    )}
                  </div>

                  <label className="grid gap-1 text-sm">
                    <span className="text-xs font-semibold text-gray-700">City</span>
                    <select
                      value={e.cityKey}
                      onChange={(ev) => {
                        const key = ev.target.value;
                        const c = getCityByKey(key);
                        updateEntry(e.id, {
                          cityKey: key,
                          latitude: c ? String(c.latitude) : e.latitude,
                          longitude: c ? String(c.longitude) : e.longitude,
                        });
                      }}
                      className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
                    >
                      {CITY_OPTIONS.map((c) => (
                        <option key={c.key} value={c.key}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <div className="grid grid-cols-2 gap-3">
                    <label className="grid gap-1 text-sm">
                      <span className="text-xs font-semibold text-gray-700">Latitude</span>
                      <input
                        inputMode="decimal"
                        value={e.latitude}
                        onChange={(ev) => updateEntry(e.id, { latitude: ev.target.value })}
                        className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
                      />
                    </label>
                    <label className="grid gap-1 text-sm">
                      <span className="text-xs font-semibold text-gray-700">Longitude</span>
                      <input
                        inputMode="decimal"
                        value={e.longitude}
                        onChange={(ev) => updateEntry(e.id, { longitude: ev.target.value })}
                        className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
                      />
                    </label>
                  </div>
                </div>

                {renderPanchangaSection(r, showTithiQualifiers)}

              </div>
            );
          })}
        </div>

        {Object.entries(rangeResultsById)
          .filter(([, results]) => Array.isArray(results) && results.length > 0)
          .map(([entryId, results]) => {
            const entry = entries.find((e) => e.id === entryId);
            if (!entry) return null;

            const dateLabel = entry.useCustomDate
              ? `${entry.customYear}-${String(entry.customMonth).padStart(2, '0')}-${String(entry.customDay).padStart(
                  2,
                  '0',
                )}`
              : entry.dateTime;

            return (
              <div key={entryId} className="mt-8 rounded-2xl bg-white p-6 shadow">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <div className="text-sm font-semibold text-gray-900">30-day range</div>
                    <div className="text-xs text-gray-500">
                      {entry.cityKey ? getCityByKey(entry.cityKey)?.name : 'Custom'} — {dateLabel}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Showing: {(results as any[]).length} days
                  </div>
                </div>

                <div className="mt-6 overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
                  <table className="min-w-full text-left text-xs">
                    <thead className="bg-gray-50 text-gray-700">
                      <tr>
                        <th className="px-3 py-2">Date</th>
                        <th className="px-3 py-2">Tithi</th>
                        <th className="px-3 py-2">Varam</th>
                        <th className="px-3 py-2">Nakshatra</th>
                        <th className="px-3 py-2">Yoga</th>
                        <th className="px-3 py-2">Karana</th>
                        <th className="px-3 py-2">Masa</th>
                        <th className="px-3 py-2">Sunrise</th>
                        <th className="px-3 py-2">Sunset</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {(results as any[]).map((item, idx) => {
                        const dateTuple = (item as any).gregorian_date as [number, number, number] | undefined;
                        const formattedDate = dateTuple
                          ? `${dateTuple[0]}-${String(dateTuple[1]).padStart(2, '0')}-${String(
                              dateTuple[2],
                            ).padStart(2, '0')}`
                          : '—';

                        const tithiName = (item as any).tithi_name ?? '—';
                        const varam = (item as any).weekday ?? '—';
                        const nakshatra = (item as any).nakshatra ?? '—';
                        const yoga = (item as any).yoga ?? '—';
                        const karana = (item as any).karana ?? '—';
                        const masa = (item as any).masa ?? '—';
                        const sunrise = formatTime((item as any).sunrise as [number, number] | undefined);
                        const sunset = formatTime((item as any).sunset as [number, number] | undefined);

                        return (
                          <tr key={idx} className="bg-white">
                            <td className="px-3 py-2 align-top">{formattedDate}</td>
                            <td className="px-3 py-2 align-top">
                              <div className="font-semibold text-gray-900">{tithiName}</div>
                              <div className="text-xs text-gray-500">
                                {(item as any).tithi_start_time ?
                                  `${formatTime((item as any).tithi_start_time)}→${formatTime((item as any).tithi_end_time)}` :
                                  ''}
                              </div>
                            </td>
                            <td className="px-3 py-2 align-top">{varam}</td>
                            <td className="px-3 py-2 align-top">
                              <div className="font-semibold text-gray-900">{nakshatra}</div>
                              <div className="text-xs text-gray-500">
                                {(item as any).nakshatra_start_time ?
                                  `${formatTime((item as any).nakshatra_start_time)}→${formatTime((item as any).nakshatra_end_time)}` :
                                  ''}
                              </div>
                            </td>
                            <td className="px-3 py-2 align-top">
                              <div className="font-semibold text-gray-900">{yoga}</div>
                              <div className="text-xs text-gray-500">
                                {(item as any).yoga_start_time ?
                                  `${formatTime((item as any).yoga_start_time)}→${formatTime((item as any).yoga_end_time)}` :
                                  ''}
                              </div>
                            </td>
                            <td className="px-3 py-2 align-top">{karana}</td>
                            <td className="px-3 py-2 align-top">{masa}</td>
                            <td className="px-3 py-2 align-top">{sunrise}</td>
                            <td className="px-3 py-2 align-top">{sunset}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}

       
      </div>
    </main>
  );
}

