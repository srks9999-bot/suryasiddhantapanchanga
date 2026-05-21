import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function POST(req: Request) {
  const baseUrl = process.env.PANCHANGA_API_BASE_URL;
  if (!baseUrl) {
    return NextResponse.json(
      { error: 'Missing PANCHANGA_API_BASE_URL env var' },
      { status: 500 },
    );
  }

  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { error: 'Invalid JSON in request body' },
      { status: 400 },
    );
  }

  let res: Response;
  try {
    res = await fetch(`${baseUrl}/api/v1/panchanga/calculate_range`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Upstream connection failed';
    return NextResponse.json(
      { error: `Panchanga API unreachable: ${msg}. Is the backend running at ${baseUrl}?` },
      { status: 502 },
    );
  }

  const text = await res.text();
  let json: unknown;
  try {
    json = JSON.parse(text);
  } catch {
    json = { error: 'Upstream returned non-JSON response', raw: text };
  }

  return NextResponse.json(json, { status: res.status });
}
