export interface CostBand {
  id: string;
  systemSizeRange: string;
  panelTier: string;
  location: string;
  installerType: string;
  p25: number;
  p50: number;
  p75: number;
  p90: number | null;
  sampleSize: number;
}

export interface CostBandFilter {
  systemSizeRange?: string;
  panelTier?: string;
  location?: string;
  installerType?: string;
  minP50?: number;
  maxP50?: number;
}

export type InstallerType = "local" | "regional" | "national" | "utility";

export const INSTALLER_TYPE_LABELS: Record<InstallerType, string> = {
  local: "Local (1–5 crews)",
  regional: "Regional (6–20 locations)",
  national: "National (21+ locations)",
  utility: "Utility / Developer",
};

export const PANEL_TIERS = ["standard", "premium", "premium-plus"];

export const SIZE_RANGES = ["3-5 kW", "5-8 kW", "8-12 kW", "12 kW+"];
