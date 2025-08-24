/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Don't attempt to load these modules on the client side
      config.resolve.fallback = {
        fs: false,
        path: false,
        canvas: false
      };
    }
    return config;
  },
};

export default nextConfig;