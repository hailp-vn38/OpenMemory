import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
  turbopack: {
    root: path.join(__dirname, '.'),
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'cdn.spectrumdevs.com',
        pathname: '/**',
      },
    ],
  },
};

export default nextConfig;
