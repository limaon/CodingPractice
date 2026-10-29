"""Small Judge0 CE adapter; performs HTTP only when explicitly called."""

import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


class Judge0Error(Exception):
    pass


class Judge0Client:
    def __init__(self, endpoint, api_key="", timeout=12, max_wait=45):
        parsed = urlparse(endpoint)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise Judge0Error("Judge0 endpoint must be an HTTPS URL.")
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key.strip()
        self.timeout = timeout
        self.max_wait = max_wait

    def _request(self, path, payload=None):
        url = self.endpoint + path
        headers = {"Accept": "application/json", "User-Agent": "CodingPractice-Anki-Addon/0.2"}
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if self.api_key:
            headers["X-Auth-Token"] = self.api_key
        request = Request(url, data=data, headers=headers)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(128 * 1024 + 1)
            if len(raw) > 128 * 1024:
                raise Judge0Error("Judge0 response exceeded the size limit.")
            return json.loads(raw.decode("utf-8"))
        except HTTPError as error:
            raise Judge0Error("Judge0 returned HTTP %d." % error.code)
        except (URLError, TimeoutError, OSError) as error:
            raise Judge0Error("Could not reach Judge0: %s" % str(error)[:240])
        except (UnicodeError, ValueError):
            raise Judge0Error("Judge0 returned an invalid response.")

    def _languages(self):
        result = self._request("/languages")
        if not isinstance(result, list):
            raise Judge0Error("Judge0 returned an invalid language list.")
        return result

    @staticmethod
    def _language_match(language, entries):
        key = re.sub(r"[^a-z0-9+#.]", "", language.lower())
        aliases = {
            "py": "python", "python3": "python", "js": "javascript", "node": "javascript",
            "ts": "typescript", "cxx": "cpp", "c++": "cpp", "g++": "cpp",
            "csharp": "c#", "cs": "c#", "golang": "go",
        }
        key = aliases.get(key, key)
        patterns = {
            "python": r"^python\s*\(", "javascript": r"^javascript\s*\(",
            "typescript": r"^typescript\s*\(", "cpp": r"^c\+\+\s*\(",
            "c": r"^c\s*\(", "java": r"^java\s*\(", "c#": r"^c#\s*\(",
            "go": r"^go\s*\(", "rust": r"^rust\s*\(", "ruby": r"^ruby\s*\(",
            "php": r"^php\s*\(", "kotlin": r"^kotlin\s*\(", "swift": r"^swift\s*\(",
            "bash": r"^bash\s*\(", "sql": r"^sql\s*\(", "lua": r"^lua\s*\(",
        }
        pattern = patterns.get(key)
        matches = [entry for entry in entries if isinstance(entry, dict)
                   and isinstance(entry.get("id"), int)
                   and isinstance(entry.get("name"), str)
                   and pattern and re.search(pattern, entry["name"], re.I)]
        if not matches:
            raise Judge0Error("No active Judge0 runtime found for '%s'." % language)

        def version_key(entry):
            found = re.search(r"\(([^)]*)\)", entry["name"])
            version = found.group(1) if found else ""
            return tuple(int(part) for part in re.findall(r"\d+", version))

        return max(matches, key=version_key)

    def judge(self, language, code, test_cases, limits=None):
        limits = limits or {}
        language_info = self._language_match(language, self._languages())
        results = []
        deadline = time.monotonic() + self.max_wait
        for case_number, case in enumerate(test_cases, 1):
            payload = {
                "source_code": code,
                "language_id": language_info["id"],
                "stdin": case["input"],
                "expected_output": case["expected"],
                "cpu_time_limit": limits.get("cpu_time_limit", 2),
                "wall_time_limit": limits.get("wall_time_limit", 5),
                "memory_limit": limits.get("memory_limit", 128000),
            }
            submission = self._request("/submissions?base64_encoded=false&wait=false", payload)
            token = submission.get("token") if isinstance(submission, dict) else None
            if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9-]{1,100}", token):
                raise Judge0Error("Judge0 did not return a valid submission token.")
            result = None
            while time.monotonic() < deadline:
                time.sleep(0.5)
                result = self._request("/submissions/%s?base64_encoded=false&fields=stdout,stderr,compile_output,message,status,time,memory" % quote(token, safe=""))
                status = result.get("status") if isinstance(result, dict) else None
                if isinstance(status, dict) and status.get("id") not in (1, 2):
                    break
            else:
                raise Judge0Error("Timed out waiting for Judge0 to finish the test cases.")
            status = result.get("status", {})
            results.append({
                "case": case_number,
                "verdict": status.get("description", "Unknown"),
                "statusId": status.get("id"),
                "stdout": _clip(result.get("stdout")),
                "stderr": _clip(result.get("stderr")),
                "compileOutput": _clip(result.get("compile_output")),
                "message": _clip(result.get("message")),
                "time": result.get("time"),
                "memory": result.get("memory"),
            })
            if status.get("id") != 3:
                # A compile/runtime failure or wrong answer applies to every test.
                if status.get("id") in (6, 13, 14):
                    for remaining in range(case_number + 1, len(test_cases) + 1):
                        results.append({"case": remaining, "verdict": "Not run", "statusId": None,
                                        "stdout": "", "stderr": "", "compileOutput": "",
                                        "message": "Stopped after an earlier failure.", "time": None, "memory": None})
                    break
        passed = sum(1 for result in results if result["statusId"] == 3)
        verdict = "Accepted" if passed == len(test_cases) else next(
            (result["verdict"] for result in results if result["statusId"] != 3), "Unknown"
        )
        return {"verdict": verdict, "passed": passed, "total": len(test_cases), "language": language_info["name"], "results": results}


def _clip(value, limit=2048):
    if not isinstance(value, str):
        return ""
    return value[:limit] + ("\n[truncated]" if len(value) > limit else "")
