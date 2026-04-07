export interface CompensationBand {
  id: string;
  role: string;
  level: string;
  location: string;
  companySize: string;
  p25: number;
  p50: number;
  p75: number;
  p90: number | null;
  sampleSize: number;
}

export interface CompensationBandFilter {
  role?: string;
  level?: string;
  location?: string;
  companySize?: string;
  minP50?: number;
  maxP50?: number;
}

export type CompanySize = "startup" | "small" | "mid" | "large" | "enterprise";

export const COMPANY_SIZE_LABELS: Record<CompanySize, string> = {
  startup: "Startup (1–50)",
  small: "Small (51–200)",
  mid: "Mid (201–1,000)",
  large: "Large (1,001–5,000)",
  enterprise: "Enterprise (5,000+)",
};

export const LEVELS = ["IC3", "IC4", "IC5", "IC6", "M4", "M5", "M6"];
