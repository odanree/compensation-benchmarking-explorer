"use client";

import { useState } from "react";
import { useQuery } from "@apollo/client";
import { GET_COST_BANDS, GET_AVAILABLE_FILTERS } from "@/graphql/queries";
import { FilterPanel } from "./FilterPanel";
import { BandTable } from "./BandTable";
import { PaginationControls } from "./PaginationControls";
import { LoadingSpinner } from "./LoadingSpinner";
import type { CostBandFilter } from "@/types/compensation";

const PAGE_SIZE = 20;

export function BandExplorer() {
  const [filters, setFilters] = useState<CostBandFilter>({});
  const [cursor, setCursor] = useState<string | null>(null);

  const { data, loading, error } = useQuery(GET_COST_BANDS, {
    variables: { first: PAGE_SIZE, after: cursor, filters },
  });

  const { data: metaData } = useQuery(GET_AVAILABLE_FILTERS);

  const handleFiltersChange = (newFilters: CostBandFilter) => {
    setFilters(newFilters);
    setCursor(null);
  };

  const handleNext = () => {
    const endCursor = data?.costBands?.pageInfo?.endCursor;
    if (endCursor) setCursor(endCursor);
  };

  const handlePrev = () => {
    setCursor(null);
  };

  if (error) {
    return (
      <div className="text-red-600 p-4 bg-red-50 rounded-lg border border-red-200">
        Error loading solar cost data: {error.message}
      </div>
    );
  }

  const bands =
    data?.costBands?.edges?.map((e: { node: unknown }) => e.node) ?? [];
  const totalCount = data?.costBands?.totalCount ?? 0;
  const pageInfo = data?.costBands?.pageInfo;

  return (
    <div className="space-y-6">
      <FilterPanel
        filters={filters}
        onFiltersChange={handleFiltersChange}
        availableSizeRanges={metaData?.availableSizeRanges ?? []}
        availableLocations={metaData?.availableLocations ?? []}
        availablePanelTiers={metaData?.availablePanelTiers ?? []}
        availableInstallerTypes={metaData?.availableInstallerTypes ?? []}
      />

      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          <div className="text-sm text-gray-500">
            {totalCount === 0
              ? "No results"
              : `${totalCount} cost ${totalCount === 1 ? "band" : "bands"}`}
          </div>
          <BandTable bands={bands} />
          <PaginationControls
            pageInfo={pageInfo}
            onNext={handleNext}
            onPrev={handlePrev}
          />
        </>
      )}
    </div>
  );
}
