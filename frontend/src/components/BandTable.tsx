import type { CompensationBand } from "@/types/compensation";
import { COMPANY_SIZE_LABELS } from "@/types/compensation";

function formatSalary(value: number | null | undefined): string {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

interface BandTableProps {
  bands: CompensationBand[];
}

export function BandTable({ bands }: BandTableProps) {
  if (bands.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 bg-white rounded-xl border border-gray-200">
        No compensation bands found. Try adjusting your filters.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
      <table className="min-w-full divide-y divide-gray-200 bg-white">
        <thead className="bg-gray-50">
          <tr>
            {["Role", "Level", "Location", "Company Size", "P25", "P50", "P75", "P90", "N"].map(
              (h) => (
                <th
                  key={h}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap"
                >
                  {h}
                </th>
              )
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {bands.map((band) => (
            <tr key={band.id} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3 text-sm font-medium text-gray-900 whitespace-nowrap">
                {band.role}
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                  {band.level}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                {band.location}
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">
                {COMPANY_SIZE_LABELS[band.companySize as keyof typeof COMPANY_SIZE_LABELS] ??
                  band.companySize}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">{formatSalary(band.p25)}</td>
              <td className="px-4 py-3 text-sm font-semibold text-gray-900">
                {formatSalary(band.p50)}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">{formatSalary(band.p75)}</td>
              <td className="px-4 py-3 text-sm text-gray-500">
                {band.p90 != null ? (
                  formatSalary(band.p90)
                ) : (
                  <span className="text-xs text-gray-400 italic">Login to view</span>
                )}
              </td>
              <td className="px-4 py-3 text-sm text-gray-500">{band.sampleSize}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
