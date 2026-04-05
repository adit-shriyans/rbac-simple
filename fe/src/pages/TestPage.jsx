import { useMutation, useQuery } from "@tanstack/react-query";
import Panel from "../components/Panel";
import JsonBlock from "../components/JsonBlock";
import { API_BASE_URL, apiRequest } from "../lib/api";

export default function TestPage() {
  const statusQuery = useQuery({
    queryKey: ["test-report-status"],
    queryFn: () => apiRequest("/tests/status", { role: "admin" }),
  });

  const runTests = useMutation({
    mutationFn: () => apiRequest("/tests/run", { method: "POST", role: "admin" }),
    onSuccess: () => statusQuery.refetch(),
  });

  const origin = API_BASE_URL.replace(/\/api$/, "");
  const reportUrl =
    runTests.data?.report_url
      ? `${origin}${runTests.data.report_url}`
      : statusQuery.data?.has_report
        ? `${API_BASE_URL}/tests/report`
        : null;

  return (
    <main className="layout">
      <Panel
        title="Backend Tests"
        description={`viewer - can view the report page
analyst - can view the report page
admin - can run the backend test suite and view the report`}
      >
        <div className="query-row">
          <button type="button" onClick={() => runTests.mutate()} disabled={runTests.isPending}>
            {runTests.isPending ? "Running tests..." : "Run tests"}
          </button>
          <button type="button" className="secondary-button" onClick={() => statusQuery.refetch()}>
            Refresh report status
          </button>
        </div>

        {runTests.error ? <p className="error-text">{runTests.error.message}</p> : null}
        {statusQuery.error ? <p className="error-text">{statusQuery.error.message}</p> : null}

        {runTests.data?.summary ? <JsonBlock value={runTests.data.summary} /> : null}
        {!runTests.data?.summary && statusQuery.data?.has_report ? (
          <JsonBlock value={statusQuery.data} />
        ) : null}

        {reportUrl ? (
          <iframe className="report-frame" title="Backend test report" src={reportUrl} />
        ) : (
          <p className="empty-state">No report yet. Click run tests to generate one.</p>
        )}
      </Panel>
    </main>
  );
}
