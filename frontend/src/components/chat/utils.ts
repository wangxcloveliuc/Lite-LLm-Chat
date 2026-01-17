const getFullImageUrl = (url: string) => {
  if (url.startsWith('http') || url.startsWith('data:')) {
    return url;
  }
  const baseUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  return `${cleanBaseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

export default getFullImageUrl;
