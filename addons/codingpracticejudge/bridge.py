"""Closed, versioned bridge protocol for CodingPractice cards."""

import json
import re

PREFIX = "codingpractice:"
VERSION = "0.2.0"
MAX_MESSAGE_BYTES = 128 * 1024
MAX_CODE_BYTES = 32 * 1024
MAX_CASES = 10
MAX_CASE_BYTES = 16 * 1024


def decode_message(message):
    if not isinstance(message, str) or len(message.encode("utf-8")) > MAX_MESSAGE_BYTES:
        return None
    if not message.startswith(PREFIX):
        return None
    try:
        request = json.loads(message[len(PREFIX):])
    except (ValueError, RecursionError):
        return None
    if not isinstance(request, dict):
        return None
    request_id = request.get("requestId")
    if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", request_id):
        return None
    if type(request.get("version")) is not int or request["version"] != 1:
        return None
    operation = request.get("operation")
    if operation == "ping" and set(request) == {"version", "operation", "requestId"}:
        return {"operation": "ping", "requestId": request_id}
    if operation != "judge" or set(request) != {
        "version", "operation", "requestId", "language", "code", "testCases"
    }:
        return None
    language = request["language"]
    code = request["code"]
    test_cases = request["testCases"]
    if not isinstance(language, str) or not 1 <= len(language.strip()) <= 40:
        return None
    if not isinstance(code, str) or not code.strip() or len(code.encode("utf-8")) > MAX_CODE_BYTES:
        return None
    if not isinstance(test_cases, list) or not 1 <= len(test_cases) <= MAX_CASES:
        return None
    cases = []
    for case in test_cases:
        if not isinstance(case, dict) or set(case) != {"input", "expected"}:
            return None
        case_input, expected = case["input"], case["expected"]
        if not isinstance(case_input, str) or not isinstance(expected, str):
            return None
        if len(case_input.encode("utf-8")) > MAX_CASE_BYTES or len(expected.encode("utf-8")) > MAX_CASE_BYTES:
            return None
        cases.append({"input": case_input, "expected": expected})
    return {
        "operation": "judge",
        "requestId": request_id,
        "language": language.strip(),
        "code": code,
        "testCases": cases,
    }


def handle_message(message):
    request = decode_message(message)
    if not request or request["operation"] != "ping":
        return None
    return {
        "version": 1,
        "requestId": request["requestId"],
        "status": "connected",
        "addonVersion": VERSION,
        "executionAvailable": True,
    }
