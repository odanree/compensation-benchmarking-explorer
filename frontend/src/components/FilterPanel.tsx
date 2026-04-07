"use client";

import type { CompensationBandFilter, CompanySize } from "@/types/compensation";
import { COMPANY_SIZE_LABELS, LEVELS } from "@/types/compensation";

interface FilterPanelProps {
  filters: CompensationBandFilter;
  onFiltersChange: (filters: CompensationBandFilter) => void;
  availableRoles: string[];
  availableLocations: string[];
}

export function FilterPanel({
  filters,
  onFiltersChange,
  availableRoles,
  availableLocations,
}: FilterPanelProps) {
  const update = (key: keyof CompensationBandFilter, value: string) => {
    onFiltersChange({ ...filters, [key]: value || undefined });
  };

  const hasActiveFilters = Object.values(filters).some(Boolean);

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Role */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
          <select
            value={filters.role ?? ""}
            onChange={(e) => update("role", e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All roles</option>
            {availableRoles.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        {/* Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
          <select
            value={filters.level ?? ""}
            onChange={(e) => update("level", e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All levels</option>
            {LEVELS.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
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

        {/* Company Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Company Size</label>
          <select
            value={filters.companySize ?? ""}
            onChange={(e) => update("companySize", e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All sizes</option>
            {(Object.entries(COMPANY_SIZE_LABELS) as [CompanySize, string][]).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
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
