export function getBackendUrl() {
  // Uniform backend URL resolver with safe fallback
  const url = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_BACKEND_URL)
    || (typeof import !== 'undefined' && typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.REACT_APP_BACKEND_URL)
    || '/api';
  return url;
}