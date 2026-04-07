import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Compensation Explorer",
  description: "Browse compensation bands by role, level, location, and company size.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <Providers>
          <nav className="bg-white border-b border-gray-200 px-4 py-3">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
              <span className="text-lg font-semibold text-gray-900">
                Compensation Explorer
              </span>
              <span className="text-sm text-gray-500">
                P90 data available after login
              </span>
            </div>
          </nav>
          {children}
        </Providers>
      </body>
    </html>
  );
}
