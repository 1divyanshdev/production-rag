/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: import.meta.dirname,
  async redirects() {
    return [
      { source: "/ask", destination: "/playground", permanent: true },
      { source: "/documents", destination: "/console", permanent: true },
    ];
  },
};

export default nextConfig;
