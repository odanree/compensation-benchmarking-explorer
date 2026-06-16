"use client";

import type { CostBandFilter, InstallerType } from "@/types/solar";
import { INSTALLER_TYPE_LABELS } from "@/types/solar";

interface FilterPanelProps {
  filters: CostBandFilter;
  onFiltersChange: (filters: CostBandFilter) => void;
  availableSizeRanges: string[];
  availableLocations: string[];
  availablePanelTiers: string[];
  availableInstallerTypes: string[];
}

export function FilterPanel({
  filters,
  onFiltersChange,
  availableSizeRanges,
  availableLocations,
  availablePanelTiers,
  availableInstallerTypes,
}: FilterPanelProps) {
  const update = (key: keyof CostBandFilter, value: string) => {
    onFiltersChange({ ...filters, [key]: value || undefined });
  };

  const hasActiveFilters = Object.values(filters).some(Boolean);

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* System Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">System Size</label>
          <select
            value={filters.systemSizeRange ?? ""}
            onChange={(e) => update("systemSizeRange", e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All sizes</option>
            {availableSizeRanges.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        {/* Panel Tier */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Panel Tier</label>
          <select
            value={filters.panelTier ?? ""}
            onChange={(e) => update("panelTier", e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All tiers</option>
            {availablePanelTiers.map((t) => (
              <option key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">State / Region</label>
          <select
            value={filters.location ?? ""}
            onChange={(e) => update("location", e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All locations</option>
            {availableLocations.map((loc) => (
              <option key={loc} value={loc}>
                {loc}
              </option>
            ))}
          </select>
        </div>

        {/* Installer Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Installer Type</label>
          <select
            value={filters.installerType ?? ""}
            onChange={(e) => update("installerType", e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All installers</option>
            {(availableInstallerTypes as InstallerType[]).map((k) => (
              <option key={k} value={k}>
                {INSTALLER_TYPE_LABELS[k] ?? k}
              </option>
            ))}
          </select>
        </div>
      </div>

      {hasActiveFilters && (
        <button
          onClick={() => onFiltersChange({})}
          className="mt-4 text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Clear all filters
        </button>
      )}
    </div>
  );
}
