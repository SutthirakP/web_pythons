"use client";
import { FormEvent, useEffect, useState } from "react";

type Student = {
  id: number;
  name: string;
  score: number;
};

type Feedback = {
  type: "success" | "error";
  text: string;
};

const API_URL = "http://127.0.0.1:8000/students";

function initials(name: string) {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

function scoreBadgeClass(score: number) {
  if (score >= 70) return "badge badge-success";
  if (score >= 50) return "badge badge-warning";
  return "badge badge-danger";
}

export default function Home() {
  const [students, setStudents] = useState<Student[]>([]);
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [score, setScore] = useState("");
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [resetting, setResetting] = useState(false);

  // GET STUDENTS
  useEffect(() => {
    async function getStudents() {
      try {
        const response = await fetch(API_URL);

        if (!response.ok) {
          throw new Error("Failed to fetch students");
        }

        const result: Student[] = await response.json();
        setStudents(result);
      } catch (error) {
        console.error(error);
        setFeedback({ type: "error", text: "Failed to fetch students" });
      } finally {
        setLoading(false);
      }
    }

    getStudents();
  }, []);

  // POST STUDENT
  async function addStudent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFeedback(null);
    setSubmitting(true);

    const newStudent: Student = {
      id: Number(id),
      name: name,
      score: Number(score),
    };

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newStudent),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to add student");
      }

      setStudents((currentStudents) => [...currentStudents, result]);
      setFeedback({ type: "success", text: "Student added successfully" });
      setId("");
      setName("");
      setScore("");
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to add student";
      setFeedback({ type: "error", text });
    } finally {
      setSubmitting(false);
    }
  }

  // DELETE STUDENT
  async function deleteStudent(studentId: number) {
    setFeedback(null);

    try {
      const response = await fetch(`${API_URL}/${studentId}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to delete student");
      }

      setStudents((currentStudents) =>
        currentStudents.filter((student) => student.id !== studentId)
      );
      setFeedback({ type: "success", text: result.message });
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to delete student";
      setFeedback({ type: "error", text });
    }
  }

  // RESET STUDENTS
  async function resetStudents() {
    setFeedback(null);
    setResetting(true);

    try {
      const response = await fetch(`${API_URL}/reset`, {
        method: "POST",
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to reset students");
      }

      setStudents(result);
      setFeedback({ type: "success", text: "Reset to default students" });
    } catch (error) {
      const text = error instanceof Error ? error.message : "Failed to reset students";
      setFeedback({ type: "error", text });
    } finally {
      setResetting(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <header>
        <h1 className="text-2xl font-bold tracking-tight">Student Records</h1>
        <p className="text-sm text-muted">Track and manage student scores</p>
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
          <h2 className="mb-4 text-base font-semibold">Add student</h2>
          <form onSubmit={addStudent} className="flex flex-col gap-4">
            <div>
              <label className="field-label" htmlFor="student-id">
                Student ID
              </label>
              <input
                id="student-id"
                type="number"
                placeholder="e.g. 4"
                value={id}
                onChange={(event) => setId(event.target.value)}
                required
                className="input"
              />
            </div>

            <div>
              <label className="field-label" htmlFor="student-name">
                Name
              </label>
              <input
                id="student-name"
                type="text"
                placeholder="e.g. Jane Doe"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
                className="input"
              />
            </div>

            <div>
              <label className="field-label" htmlFor="student-score">
                Score
              </label>
              <input
                id="student-score"
                type="number"
                placeholder="0-100"
                value={score}
                onChange={(event) => setScore(event.target.value)}
                required
                className="input"
              />
            </div>

            <button type="submit" disabled={submitting} className="btn btn-primary mt-1">
              {submitting ? "Adding…" : "+ Add student"}
            </button>
          </form>
        </section>

        <section className="card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">All students</h2>
            <div className="flex items-center gap-2">
              <span className="badge badge-neutral">{students.length} total</span>
              <button
                type="button"
                onClick={resetStudents}
                disabled={resetting}
                className="btn btn-ghost"
              >
                {resetting ? "Resetting…" : "Reset"}
              </button>
            </div>
          </div>

          {loading ? (
            <div className="flex flex-col gap-3">
              <div className="skeleton h-16 w-full animate-pulse" />
              <div className="skeleton h-16 w-full animate-pulse" />
              <div className="skeleton h-16 w-full animate-pulse" />
            </div>
          ) : students.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-14 text-center text-muted">
              <span className="text-3xl">🗂️</span>
              <p className="text-sm">No students yet — add your first one.</p>
            </div>
          ) : (
            <ul className="flex flex-col gap-3">
              {students.map((student) => (
                <li
                  key={student.id}
                  className="card flex items-center gap-4 p-3 shadow-none"
                >
                  <div className="avatar">{initials(student.name)}</div>

                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{student.name}</p>
                    <p className="text-xs text-muted">ID #{student.id}</p>
                  </div>

                  <span className={scoreBadgeClass(student.score)}>{student.score}</span>

                  <button
                    type="button"
                    onClick={() => deleteStudent(student.id)}
                    className="icon-btn"
                    aria-label={`Delete ${student.name}`}
                  >
                    🗑
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
