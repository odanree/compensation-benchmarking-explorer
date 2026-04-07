import { gql } from "@apollo/client";

export const GET_COMPENSATION_BANDS = gql`
  query GetCompensationBands(
    $first: Int
    $after: String
    $filters: CompensationBandFilter
  ) {
    compensationBands(first: $first, after: $after, filters: $filters) {
      edges {
        cursor
        node {
          id
          role
          level
          location
          companySize
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
    availableRoles
    availableLocations
  }
`;
