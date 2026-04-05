from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.test_report import (
    html_report_path,
    parse_junit_xml,
    report_directory,
    write_html_report,
    xml_report_path,
)

router = APIRouter(prefix="/tests", tags=["tests"])


def backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


@router.get("/status")
async def get_test_status():
    xml_path = xml_report_path()
    html_path = html_report_path()
    if not xml_path.exists() or not html_path.exists():
        return {"has_report": False}

    return {"has_report": True, **parse_junit_xml(xml_path).to_dict()}


@router.get("/report")
async def get_test_report():
    report_path = html_report_path()
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Test report not found. Run tests first.")
    return FileResponse(report_path, media_type="text/html")


@router.post("/run")
async def run_tests():
    root = backend_root()
    report_directory().mkdir(parents=True, exist_ok=True)
    xml_path = xml_report_path()
    html_path = html_report_path()

    def _run_pytest():
        return subprocess.run(
            [sys.executable, "-m", "pytest", f"--junitxml={xml_path}"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )

    process = await asyncio.to_thread(_run_pytest)
    stdout = process.stdout
    stderr = process.stderr

    if not xml_path.exists():
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Tests finished without generating a report.",
                "stdout": stdout,
                "stderr": stderr,
            },
        )

    summary = parse_junit_xml(xml_path)
    write_html_report(summary, xml_path, html_path)

    return {
        "message": "Tests completed.",
        "status": "passed" if process.returncode == 0 else "failed",
        "exit_code": process.returncode,
        "report_url": "/api/tests/report",
        "summary": summary.to_dict(),
        "stdout": stdout,
        "stderr": stderr,
    }
