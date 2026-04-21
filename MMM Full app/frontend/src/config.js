// frontend/src/config.js
// ─────────────────────────────────────────────────────────────────────────────
//  API Base URL — auto-resolves from environment
//  In development (localhost / 127.0.0.1) → http://localhost:8000
//  In production (any other host)         → same origin as the frontend
// ─────────────────────────────────────────────────────────────────────────────

const API_BASE_URL = (() => {
  const { hostname, protocol, port } = window.location;
  const isLocal = hostname === 'localhost' || hostname === '127.0.0.1';
  // In local dev the backend runs on port 8000
  if (isLocal) return `${protocol}//${hostname}:8000/api/v1`;
  // In production, the backend is reverse-proxied at /api/v1 on the same host
  return `${protocol}//${window.location.host}/api/v1`;
})();
