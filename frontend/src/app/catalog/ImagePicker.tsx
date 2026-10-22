"use client";
import { ChangeEvent, DragEvent, useEffect, useMemo, useRef, useState } from "react";

export const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const ACCEPT = "image/png,image/jpeg,image/gif,image/webp";

// Returns an error message, or null if the file is fine to upload.
export function checkImage(file: File): string | null {
  if (!file.type.startsWith("image/")) return "Please choose an image file (jpg, png, gif, webp)";
  if (file.size > MAX_IMAGE_BYTES) return "Image must be 5 MB or smaller";
  return null;
}

/**
 * Picks an image and previews it locally before anything is uploaded.
 * `file` = newly picked file (not uploaded yet), `currentUrl` = image the product already has.
 */
export default function ImagePicker({
  id,
  file,
  currentUrl,
  onPick,
  onClear,
  onError,
  compact = false,
}: {
  id: string;
  file: File | null;
  currentUrl: string | null;
  onPick: (file: File) => void;
  onClear: () => void;
  onError: (message: string) => void;
  compact?: boolean;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragging, setDragging] = useState(false);

  // blob: URL so the picked file shows instantly, before the upload happens
  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const shown = previewUrl ?? currentUrl;

  function take(picked: File | undefined) {
    if (!picked) return;
    const problem = checkImage(picked);
    if (problem) {
      onError(problem);
      return;
    }
    onPick(picked);
  }

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    take(event.target.files?.[0]);
    event.target.value = ""; // so picking the same file again still fires onChange
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setDragging(false);
    take(event.dataTransfer.files?.[0]);
  }

  function clear() {
    if (inputRef.current) inputRef.current.value = "";
    onClear();
  }

  return (
    <div className={compact ? "image-picker compact" : "image-picker"}>
      <input
        ref={inputRef}
        id={id}
        type="file"
        accept={ACCEPT}
        onChange={handleChange}
        className="sr-only"
      />

      {shown ? (
        <div className="image-picker-preview">
          {/* eslint-disable-next-line @next/next/no-img-element -- blob: or FastAPI URL, not optimizable by next/image */}
          <img src={shown} alt="Product preview" />
          <div className="image-picker-actions">
            <label htmlFor={id} className="image-picker-btn">
              Change
            </label>
            <button type="button" onClick={clear} className="image-picker-btn danger">
              Remove
            </button>
          </div>
          {file && <span className="image-picker-pending">Not uploaded yet</span>}
        </div>
      ) : (
        <label
          htmlFor={id}
          className={dragging ? "image-picker-drop dragging" : "image-picker-drop"}
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
        >
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <rect x="3" y="4" width="18" height="16" rx="3" stroke="currentColor" strokeWidth="1.7" />
            <circle cx="9" cy="10" r="1.8" stroke="currentColor" strokeWidth="1.7" />
            <path d="m4 18 5-5 4 4 3-3 4 4" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
          </svg>
          <span className="text-sm font-semibold">
            {compact ? "Add image" : "Click or drop an image"}
          </span>
          {!compact && <span className="text-xs text-muted">JPG, PNG, GIF, WEBP · up to 5 MB</span>}
        </label>
      )}
    </div>
  );
}
