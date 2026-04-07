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
          compensationBands: {
            keyArgs: ["filters"],
            merge(existing, incoming, { args }) {
              if (!args?.after) return incoming;
              const merged = existing ? { ...existing } : { ...incoming };
              merged.edges = [...(existing?.edges ?? []), ...incoming.edges];
              merged.pageInfo = incoming.pageInfo;
              return merged;
            },
          },
        },
      },
    },
  }),
});
