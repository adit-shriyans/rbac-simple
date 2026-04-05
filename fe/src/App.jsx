import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Navbar from "./components/Navbar";
import Panel from "./components/Panel";
import JsonBlock from "./components/JsonBlock";
import { API_BASE_URL, apiRequest } from "./lib/api";
import TestPage from "./pages/TestPage";

const initialUserForm = {
  name: "Adit Analyst",
  email: "adit@example.com",
  role: "analyst",
  status: "active",
};

const initialUserUpdateForm = {
  userId: "1",
  name: "",
  email: "",
  role: "",
  status: "",
};

const initialRecordForm = {
  amount: "1250.50",
  type: "income",
  category: "Consulting",
  entry_date: "2026-04-01",
  notes: "Quarterly consulting payout",
  created_by_user_id: "",
};

const initialRecordUpdateForm = {
  recordId: "1",
  amount: "",
  type: "",
  category: "",
  entry_date: "",
  notes: "",
  created_by_user_id: "",
};

const initialRecordFilters = {
  page: "1",
  page_size: "10",
  category: "",
  type: "",
  start_date: "",
  end_date: "",
};

const initialDashboardFilters = {
  start_date: "",
  end_date: "",
};

function buildQueryString(filters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.set(key, value);
    }
  });
  const query = params.toString();
  return query ? `?${query}` : "";
}

function cleanBody(payload) {
  return Object.fromEntries(
    Object.entries(payload)
      .filter(([, value]) => value !== "" && value !== null && value !== undefined)
      .map(([key, value]) => {
        if (["amount"].includes(key)) {
          return [key, Number(value)];
        }
        if (["created_by_user_id"].includes(key)) {
          return [key, Number(value)];
        }
        return [key, value];
      })
  );
}

function MutationPanel({ title, mutation, children }) {
  return (
    <div className="mutation-card">
      <div className="mutation-head">
        <h3>{title}</h3>
        {mutation.isPending ? <span className="status-chip">Sending...</span> : null}
      </div>
      {children}
      {mutation.error ? <p className="error-text">{mutation.error.message}</p> : null}
      {mutation.data ? <JsonBlock value={mutation.data} /> : null}
    </div>
  );
}

