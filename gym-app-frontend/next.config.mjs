/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true,
  },
  images: {
    domains: ["localhost", "v2.exercisedb.io"],
  },
};

export default nextConfig;
