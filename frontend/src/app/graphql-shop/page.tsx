"use client";
import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

type Product = {
  id: number;
  name: string;
  price: number;
};

type Feedback = {
  type: "success" | "error";
  text: string;
};

const GRAPHQL_URL = "http://127.0.0.1:8005/graphql";

// One helper for every request: GraphQL always POSTs { query, variables } to one URL
async function gql<T>(query: string, variables: Record<string, unknown> = {}): Promise<T> {
  const response = await fetch(GRAPHQL_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });
  const result = await response.json();
  if (result.errors?.length) {
    throw new Error(result.errors[0].message);
  }
  return result.data as T;
}

const PRODUCTS_QUERY = `
  query {
    products { id name price }
  }
`;

const CREATE_MUTATION = `
  mutation Create($name: String!, $price: Float!) {
    createProduct(name: $name, price: $price) { id name price }
  }
`;

const UPDATE_MUTATION = `
  mutation Update($id: Int!, $name: String, $price: Float) {
    updateProduct(id: $id, name: $name, price: $price) { id name price }
  }
`;

const DELETE_MUTATION = `
  mutation Delete($id: Int!) {
    deleteProduct(id: $id)
  }
`;

export default function GraphqlShopPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [adding, setAdding] = useState(false);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editDraft, setEditDraft] = useState({ name: "", price: "" });

  // READ
  useEffect(() => {
    gql<{ products: Product[] }>(PRODUCTS_QUERY)
      .then((data) => setProducts(data.products))
      .catch(() => setFeedback({ type: "error", text: "Failed to load products from GraphQL" }))
      .finally(() => setLoading(false));
  }, []);

  // CREATE
  async function addProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback(null);
    setAdding(true);
    try {
      const data = await gql<{ createProduct: Product }>(CREATE_MUTATION, {
        name,
        price: Number(price),
      });
      setProducts((current) => [...current, data.createProduct]);
      setFeedback({ type: "success", text: `Added "${data.createProduct.name}" (id ${data.createProduct.id})` });
      setName("");
      setPrice("");
    } catch (error) {
      setFeedback({ type: "error", text: error instanceof Error ? error.message : "Failed to add product" });
    } finally {
      setAdding(false);
    }
  }

  // UPDATE
  function startEdit(product: Product) {
    setFeedback(null);
    setEditingId(product.id);
    setEditDraft({ name: product.name, price: String(product.price) });
  }

  async function saveEdit(id: number) {
    const newPrice = Number(editDraft.price);
    if (editDraft.name.trim() === "" || Number.isNaN(newPrice)) {
      setFeedback({ type: "error", text: "Name and price are required" });
      return;
    }
    setFeedback(null);
    try {
      const data = await gql<{ updateProduct: Product | null }>(UPDATE_MUTATION, {
        id,
        name: editDraft.name,
        price: newPrice,
      });
      if (!data.updateProduct) throw new Error("Product not found");
      setProducts((current) => current.map((p) => (p.id === id ? data.updateProduct! : p)));
      setFeedback({ type: "success", text: "Product updated" });
      setEditingId(null);
    } catch (error) {
      setFeedback({ type: "error", text: error instanceof Error ? error.message : "Failed to update product" });
    }
  }

  // DELETE
  async function deleteProduct(id: number) {
    setFeedback(null);
    try {
      const data = await gql<{ deleteProduct: boolean }>(DELETE_MUTATION, { id });
      if (!data.deleteProduct) throw new Error("Product not found");
      setProducts((current) => current.filter((p) => p.id !== id));
      setFeedback({ type: "success", text: "Product deleted" });
    } catch (error) {
      setFeedback({ type: "error", text: error instanceof Error ? error.message : "Failed to delete product" });
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">GraphQL Shop</h1>
          <p className="text-sm text-muted">Products stored in SQLite, read and written through GraphQL</p>
        </div>
        <Link href="/catalog" className="text-sm text-muted hover:underline">
          ← Catalog
        </Link>
      </header>

      {feedback && (
        <div
          className={feedback.type === "success" ? "alert alert-success" : "alert alert-danger"}
          role="status"
        >
          <span>{feedback.type === "success" ? "✓" : "!"}</span>
          <span>{feedback.text}</span>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[340px_1fr] lg:items-start">
        <section className="card p-6">
          <h2 className="mb-4 text-base font-semibold">Add product</h2>
          <form onSubmit={addProduct} className="flex flex-col gap-4">
            <div>
              <label className="field-label" htmlFor="gql-name">Name</label>
              <input
                id="gql-name"
                type="text"
                placeholder="e.g. MacBook"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
                className="input"
              />
            </div>
            <div>
              <label className="field-label" htmlFor="gql-price">Price</label>
              <input
                id="gql-price"
                type="number"
                step="0.01"
                placeholder="0.00"
                value={price}
                onChange={(event) => setPrice(event.target.value)}
                required
                className="input"
              />
            </div>
            <button type="submit" disabled={adding} className="btn btn-primary mt-1">
              {adding ? "Adding…" : "+ Add product"}
            </button>
          </form>
        </section>

        <section className="card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">All products</h2>
            <span className="badge badge-neutral">{products.length} total</span>
          </div>

          {loading ? (
            <div className="flex flex-col gap-3">
              <div className="skeleton h-16 w-full animate-pulse" />
              <div className="skeleton h-16 w-full animate-pulse" />
            </div>
          ) : products.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-14 text-center text-muted">
              <p className="text-sm">No products yet — add your first one.</p>
            </div>
          ) : (
            <ul className="flex flex-col gap-3">
              {products.map((product) =>
                editingId === product.id ? (
                  <li key={product.id} className="card flex flex-col gap-2 p-3 shadow-none">
                    <div className="flex flex-col gap-2 sm:flex-row">
                      <input
                        id={`gql-edit-name-${product.id}`}
                        value={editDraft.name}
                        onChange={(event) => setEditDraft((d) => ({ ...d, name: event.target.value }))}
                        className="input"
                        placeholder="Name"
                      />
                      <input
                        id={`gql-edit-price-${product.id}`}
                        type="number"
                        step="0.01"
                        value={editDraft.price}
                        onChange={(event) => setEditDraft((d) => ({ ...d, price: event.target.value }))}
                        className="input"
                        style={{ maxWidth: "9rem" }}
                        placeholder="Price"
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <button type="button" onClick={() => setEditingId(null)} className="btn btn-ghost">
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={() => saveEdit(product.id)}
                        className="btn btn-primary"
                        style={{ width: "auto" }}
                      >
                        Save
                      </button>
                    </div>
                  </li>
                ) : (
                  <li key={product.id} className="card flex items-center gap-4 p-3 shadow-none">
                    <span className="badge badge-neutral">#{product.id}</span>
                    <p className="min-w-0 flex-1 truncate font-medium">{product.name}</p>
                    <span className="badge badge-neutral">${product.price.toFixed(2)}</span>
                    <button
                      type="button"
                      onClick={() => startEdit(product)}
                      className="icon-btn"
                      aria-label={`Edit ${product.name}`}
                      style={{ color: "var(--foreground)" }}
                    >
                      ✎
                    </button>
                    <button
                      type="button"
                      onClick={() => deleteProduct(product.id)}
                      className="icon-btn"
                      aria-label={`Delete ${product.name}`}
                    >
                      🗑
                    </button>
                  </li>
                )
              )}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
