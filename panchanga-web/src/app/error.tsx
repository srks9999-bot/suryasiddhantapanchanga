'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('App error:', error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-orange-50 p-6">
      <h1 className="text-xl font-semibold text-gray-900">Something went wrong</h1>
      <p className="max-w-md text-center text-sm text-gray-600">{error.message}</p>
      <button
        type="button"
        onClick={reset}
        className="rounded-lg bg-orange-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-orange-700"
      >
        Try again
      </button>
      <p className="text-xs text-gray-500">
        If this persists, try: stop dev server, delete the <code className="rounded bg-gray-200 px-1">.next</code> folder, restart, and hard-refresh the browser (Ctrl+Shift+R).
      </p>
    </div>
  );
}
