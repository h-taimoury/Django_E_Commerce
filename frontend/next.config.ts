import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,

  // I added this to allow loading images from my Django backend server
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "127.0.0.1",
        port: "8000",
        pathname: "/media/**",
      },
    ],
  },
};

export default nextConfig;
