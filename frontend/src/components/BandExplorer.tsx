"use client";

import { useState } from "react";
import { useQuery } from "@apollo/client";
import { GET_COMPENSATION_BANDS, GET_AVAILABLE_FILTERS } from "@/graphql/queries";
import { FilterPanel } from "./FilterPanel";
import { BandTable } from "./BandTable";
import { PaginationControls } from "./PaginationControls";
import { LoadingSpinner } from "./LoadingSpinner";
import type { CompensationBandFilter } from "@/types/compensation";

const PAGE_SIZE = 20;

export function BandExplorer() {
  const [filters, setFilters] = useState<CompensationBandFilter>({});
  const [cursor, setCursor] = useState<string | null>(null);

  const { data, loading, error } = useQuery(GET_COMPENSATION_BANDS, {
    variables: { first: PAGE_SIZE, after: cursor, filters },
  });

  const { data: metaData } = useQuery(GET_AVAILABLE_FILTERS);

  const handleFiltersChange = (newFilters: CompensationBandFilter) => {
    setFilters(newFilters);
    setCursor(null);
  };

  const handleNext = () => {
    const endCursor = data?.compensationBands?.pageInfo?.endCursor;
    if (endCursor) setCursor(endCursor);
  };

  const handlePrev = () => {
    setCursor(null);
  };

  if (error) {
    return (
      <div className="text-red-600 p-4 bg-red-50 rounded-lg border border-red-200">
        Error loading compensation data: {error.message}
      </div>
    );
  }

  const bands =
    data?.compensationBands?.edges?.map((e: { node: unknown }) => e.node) ?? [];
  const totalCount = data?.compensationBands?.totalCount ?? 0;
  const pageInfo = data?.compensationBands?.pageInfo;

  return (
    <div className="space-y-6">
      <FilterPanel
        filters={filters}
        onFiltersChange={handleFiltersChange}
        availableRoles={metaData?.availableRoles ?? []}
        availableLocations={metaData?.availableLocations ?? []}
      />

      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          <div className="text-sm text-gray-500">
            {totalCount === 0
              ? "No results"
              : `${totalCount} compensation ${totalCount === 1 ? "band" : "bands"}`}
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
