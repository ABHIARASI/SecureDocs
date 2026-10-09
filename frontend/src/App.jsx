import { useState, useEffect } from "react";

import "./App.css";

import api from "./api";



function App() {

  const [token, setToken] = useState(

    () => localStorage.getItem("securedocs_token")

  );

  const [authMode, setAuthMode] = useState("login");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [activePage, setActivePage] = useState("Documents");



  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");

  const [error, setError] = useState("");



  const [documents, setDocuments] = useState([]);

  const [documentsLoading, setDocumentsLoading] = useState(false);

  const [documentsError, setDocumentsError] = useState("");



  const [query, setQuery] = useState("");

  const [answer, setAnswer] = useState("");

  const [sources, setSources] = useState([]);

  const [searchLoading, setSearchLoading] = useState(false);

  const [searchError, setSearchError] = useState("");



  // Fetch documents whenever the authenticated user opens Documents.

  useEffect(() => {

    if (!token || activePage !== "Documents") return;



    let cancelled = false;



    async function fetchDocuments() {

      setDocumentsLoading(true);

      setDocumentsError("");



      try {

        const response = await api.get("/documents/");



        if (!cancelled) {

          setDocuments(response.data);

        }

      } catch (err) {

        if (!cancelled) {

          setDocumentsError(

            err.response?.data?.detail ||

              "Unable to load documents. Please try again."

          );

        }

      } finally {

        if (!cancelled) {

          setDocumentsLoading(false);

        }

      }

    }



    fetchDocuments();



    return () => {

      cancelled = true;

    };

  }, [token, activePage]);



  async function handleAuth(event) {

    event.preventDefault();

    setLoading(true);

    setMessage("");

    setError("");



    try {

      if (authMode === "register") {

        await api.post("/auth/register", {

          email: email.trim(),

          password,

        });



        setAuthMode("login");

        setPassword("");

        setMessage("Account created. You can now sign in.");

      } else {

        const formData = new URLSearchParams();

        formData.append("username", email.trim());

        formData.append("password", password);



        const response = await api.post(

          "/auth/login",

          formData,

          {

            headers: {

              "Content-Type": "application/x-www-form-urlencoded",

            },

          }

        );



        const accessToken = response.data.access_token;



        localStorage.setItem("securedocs_token", accessToken);

        setToken(accessToken);

        setPassword("");

        setActivePage("Documents");

      }

    } catch (err) {

      setError(

        err.response?.data?.detail ||

          "Something went wrong. Check your connection and try again."

      );

    } finally {

      setLoading(false);

    }

  }



  function handleLogout() {

    localStorage.removeItem("securedocs_token");

    setToken(null);

    setEmail("");

    setPassword("");

    setMessage("");

    setError("");

    setDocuments([]);

    setDocumentsError("");

    setQuery("");

    setAnswer("");

    setSources([]);

    setSearchError("");

    setActivePage("Documents");

  }



  async function handleUpload(event) {

    const file = event.target.files?.[0];

    event.target.value = "";



    if (!file) return;



    if (file.type !== "application/pdf") {

      setDocumentsError("Please select a PDF file.");

      return;

    }



    if (file.size > 10 * 1024 * 1024) {

      setDocumentsError("The PDF must be smaller than 10 MB.");

      return;

    }



    setDocumentsLoading(true);

    setDocumentsError("");



    const formData = new FormData();

    formData.append("file", file);



    try {

      await api.post("/documents/upload", formData);

      const response = await api.get("/documents/");

      setDocuments(response.data);

    } catch (err) {

      setDocumentsError(

        err.response?.data?.detail ||

          "Upload failed. Please try again."

      );

    } finally {

      setDocumentsLoading(false);

    }

  }



  async function handleDelete(documentId) {

    const confirmed = window.confirm(

      "Are you sure you want to delete this document?"

    );



    if (!confirmed) return;



    setDocumentsError("");



    try {

      await api.delete(`/documents/${documentId}`);



      setDocuments((currentDocuments) =>

        currentDocuments.filter(

          (document) => document.id !== documentId

        )

      );

    } catch (err) {

      setDocumentsError(

        err.response?.data?.detail ||

          "Could not delete the document."

      );

    }

  }



  async function handleSearch(event) {

    event.preventDefault();



    if (!query.trim()) return;



    setSearchLoading(true);

    setSearchError("");

    setAnswer("");

    setSources([]);



    try {

      const response = await api.post("/search/", {

        query: query.trim(),

      });



      setAnswer(response.data.answer);

      setSources(response.data.sources || []);

    } catch (err) {

      setSearchError(

        err.response?.data?.detail ||

          "Search failed. Please try again."

      );

    } finally {

      setSearchLoading(false);

    }

  }



  if (!token) {

    return (

      <div className="auth-page">

        <div className="auth-brand">

          <div className="brand-icon">S</div>

          <span>SecureDocs</span>

        </div>



        <div className="auth-card">

          <p className="eyebrow">YOUR PRIVATE KNOWLEDGE BASE</p>



          <h1>

            {authMode === "login"

              ? "Welcome back"

              : "Create your account"}

          </h1>



          <p className="subtitle">

            {authMode === "login"

              ? "Sign in to access your documents and AI search."

              : "Create an account to securely manage your documents."}

          </p>



          <form onSubmit={handleAuth} className="auth-form">

            <label htmlFor="email">Email address</label>

            <input

              id="email"

              type="email"

              autoComplete="email"

              placeholder="you\@example.com"

              value={email}

              onChange={(event) => setEmail(event.target.value)}

              required

            />



            <label htmlFor="password">Password</label>

            <input

              id="password"

              type="password"

              autoComplete={

                authMode === "login"

                  ? "current-password"

                  : "new-password"

              }

              placeholder="Enter your password"

              value={password}

              onChange={(event) => setPassword(event.target.value)}

              required

            />



            {message && (

              <p className="success-message">{message}</p>

            )}



            {error && <p className="error-message">{error}</p>}



            <button

              className="primary-button auth-submit"

              type="submit"

              disabled={loading}

            >

              {loading

                ? "Please wait..."

                : authMode === "login"

                  ? "Sign in"

                  : "Create account"}

            </button>

          </form>



          <p className="auth-switch">

            {authMode === "login"

              ? "Don't have an account?"

              : "Already have an account?"}{" "}

            <button

              type="button"

              onClick={() => {

                setAuthMode(

                  authMode === "login" ? "register" : "login"

                );

                setMessage("");

                setError("");

              }}

            >

              {authMode === "login" ? "Create one" : "Sign in"}

            </button>

          </p>

        </div>



        <p className="auth-footer">

          Secure document storage and AI-powered retrieval.

        </p>

      </div>

    );

  }



  return (

    <div className="app">

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-icon">S</div>

          <span>SecureDocs</span>

        </div>



        <p className="nav-label">WORKSPACE</p>



        <button

          className={`nav-item ${

            activePage === "Documents" ? "active" : ""

          }`}

          onClick={() => setActivePage("Documents")}

        >

          <span>▤</span>

          Documents

        </button>



        <button

          className={`nav-item ${

            activePage === "AI Search" ? "active" : ""

          }`}

          onClick={() => setActivePage("AI Search")}

        >

          <span>⌕</span>

          AI Search

        </button>



        <div className="sidebar-bottom">

          <div className="avatar">

            {(email.trim()[0] || "U").toUpperCase()}

          </div>

          <div>

            <p className="user-name">

              {email || "Signed-in user"}

            </p>

            <p className="user-role">Personal workspace</p>

          </div>

        </div>

      </aside>



      <main className="main">

        <header className="topbar">

          <span>Workspace / {activePage}</span>



          <button

            className="logout-button"

            onClick={handleLogout}

          >

            Sign out

          </button>

        </header>



        {activePage === "Documents" ? (

          <section className="content">

            <div className="page-heading">

              <div>

                <p className="eyebrow">YOUR WORKSPACE</p>

                <h1>My Documents</h1>

                <p className="subtitle">

                  Manage and search your documents securely.

                </p>

              </div>



              <button

                className="primary-button"

                onClick={() => setActivePage("AI Search")}

              >

                Ask your documents

              </button>

            </div>



            <div className="dashboard-hero">
              <div className="dashboard-hero-copy">
                <p className="hero-kicker">YOUR KNOWLEDGE, ORGANIZED</p>
                <h2>Your documents. One intelligent search.</h2>
                <p>Upload PDFs, find useful passages, and get answers grounded in your own files.</p>
              </div>
              <button className="hero-action" type="button" onClick={() => setActivePage("AI Search")}>
                Open AI Search <span aria-hidden="true">→</span>
              </button>
              <div className="hero-decoration" aria-hidden="true">
                <span className="hero-sheet sheet-one"></span>
                <span className="hero-sheet sheet-two"></span>
                <span className="hero-sheet sheet-three">PDF</span>
              </div>
            </div>

            <div className="stats-grid">

              <div className="stat-card">

                <p>Total documents</p>

                <h2>

                  {documentsLoading ? "..." : documents.length}

                </h2>

                <span>PDFs in your document library</span>

              </div>



              <div className="stat-card">

                <p>AI-powered search</p>

                <h2>Available</h2>

                <span>

                  Search your uploaded document content.

                </span>

              </div>



              <div className="stat-card">

                <p>Access control</p>

                <h2>Enabled</h2>

                <span>

                  Requests use your authentication token.

                </span>

              </div>

            </div>



            <div className="section-heading">

              <div>

                <h2>Document library</h2>

                <p>Your uploaded PDF files.</p>

              </div>



              <label className="primary-button upload-button">

                Upload PDF

                <input

                  type="file"

                  accept=".pdf,application/pdf"

                  onChange={handleUpload}

                  disabled={documentsLoading}

                  hidden

                />

              </label>

            </div>



            {documentsLoading ? (

              <div className="empty-state">

                <p>Loading your documents...</p>

              </div>

            ) : documentsError ? (

              <div className="empty-state">

                <h3>Couldn't load documents</h3>

                <p>{documentsError}</p>

                <button

                  className="secondary-button"

                  onClick={() => {

                    setActivePage("AI Search");

                    setActivePage("Documents");

                  }}

                >

                  Retry

                </button>

              </div>

            ) : documents.length === 0 ? (

              <div className="empty-state">

                <div className="empty-icon">PDF</div>

                <h3>No documents yet</h3>

                <p>

                  Upload a PDF to start building your searchable

                  document library.

                </p>

              </div>

            ) : (

              <div className="document-list">

                {documents.map((document) => (

                  <div

                    className="document-card"

                    key={document.id}

                  >

                    <div className="document-icon">PDF</div>



                    <div className="document-info">

                      <h3>{document.filename}</h3>

                      <p>

                        Uploaded{" "}

                        {document.uploaded_at

                          ? new Date(

                              document.uploaded_at

                            ).toLocaleDateString()

                          : "date unavailable"}

                      </p>

                    </div>



                    <div className="document-actions">

                      <span className="document-status">Processed</span>



                      <button

                        className="delete-button"

                        onClick={() => handleDelete(document.id)}

                        aria-label={`Delete ${document.filename}`}

                      >

                        Delete

                      </button>

                    </div>

                  </div>

                ))}

              </div>

            )}

          </section>

        ) : (

          <section className="content">

            <p className="eyebrow">

              INTELLIGENT DOCUMENT RETRIEVAL

            </p>



            <h1>Ask your documents</h1>



            <p className="subtitle">

              Get answers grounded in your uploaded PDFs.

            </p>



            <form className="search-panel" onSubmit={handleSearch}>

              <label htmlFor="search-query">Your question</label>



              <textarea

                id="search-query"

                placeholder="What projects have I worked on?"

                rows={4}

                value={query}

                onChange={(event) => setQuery(event.target.value)}

                minLength={3}

                maxLength={500}

                required

              />



              {searchError && (

                <p className="error-message">{searchError}</p>

              )}



              <button

                className="primary-button"

                type="submit"

                disabled={searchLoading}

              >

                {searchLoading ? "Searching documents..." : "Ask AI"}

              </button>



              <p className="helper-text">

                Answers are generated from relevant passages in your documents.

              </p>

            </form>



            {answer && (

              <div className="search-results">

                <div className="result-heading">

                  <p className="eyebrow">AI RESPONSE</p>

                  <h2>Answer</h2>

                </div>



                <div className="answer-card">

                  <p className="answer-text">{answer}</p>

                </div>



                {sources.length > 0 && (

                  <div className="sources-section">

                    <h2>Sources</h2>

                    <p className="subtitle">

                      Relevant passages retrieved from your documents.

                    </p>



                    <div className="source-list">

                      {sources.map((source) => (

                        <article

                          className="source-card"

                          key={`${source.document_id}-${source.chunk_id}`}

                        >

                          <div className="source-header">

                            <h3>{source.document}</h3>



                            <span className="similarity">

                              Similarity:{" "}

                              {(

                                Number(source.similarity) * 100

                              ).toFixed(1)}%

                            </span>

                          </div>



                          <p>{source.chunk}</p>

                        </article>

                      ))}

                    </div>

                  </div>

                )}

              </div>

            )}

          </section>

        )}

      </main>

    </div>

  );

}



export default App;