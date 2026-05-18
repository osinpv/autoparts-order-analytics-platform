db = db.getSiblingDB("autoparts_docs");

db.createCollection("product_documents", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["product_id", "sku", "category", "attributes", "created_at"],
      properties: {
        product_id: {
          bsonType: "int"
        },
        sku: {
          bsonType: "string"
        },
        category: {
          bsonType: "string"
        },
        attributes: {
          bsonType: "object"
        },
        fitment: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["make", "model", "year_from", "year_to"],
            properties: {
              make: {
                bsonType: "string"
              },
              model: {
                bsonType: "string"
              },
              year_from: {
                bsonType: "int"
              },
              year_to: {
                bsonType: "int"
              },
              engine: {
                bsonType: "string"
              }
            }
          }
        },
        oem_numbers: {
          bsonType: "array",
          items: {
            bsonType: "string"
          }
        },
        created_at: {
          bsonType: "date"
        }
      }
    }
  },
  validationAction: "error"
});

db.product_documents.createIndex(
  { product_id: 1 },
  { unique: true, name: "ux_product_documents_product_id" }
);

db.product_documents.createIndex(
  {
    "fitment.make": 1,
    "fitment.model": 1,
    "fitment.engine": 1
  },
  { name: "ix_product_documents_fitment_make_model_engine" }
);

db.product_documents.createIndex(
    {
      "oem_numbers": 1
    },
    { name: "ix_product_documents_oem_numbers" }
);