export default function App() {
  const currentPath = window.location.pathname;
  const queryClient = useQueryClient();
  const [role, setRole] = useState("viewer");
  const [theme, setTheme] = useState("dark");
  const [userForm, setUserForm] = useState(initialUserForm);
  const [userUpdateForm, setUserUpdateForm] = useState(initialUserUpdateForm);
  const [recordForm, setRecordForm] = useState(initialRecordForm);
  const [recordUpdateForm, setRecordUpdateForm] = useState(initialRecordUpdateForm);
  const [recordFilters, setRecordFilters] = useState(initialRecordFilters);
  const [dashboardFilters, setDashboardFilters] = useState(initialDashboardFilters);
  const [deleteRecordId, setDeleteRecordId] = useState("1");

  const recordsQueryString = buildQueryString(recordFilters);
  const dashboardQueryString = buildQueryString(dashboardFilters);

  const usersQuery = useQuery({
    queryKey: ["users", role],
    queryFn: () => apiRequest("/users", { role }),
    enabled: false,
  });

  const recordsQuery = useQuery({
    queryKey: ["records", role, recordsQueryString],
    queryFn: () => apiRequest(`/records${recordsQueryString}`, { role }),
    enabled: false,
  });

  const dashboardQuery = useQuery({
    queryKey: ["dashboard", role, dashboardQueryString],
    queryFn: () => apiRequest(`/dashboard/summary${dashboardQueryString}`, { role }),
    enabled: false,
  });

  const refreshQueries = () => {
    queryClient.invalidateQueries({ queryKey: ["users"] });
    queryClient.invalidateQueries({ queryKey: ["records"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const createUser = useMutation({
    mutationFn: () => apiRequest("/users", { method: "POST", role, body: userForm }),
    onSuccess: refreshQueries,
  });

  const updateUser = useMutation({
    mutationFn: () =>
      apiRequest(`/users/${userUpdateForm.userId}`, {
        method: "PATCH",
        role,
        body: cleanBody({
          name: userUpdateForm.name,
          email: userUpdateForm.email,
          role: userUpdateForm.role,
          status: userUpdateForm.status,
        }),
      }),
    onSuccess: refreshQueries,
  });

  const createRecord = useMutation({
    mutationFn: () =>
      apiRequest("/records", {
        method: "POST",
        role,
        body: cleanBody(recordForm),
      }),
    onSuccess: refreshQueries,
  });

  const updateRecord = useMutation({
    mutationFn: () =>
      apiRequest(`/records/${recordUpdateForm.recordId}`, {
        method: "PATCH",
        role,
        body: cleanBody({
          amount: recordUpdateForm.amount,
          type: recordUpdateForm.type,
          category: recordUpdateForm.category,
          entry_date: recordUpdateForm.entry_date,
          notes: recordUpdateForm.notes,
          created_by_user_id: recordUpdateForm.created_by_user_id,
        }),
      }),
    onSuccess: refreshQueries,
  });

  const deleteRecord = useMutation({
    mutationFn: () => apiRequest(`/records/${deleteRecordId}`, { method: "DELETE", role }),
    onSuccess: refreshQueries,
  });

  return (
    <div className="app-shell" data-theme={theme}>
      <Navbar
        role={role}
        setRole={setRole}
        theme={theme}
        toggleTheme={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
        currentPath={currentPath}
      />

      {currentPath === "/test" ? (
        <TestPage />
      ) : (
      <main className="layout">
        <Panel
          title="Environment"
          description="Switch roles in the navbar and trigger requests without any frontend validation. Unauthorized actions should fail from the backend."
        >
          <div className="meta-grid">
            <div className="meta-card">
              <span>API base</span>
              <strong>{API_BASE_URL}</strong>
            </div>
            <div className="meta-card">
              <span>Current header</span>
              <strong>x-user-role: {role}</strong>
            </div>
          </div>
        </Panel>

        <Panel
          title="Users"
          description={`viewer - no permission
analyst - read permission
admin - create, read, and update permission`}
        >
          <div className="query-row">
            <button type="button" onClick={() => usersQuery.refetch()}>
              Reload users
            </button>
            {usersQuery.error ? <p className="error-text">{usersQuery.error.message}</p> : null}
          </div>
          {usersQuery.data ? <JsonBlock value={usersQuery.data} /> : null}

          <div className="form-grid">
            <MutationPanel title="Create user" mutation={createUser}>
              <input
                value={userForm.name}
                onChange={(event) => setUserForm((current) => ({ ...current, name: event.target.value }))}
                placeholder="name"
              />
              <input
                value={userForm.email}
                onChange={(event) => setUserForm((current) => ({ ...current, email: event.target.value }))}
                placeholder="email"
              />
              <select
                value={userForm.role}
                onChange={(event) => setUserForm((current) => ({ ...current, role: event.target.value }))}
              >
                <option value="viewer">viewer</option>
                <option value="analyst">analyst</option>
                <option value="admin">admin</option>
              </select>
              <select
                value={userForm.status}
                onChange={(event) => setUserForm((current) => ({ ...current, status: event.target.value }))}
              >
                <option value="active">active</option>
                <option value="inactive">inactive</option>
              </select>
              <button type="button" onClick={() => createUser.mutate()}>
                POST /users
              </button>
            </MutationPanel>

            <MutationPanel title="Update user" mutation={updateUser}>
              <input
                value={userUpdateForm.userId}
                onChange={(event) =>
                  setUserUpdateForm((current) => ({ ...current, userId: event.target.value }))
                }
                placeholder="user id"
              />
              <input
                value={userUpdateForm.name}
                onChange={(event) =>
                  setUserUpdateForm((current) => ({ ...current, name: event.target.value }))
                }
                placeholder="name"
              />
              <input
                value={userUpdateForm.email}
                onChange={(event) =>
                  setUserUpdateForm((current) => ({ ...current, email: event.target.value }))
                }
                placeholder="email"
              />
              <select
                value={userUpdateForm.role}
                onChange={(event) =>
                  setUserUpdateForm((current) => ({ ...current, role: event.target.value }))
                }
              >
                <option value="">role unchanged</option>
                <option value="viewer">viewer</option>
                <option value="analyst">analyst</option>
                <option value="admin">admin</option>
              </select>
              <select
                value={userUpdateForm.status}
                onChange={(event) =>
                  setUserUpdateForm((current) => ({ ...current, status: event.target.value }))
                }
              >
                <option value="">status unchanged</option>
                <option value="active">active</option>
                <option value="inactive">inactive</option>
              </select>
              <button type="button" onClick={() => updateUser.mutate()}>
                PATCH /users/:id
              </button>
            </MutationPanel>
          </div>
        </Panel>

        <Panel
          title="Financial Records"
          description={`viewer - read permission
analyst - read permission
admin - create, read, update, and delete permission`}
        >
          <div className="filter-grid">
            <input
              value={recordFilters.page}
              onChange={(event) => setRecordFilters((current) => ({ ...current, page: event.target.value }))}
              placeholder="page"
            />
            <input
              value={recordFilters.page_size}
              onChange={(event) =>
                setRecordFilters((current) => ({ ...current, page_size: event.target.value }))
              }
              placeholder="page size"
            />
            <input
              value={recordFilters.category}
              onChange={(event) =>
                setRecordFilters((current) => ({ ...current, category: event.target.value }))
              }
              placeholder="category"
            />
            <select
              value={recordFilters.type}
              onChange={(event) => setRecordFilters((current) => ({ ...current, type: event.target.value }))}
            >
              <option value="">all types</option>
              <option value="income">income</option>
              <option value="expense">expense</option>
            </select>
            <input
              value={recordFilters.start_date}
              onChange={(event) =>
                setRecordFilters((current) => ({ ...current, start_date: event.target.value }))
              }
              placeholder="start date"
            />
            <input
              value={recordFilters.end_date}
              onChange={(event) =>
                setRecordFilters((current) => ({ ...current, end_date: event.target.value }))
              }
              placeholder="end date"
            />
            <button type="button" onClick={() => recordsQuery.refetch()}>
              Reload records
            </button>
          </div>
          {recordsQuery.error ? <p className="error-text">{recordsQuery.error.message}</p> : null}
          {recordsQuery.data ? <JsonBlock value={recordsQuery.data} /> : null}

          <div className="form-grid">
            <MutationPanel title="Create record" mutation={createRecord}>
              <input
                value={recordForm.amount}
                onChange={(event) => setRecordForm((current) => ({ ...current, amount: event.target.value }))}
                placeholder="amount"
              />
              <select
                value={recordForm.type}
                onChange={(event) => setRecordForm((current) => ({ ...current, type: event.target.value }))}
              >
                <option value="income">income</option>
                <option value="expense">expense</option>
              </select>
              <input
                value={recordForm.category}
                onChange={(event) =>
                  setRecordForm((current) => ({ ...current, category: event.target.value }))
                }
                placeholder="category"
              />
              <input
                value={recordForm.entry_date}
                onChange={(event) =>
                  setRecordForm((current) => ({ ...current, entry_date: event.target.value }))
                }
                placeholder="entry date"
              />
              <input
                value={recordForm.notes}
                onChange={(event) => setRecordForm((current) => ({ ...current, notes: event.target.value }))}
                placeholder="notes"
              />
              <input
                value={recordForm.created_by_user_id}
                onChange={(event) =>
                  setRecordForm((current) => ({ ...current, created_by_user_id: event.target.value }))
                }
                placeholder="created by user id"
              />
              <button type="button" onClick={() => createRecord.mutate()}>
                POST /records
              </button>
            </MutationPanel>

            <MutationPanel title="Update record" mutation={updateRecord}>
              <input
                value={recordUpdateForm.recordId}
                onChange={(event) =>
                  setRecordUpdateForm((current) => ({ ...current, recordId: event.target.value }))
                }
                placeholder="record id"
              />
              <input
                value={recordUpdateForm.amount}
                onChange={(event) =>
                  setRecordUpdateForm((current) => ({ ...current, amount: event.target.value }))
                }
                placeholder="amount"
              />
              <select
                value={recordUpdateForm.type}
                onChange={(event) =>
                  setRecordUpdateForm((current) => ({ ...current, type: event.target.value }))
                }
              >
                <option value="">type unchanged</option>
                <option value="income">income</option>
                <option value="expense">expense</option>
              </select>
              <input
                value={recordUpdateForm.category}
                onChange={(event) =>
                  setRecordUpdateForm((current) => ({ ...current, category: event.target.value }))
                }
                placeholder="category"
              />
              <input
                value={recordUpdateForm.entry_date}
                onChange={(event) =>
                  setRecordUpdateForm((current) => ({ ...current, entry_date: event.target.value }))
                }
                placeholder="entry date"
              />
              <input
                value={recordUpdateForm.notes}
                onChange={(event) =>
                  setRecordUpdateForm((current) => ({ ...current, notes: event.target.value }))
                }
                placeholder="notes"
              />
              <button type="button" onClick={() => updateRecord.mutate()}>
                PATCH /records/:id
              </button>
            </MutationPanel>

            <MutationPanel title="Delete record" mutation={deleteRecord}>
              <input
                value={deleteRecordId}
                onChange={(event) => setDeleteRecordId(event.target.value)}
                placeholder="record id"
              />
              <button type="button" onClick={() => deleteRecord.mutate()}>
                DELETE /records/:id
              </button>
            </MutationPanel>
          </div>
        </Panel>

        <Panel
          title="Dashboard Summary"
          description={`viewer - no permission
analyst - read summary permission
admin - read summary permission`}
        >
          <div className="filter-grid">
            <input
              value={dashboardFilters.start_date}
              onChange={(event) =>
                setDashboardFilters((current) => ({ ...current, start_date: event.target.value }))
              }
              placeholder="start date"
            />
            <input
              value={dashboardFilters.end_date}
              onChange={(event) =>
                setDashboardFilters((current) => ({ ...current, end_date: event.target.value }))
              }
              placeholder="end date"
            />
            <button type="button" onClick={() => dashboardQuery.refetch()}>
              Reload summary
            </button>
          </div>
          {dashboardQuery.error ? <p className="error-text">{dashboardQuery.error.message}</p> : null}
          {dashboardQuery.data ? <JsonBlock value={dashboardQuery.data} /> : null}
        </Panel>
      </main>
      )}
    </div>
  );
}
