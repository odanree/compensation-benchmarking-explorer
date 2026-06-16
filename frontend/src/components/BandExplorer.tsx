"use client";

import { useState } from "react";
import { useQuery } from "@apollo/client";
import { GET_COST_BANDS, GET_AVAILABLE_FILTERS } from "@/graphql/queries";
import { FilterPanel } from "./FilterPanel";
import { BandTable } from "./BandTable";
import { PaginationControls } from "./PaginationControls";
import { LoadingSpinner } from "./LoadingSpinner";
import type { CostBandFilter } from "@/types/solar";

const PAGE_SIZE = 20;

export function BandExplorer() {
  const [filters, setFilters] = useState<CostBandFilter>({});
  // cursorStack[0] is always null (page 1). Each Next click pushes the page's
  // endCursor; each Previous pops, revealing the previous page's start cursor.
  const [cursorStack, setCursorStack] = useState<(string | null)[]>([null]);
  const currentCursor = cursorStack[cursorStack.length - 1];

  const { data, loading, error } = useQuery(GET_COST_BANDS, {
    variables: { first: PAGE_SIZE, after: currentCursor, filters },
  });

  const { data: metaData } = useQuery(GET_AVAILABLE_FILTERS);

  const handleFiltersChange = (newFilters: CostBandFilter) => {
    setFilters(newFilters);
    setCursorStack([null]);
  };

  const handleNext = () => {
    const endCursor = data?.costBands?.pageInfo?.endCursor;
    if (endCursor) setCursorStack([...cursorStack, endCursor]);
  };

  const handlePrev = () => {
    if (cursorStack.length > 1) {
      setCursorStack(cursorStack.slice(0, -1));
    }
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
  const serverPageInfo = data?.costBands?.pageInfo;
  // Override hasPreviousPage with the client-side stack state; the server's
  // value is approximate (true whenever `after != null`) per ADR 002.
  const pageInfo = serverPageInfo
    ? { ...serverPageInfo, hasPreviousPage: cursorStack.length > 1 }
    : undefined;

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
