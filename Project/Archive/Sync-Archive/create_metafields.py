"""
BMBooks — Create Bookscan metafield definitions in live Shopify store.

Run once. Safe to re-run — Shopify returns an error on duplicates but
does not overwrite existing definitions.

Usage:
    python create_metafields.py
"""

import os
import requests
import json

SHOPIFY_STORE_URL    = os.environ.get("SHOPIFY_STORE_URL", "bruce-mckenzie-booksellers.myshopify.com")
SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]

GRAPHQL_URL = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-01/graphql.json"
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
}

METAFIELD_DEFINITIONS = [
    {
        "name":      "Author",
        "namespace": "bookscan",
        "key":       "author",
        "type":      "single_line_text_field",
        "ownerType": "PRODUCT",
    },
    {
        "name":      "ISBN",
        "namespace": "bookscan",
        "key":       "isbn",
        "type":      "single_line_text_field",
        "ownerType": "PRODUCT",
    },
    {
        "name":      "Pages",
        "namespace": "bookscan",
        "key":       "pages",
        "type":      "number_integer",
        "ownerType": "PRODUCT",
    },
    {
        "name":      "Publication Date",
        "namespace": "bookscan",
        "key":       "publication_date",
        "type":      "single_line_text_field",
        "ownerType": "PRODUCT",
    },
]

MUTATION = """
mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $definition) {
    createdDefinition {
      id
      name
      namespace
      key
      type { name }
    }
    userErrors {
      field
      message
      code
    }
  }
}
"""


def create_definition(defn):
    response = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json={"query": MUTATION, "variables": {"definition": defn}},
    )
    response.raise_for_status()
    data = response.json()

    result = data["data"]["metafieldDefinitionCreate"]
    errors = result.get("userErrors", [])

    if errors:
        for e in errors:
            if e.get("code") == "TAKEN":
                print(f"  SKIP  bookscan.{defn['key']} — already exists")
            else:
                print(f"  ERROR bookscan.{defn['key']} — {e['message']}")
    else:
        created = result["createdDefinition"]
        print(f"  OK    bookscan.{created['key']} ({created['type']['name']})")


def main():
    print(f"Creating metafield definitions on {SHOPIFY_STORE_URL}\n")
    for defn in METAFIELD_DEFINITIONS:
        create_definition(defn)
    print("\nDone.")


if __name__ == "__main__":
    main()
