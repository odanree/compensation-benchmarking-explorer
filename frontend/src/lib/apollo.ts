import { ApolloClient, InMemoryCache, HttpLink, from } from "@apollo/client";
import { onError } from "@apollo/client/link/error";

const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, path }) => {
      console.error(`[GraphQL error]: Message: ${message}, Path: ${path}`);
    });
  }
  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
  }
});

const httpLink = new HttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_URL || "http://localhost:8000/graphql/",
  credentials: "include",
});

export const apolloClient = new ApolloClient({
  link: from([errorLink, httpLink]),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          costBands: {
            // Cache per filter set; within a filter set, each cursor is its own
            // page (Next/Previous replace the visible rows rather than append).
            // Earlier version appended for infinite-scroll, but the UI uses
            // explicit Next/Previous buttons — append was a UX mismatch.
            keyArgs: ["filters", "after"],
          },
        },
      },
    },
  }),
});
