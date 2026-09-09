"use client";
import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

type Category = {
  id: number;
  name: string;
};

type Product = {
  id: number;
  name: string;
  description: string | null;
  price: number;
  categories: Category[];
};

type Feedback = {
  type: "success" | "error";
  text: string;
};

const API_URL = "http://127.0.0.1:8002";

function ChipToggle({
  label,
  selected,
  onClick,
}: {
  label: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={selected ? "chip-toggle selected" : "chip-toggle"}
    >
      {label}
    </button>
  );
}

export default function CatalogPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  const [categoryName, setCategoryName] = useState("");
  const [addingCategory, setAddingCategory] = useState(false);

  const [productName, setProductName] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const [productPrice, setProductPrice] = useState("");
  const [productCategoryIds, setProductCategoryIds] = useState<number[]>([]);
  const [addingProduct, setAddingProduct] = useState(false);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editDraft, setEditDraft] = useState({
    name: "",
    description: "",
    price: "",
    categoryIds: [] as number[],
  });

  // LOAD everything
  useEffect(() => {
    async function load() {
      try {
        const [categoriesRes, productsRes] = await Promise.all([
          fetch(`${API_URL}/categories/`),
          fetch(`${API_URL}/products/`),
        ]);

        if (!categoriesRes.ok || !productsRes.ok) {
          throw new Error("Failed to fetch catalog");
        }

        setCategories(await categoriesRes.json());
        setProducts(await productsRes.json());
      } catch (error) {
        console.error(error);
        setFeedback({ type: "error", text: "Failed to fetch catalog" });
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  function toggleId(ids: number[], id: number) {
    return ids.includes(id) ? ids.filter((existing) => existing !== id) : [...ids, id];
  }

  // CREATE category
  async function addCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback(null);
    setAddingCategory(true);

    try {
      const response = await fetch(`${API_URL}/categories/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: categoryName }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to add category");
      }

      setCategories((current) => [...current, result]);
      setCategoryName("");
      setFeedback({ type: "success", text: "Category added" });
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to add category";
      setFeedback({ type: "error", text });
    } finally {
      setAddingCategory(false);
    }
  }

  // DELETE category
  async function deleteCategory(categoryId: number) {
    setFeedback(null);

    try {
      const response = await fetch(`${API_URL}/categories/${categoryId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || "Failed to delete category");
      }

      setCategories((current) => current.filter((category) => category.id !== categoryId));
      setProducts((current) =>
        current.map((product) => ({
          ...product,
          categories: product.categories.filter((category) => category.id !== categoryId),
        }))
      );
      setFeedback({ type: "success", text: "Category deleted" });
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to delete category";
      setFeedback({ type: "error", text });
    }
  }

  // CREATE product
  async function addProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback(null);
    setAddingProduct(true);

    try {
      const response = await fetch(`${API_URL}/products/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: productName,
          description: productDescription.trim() === "" ? null : productDescription,
          price: Number(productPrice),
          category_ids: productCategoryIds,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to add product");
      }

      setProducts((current) => [...current, result]);
      setFeedback({ type: "success", text: "Product added" });
      setProductName("");
      setProductDescription("");
      setProductPrice("");
      setProductCategoryIds([]);
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to add product";
      setFeedback({ type: "error", text });
    } finally {
      setAddingProduct(false);
    }
  }

  // DELETE product
  async function deleteProduct(productId: number) {
    setFeedback(null);

    try {
      const response = await fetch(`${API_URL}/products/${productId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.detail || "Failed to delete product");
      }

      setProducts((current) => current.filter((product) => product.id !== productId));
      setFeedback({ type: "success", text: "Product deleted" });
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to delete product";
      setFeedback({ type: "error", text });
    }
  }

  // EDIT product
  function startEdit(product: Product) {
    setFeedback(null);
    setEditingId(product.id);
    setEditDraft({
      name: product.name,
      description: product.description ?? "",
      price: String(product.price),
      categoryIds: product.categories.map((category) => category.id),
    });
  }

  async function saveEdit(productId: number) {
    const newPrice = Number(editDraft.price);
    if (editDraft.name.trim() === "" || Number.isNaN(newPrice)) {
      setFeedback({ type: "error", text: "Name and price are required" });
      return;
    }

    setFeedback(null);

    try {
      const response = await fetch(`${API_URL}/products/${productId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: editDraft.name,
          description: editDraft.description.trim() === "" ? null : editDraft.description,
          price: newPrice,
          category_ids: editDraft.categoryIds,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to update product");
      }

      setProducts((current) =>
        current.map((product) => (product.id === productId ? result : product))
      );
      setFeedback({ type: "success", text: "Product updated" });
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
          <h1 className="text-2xl font-bold tracking-tight">Catalog</h1>
          <p className="text-sm text-muted">Products and categories (many-to-many)</p>
        </div>
        <Link href="/products" className="text-sm text-muted hover:underline">
          ← Products
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
        <div className="flex flex-col gap-6">
          <section className="card p-6">
            <h2 className="mb-4 text-base font-semibold">Add category</h2>
            <form onSubmit={addCategory} className="flex flex-col gap-4">
              <div>
                <label className="field-label" htmlFor="category-name">
                  Name
                </label>
                <input
                  id="category-name"
                  type="text"
                  placeholder="e.g. Electronics"
                  value={categoryName}
                  onChange={(event) => setCategoryName(event.target.value)}
                  required
                  className="input"
                />
              </div>
              <button type="submit" disabled={addingCategory} className="btn btn-primary">
                {addingCategory ? "Adding…" : "+ Add category"}
              </button>
            </form>

            {categories.length > 0 && (
              <ul className="mt-5 flex flex-col gap-2">
                {categories.map((category) => (
                  <li
                    key={category.id}
                    className="flex items-center justify-between gap-2 border-t pt-2 text-sm"
                    style={{ borderColor: "var(--border)" }}
                  >
                    <span>{category.name}</span>
                    <button
                      type="button"
                      onClick={() => deleteCategory(category.id)}
                      className="icon-btn"
                      style={{ width: "1.8rem", height: "1.8rem" }}
                      aria-label={`Delete ${category.name}`}
                    >
                      🗑
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

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
                  placeholder="e.g. USB Hub"
                  value={productName}
                  onChange={(event) => setProductName(event.target.value)}
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
                  placeholder="e.g. 4-port"
                  value={productDescription}
                  onChange={(event) => setProductDescription(event.target.value)}
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
                  value={productPrice}
                  onChange={(event) => setProductPrice(event.target.value)}
                  required
                  className="input"
                />
              </div>

              <div>
                <span className="field-label">Categories</span>
                {categories.length === 0 ? (
                  <p className="text-xs text-muted">Add a category first.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {categories.map((category) => (
                      <ChipToggle
                        key={category.id}
                        label={category.name}
                        selected={productCategoryIds.includes(category.id)}
                        onClick={() =>
                          setProductCategoryIds((ids) => toggleId(ids, category.id))
                        }
                      />
                    ))}
                  </div>
                )}
              </div>

              <button type="submit" disabled={addingProduct} className="btn btn-primary">
                {addingProduct ? "Adding…" : "+ Add product"}
              </button>
            </form>
          </section>
        </div>

        <section className="card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">All products</h2>
            <span className="badge badge-neutral">{products.length} total</span>
          </div>

          {loading ? (
            <div className="flex flex-col gap-3">
              <div className="skeleton h-20 w-full animate-pulse" />
              <div className="skeleton h-20 w-full animate-pulse" />
            </div>
          ) : products.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-14 text-center text-muted">
              <span className="text-3xl">🏷️</span>
              <p className="text-sm">No products yet — add your first one.</p>
            </div>
          ) : (
            <ul className="flex flex-col gap-3">
              {products.map((product) =>
                editingId === product.id ? (
                  <li key={product.id} className="card flex flex-col gap-3 p-3 shadow-none">
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
                          setEditDraft((draft) => ({
                            ...draft,
                            description: event.target.value,
                          }))
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

                    <div className="flex flex-wrap gap-2">
                      {categories.map((category) => (
                        <ChipToggle
                          key={category.id}
                          label={category.name}
                          selected={editDraft.categoryIds.includes(category.id)}
                          onClick={() =>
                            setEditDraft((draft) => ({
                              ...draft,
                              categoryIds: toggleId(draft.categoryIds, category.id),
                            }))
                          }
                        />
                      ))}
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
                  <li key={product.id} className="card flex flex-col gap-2 p-3 shadow-none">
                    <div className="flex items-center gap-4">
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
                    </div>

                    {product.categories.length > 0 && (
                      <div className="flex flex-wrap gap-2 pl-0">
                        {product.categories.map((category) => (
                          <span key={category.id} className="badge badge-neutral">
                            {category.name}
                          </span>
                        ))}
                      </div>
                    )}
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
