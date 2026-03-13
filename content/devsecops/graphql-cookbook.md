+++
date = '2026-03-13T18:50:00+01:00'
title = 'GraphQL Cookbook'
weight = 30
+++

You can query the world using a GraphQL client such as [Insomnia](https://insomnia.rest/) or [Postman](https://www.postman.com/), alternatively you can write code to query the GraphQL API. Below are some examples of how to do this in different programming languages.

## JavaScript

Install the `graphql-request` library:

```bash
pnpm install graphql-request
```

Then you can use the following code to query for all killmail objects:

```javascript
const { GraphQLClient, gql } = require('graphql-request');

// 1. Ensure the endpoint is correct (Sui often updates these)
const client = new GraphQLClient('https://graphql.testnet.sui.io/graphql');

const query = gql`
  query GetAllKillmailObjects {
    # 'first' is usually mandatory for pagination
    objects(
      first: 20,
      filter: { type: "0x28b497559d65ab320d9da4613bf2498d5946b2c0ae3597ccfda3072ce127448c::killmail::Killmail" }
    ) {
      nodes {
        address
        version
        digest
        asMoveObject {
          contents {
            json # Returns the fields of the Move struct as a JSON object
          }
        }
      }
    }
  }
`;

client.request(query)
  .then((data) => console.log(JSON.stringify(data, null, 2)))
  .catch((err) => console.error("Query Error:", err));
```

## Python

Install the `gql` library:

```bash
pip install gql
```

Then you can use the following code to query for all killmail objects:

```python
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import json

# 1. Setup the transport with the Sui Testnet endpoint
transport = RequestsHTTPTransport(
    url='https://graphql.testnet.sui.io/graphql',
    verify=True,
    retries=3,
)

# 2. Create the client
client = Client(transport=transport, fetch_schema_from_transport=False)

# 3. Define the query (using a multi-line string)
query = gql("""
    query GetAllKillmailObjects {
      objects(
        first: 20,
        filter: { type: "0x28b497559d65ab320d9da4613bf2498d5946b2c0ae3597ccfda3072ce127448c::killmail::Killmail" }
      ) {
        nodes {
          address
          version
          digest
          asMoveObject {
            contents {
              json
            }
          }
        }
      }
    }
""")

try:
    # 4. Execute the request
    response = client.execute(query)

    # 5. Print the formatted JSON result
    print(json.dumps(response, indent=2))

except Exception as e:
    print(f"Query failed: {e}")

```

## GraphQL Queries

### Query for all killmail objects

```graphql
query GetAllKillmailObjects {
  objects(filter: { type: "0x28b497559d65ab320d9da4613bf2498d5946b2c0ae3597ccfda3072ce127448c::killmail::Killmail" }) {
    nodes {
      address # The Sui Object ID
      version
      digest
      asMoveObject {
        contents {
          json # This contains the killer_id, victim_id, loss_type, etc.
        }
      }
    }
  }
}
```

### Query a Storage Inventory

```graphql
query {
  object(address: "0x481413ce66410a2192c14158bdc29bdc634c6d513412fdcfdc1760647f2dd15b") {
    address
    asMoveObject {
      contents {
        type { repr }
        json # Look here for 'inventory' or 'storage' fields
      }
      dynamicFields {
        nodes {
          name {
            type { repr }
            json
          }
          value {
            ... on MoveValue {
              json # Individual item stacks often appear here
            }
          }
        }
      }
    }
  }
}
```

Query the items in an inventory:

```graphql
query {
  object(address: "0x6d5462992e7459da24b3b498fb2a25aec443886791321ffc469126a9ff50a462") {
    address
    asMoveObject {
      contents {
        type { repr }
        # Look for 'inventory' or 'storage' keys in this JSON output
        json
      }
      # EVE Frontier SSUs often use Dynamic Fields for item stacks
      dynamicFields {
        nodes {
          name {
            type { repr }
            json  # This will likely show the Item ID/Type
          }
          value {
            ... on MoveValue {
              json # This will show the quantity and other item metadata
            }
          }
        }
      }
    }
  }
}
```
