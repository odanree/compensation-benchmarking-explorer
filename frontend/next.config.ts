import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow Apollo Client to work correctly with App Router
  experimental: {
    // Required for Apollo Client in Next.js App Router
  },
};

export default nextConfig;
