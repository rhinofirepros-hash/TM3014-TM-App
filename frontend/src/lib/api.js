export function getBackendUrl() {
  // Uniform backend URL resolver with safe fallback
  const url = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_BACKEND_URL)
    || process.env.REACT_APP_BACKEND_URL
    || '/api';
  return url;
}