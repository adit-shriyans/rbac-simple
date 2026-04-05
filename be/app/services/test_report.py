from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET


@dataclass
class ReportSummary:
    total: int
    passed: int
    failures: int
    errors: int
    skipped: int
    duration_seconds: float
    generated_at: str
    report_path: str

    def to_dict(self) -> dict:
        return asdict(self)


def report_directory() -> Path:
    return Path(__file__).resolve().parents[2] / "test_reports"


def xml_report_path() -> Path:
    return report_directory() / "latest.xml"


def html_report_path() -> Path:
    return report_directory() / "latest.html"


def parse_junit_xml(xml_path: Path) -> ReportSummary:
    root = ET.parse(xml_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise ValueError("Invalid JUnit XML report.")

    total = int(suite.attrib.get("tests", 0))
    failures = int(suite.attrib.get("failures", 0))
    errors = int(suite.attrib.get("errors", 0))
    skipped = int(suite.attrib.get("skipped", 0))
    passed = max(total - failures - errors - skipped, 0)

    return ReportSummary(
        total=total,
        passed=passed,
        failures=failures,
        errors=errors,
        skipped=skipped,
        duration_seconds=float(suite.attrib.get("time", 0.0)),
        generated_at=datetime.now(UTC).isoformat(),
        report_path="/api/tests/report",
    )


def write_html_report(summary: ReportSummary, xml_path: Path, html_path: Path) -> None:
    root = ET.parse(xml_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    testcases = suite.findall("testcase") if suite is not None else []

    rows = []
    for testcase in testcases:
        classname = testcase.attrib.get("classname", "")
        name = testcase.attrib.get("name", "")
        duration = testcase.attrib.get("time", "0")
        failure = testcase.find("failure")
        error = testcase.find("error")
        skipped = testcase.find("skipped")

        status = "passed"
        details = ""
        if failure is not None:
            status = "failed"
            details = failure.attrib.get("message", "") or (failure.text or "")
        elif error is not None:
            status = "error"
            details = error.attrib.get("message", "") or (error.text or "")
        elif skipped is not None:
            status = "skipped"
            details = skipped.attrib.get("message", "") or (skipped.text or "")

        rows.append(
            f"""
            <tr>
              <td>{classname}</td>
              <td>{name}</td>
              <td><span class="badge {status}">{status}</span></td>
              <td>{duration}s</td>
              <td><pre>{details.strip()}</pre></td>
            </tr>
            """
        )

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Zorvyn Test Report</title>
    <style>
      body {{ margin: 0; padding: 24px; font-family: Segoe UI, Arial, sans-serif; background: #0f172a; color: #f8fafc; }}
      .wrap {{ max-width: 1200px; margin: 0 auto; }}
      .hero, .panel {{ background: #111827; border: 1px solid rgba(248,250,252,0.12); border-radius: 20px; padding: 20px; margin-bottom: 16px; }}
      .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 16px; }}
      .stat {{ border: 1px solid rgba(248,250,252,0.12); border-radius: 16px; padding: 14px; background: #0b1220; }}
      .stat span {{ display: block; color: #94a3b8; margin-bottom: 6px; font-size: 0.9rem; }}
      table {{ width: 100%; border-collapse: collapse; }}
      th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid rgba(248,250,252,0.12); padding: 12px 10px; }}
      th {{ color: #94a3b8; }}
      .badge {{ display: inline-block; border-radius: 999px; padding: 0.25rem 0.6rem; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; }}
      .passed {{ background: rgba(16,185,129,0.18); color: #10b981; }}
      .failed {{ background: rgba(239,68,68,0.18); color: #ef4444; }}
      .error {{ background: rgba(249,115,22,0.18); color: #f97316; }}
      .skipped {{ background: rgba(234,179,8,0.18); color: #eab308; }}
      pre {{ margin: 0; white-space: pre-wrap; color: #e2e8f0; }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <section class="hero">
        <h1>Zorvyn Backend Test Report</h1>
        <p>Generated at {summary.generated_at}</p>
        <div class="stats">
          <div class="stat"><span>Total</span><strong>{summary.total}</strong></div>
          <div class="stat"><span>Passed</span><strong>{summary.passed}</strong></div>
          <div class="stat"><span>Failures</span><strong>{summary.failures}</strong></div>
          <div class="stat"><span>Errors</span><strong>{summary.errors}</strong></div>
          <div class="stat"><span>Skipped</span><strong>{summary.skipped}</strong></div>
          <div class="stat"><span>Duration</span><strong>{summary.duration_seconds:.2f}s</strong></div>
        </div>
      </section>
      <section class="panel">
        <table>
          <thead>
            <tr><th>Class</th><th>Test</th><th>Status</th><th>Time</th><th>Details</th></tr>
          </thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </section>
    </div>
  </body>
</html>"""

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
