import { gql } from "@apollo/client";

export const GET_COST_BANDS = gql`
  query GetCostBands(
    $first: Int
    $after: String
    $filters: CostBandFilter
  ) {
    costBands(first: $first, after: $after, filters: $filters) {
      edges {
        cursor
        node {
          id
          systemSizeRange
          panelTier
          location
          installerType
          p25
          p50
          p75
          p90
          sampleSize
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
    }
  }
`;

export const GET_AVAILABLE_FILTERS = gql`
  query GetAvailableFilters {
    availableSizeRanges
    availableLocations
    availablePanelTiers
    availableInstallerTypes
  }
`;
