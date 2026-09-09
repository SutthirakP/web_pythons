"use client";
import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

type Product = {
  id: number;
  name: string;
  description: string | null;
  price: number;
};

type Feedback = {
  type: "success" | "error";
  text: string;
};

const API_URL = "http://127.0.0.1:8001/products";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editDraft, setEditDraft] = useState({ name: "", description: "", price: "" });

  // READ ALL
  useEffect(() => {
    async function getProducts() {
      try {
        const response = await fetch(`${API_URL}/`);

        if (!response.ok) {
          throw new Error("Failed to fetch products");
        }

        const result: Product[] = await response.json();
        setProducts(result);
      } catch (error) {
        console.error(error);
        setFeedback({ type: "error", text: "Failed to fetch products" });
      } finally {
        setLoading(false);
      }
    }

    getProducts();
  }, []);

  // CREATE
  async function addProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback(null);
    setSubmitting(true);

    try {
      const response = await fetch(`${API_URL}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          description: description.trim() === "" ? null : description,
          price: Number(price),
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to add product");
      }

      setProducts((current) => [...current, result]);
      setFeedback({ type: "success", text: "Product added successfully" });
      setName("");
      setDescription("");
      setPrice("");
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to add product";
      setFeedback({ type: "error", text });
    } finally {
      setSubmitting(false);
    }
  }

  // DELETE
  async function deleteProduct(productId: number) {
    setFeedback(null);

    try {
      const response = await fetch(`${API_URL}/${productId}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to delete product");
      }

      setProducts((current) => current.filter((product) => product.id !== productId));
      setFeedback({ type: "success", text: result.message });
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to delete product";
      setFeedback({ type: "error", text });
    }
  }

  // EDIT
  function startEdit(product: Product) {
    setFeedback(null);
    setEditingId(product.id);
    setEditDraft({
      name: product.name,
      description: product.description ?? "",
      price: String(product.price),
    });
  }

  async function saveEdit(productId: number) {
    const newPrice = Number(editDraft.price);
    if (editDraft.name.trim() === "" || editDraft.price.trim() === "" || Number.isNaN(newPrice)) {
      setFeedback({ type: "error", text: "Name and price are required" });
      return;
    }

    setFeedback(null);

    try {
      const response = await fetch(`${API_URL}/${productId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: editDraft.name,
          description: editDraft.description.trim() === "" ? null : editDraft.description,
          price: newPrice,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to update product");
      }

      setProducts((current) =>
        current.map((product) => (product.id === productId ? result : product))
      );
      setFeedback({ type: "success", text: "Product updated successfully" });
      setEditingId(null);
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to update product";
      setFeedback({ type: "error", text });
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Products</h1>
          <p className="text-sm text-muted">Manage the product catalog</p>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/" className="text-sm text-muted hover:underline">
            ← Students
          </Link>
          <Link href="/catalog" className="text-sm text-muted hover:underline">
            Catalog →
          </Link>
        </div>
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
              <label className="field-label" htmlFor="product-name">
                Name
              </label>
              <input
                id="product-name"
                type="text"
                placeholder="e.g. Keyboard"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
                className="input"
              />
            </div>

            <div>
              <label className="field-label" htmlFor="product-description">
                Description
              </label>
              <input
                id="product-description"
                type="text"
                placeholder="e.g. Mechanical, RGB"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                className="input"
              />
            </div>

            <div>
              <label className="field-label" htmlFor="product-price">
                Price
              </label>
              <input
                id="product-price"
                type="number"
                step="0.01"
                placeholder="0.00"
                value={price}
                onChange={(event) => setPrice(event.target.value)}
                required
                className="input"
              />
            </div>

            <button type="submit" disabled={submitting} className="btn btn-primary mt-1">
              {submitting ? "Adding…" : "+ Add product"}
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
              <div className="skeleton h-16 w-full animate-pulse" />
            </div>
          ) : products.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-14 text-center text-muted">
              <span className="text-3xl">📦</span>
              <p className="text-sm">No products yet — add your first one.</p>
            </div>
          ) : (
            <ul className="flex flex-col gap-3">
              {products.map((product) =>
                editingId === product.id ? (
                  <li key={product.id} className="card flex flex-col gap-2 p-3 shadow-none">
                    <div className="flex flex-col gap-2 sm:flex-row">
                      <input
                        value={editDraft.name}
                        onChange={(event) =>
                          setEditDraft((draft) => ({ ...draft, name: event.target.value }))
                        }
                        className="input"
                        placeholder="Name"
                      />
                      <input
                        value={editDraft.description}
                        onChange={(event) =>
                          setEditDraft((draft) => ({ ...draft, description: event.target.value }))
                        }
                        className="input"
                        placeholder="Description"
                      />
                      <input
                        type="number"
                        step="0.01"
                        value={editDraft.price}
                        onChange={(event) =>
                          setEditDraft((draft) => ({ ...draft, price: event.target.value }))
                        }
                        className="input"
                        style={{ maxWidth: "8rem" }}
                        placeholder="Price"
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => setEditingId(null)}
                        className="btn btn-ghost"
                      >
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
                  <li
                    key={product.id}
                    className="card flex items-center gap-4 p-3 shadow-none"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-medium">{product.name}</p>
                      <p className="truncate text-xs text-muted">
                        {product.description || "No description"}
                      </p>
                    </div>

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
