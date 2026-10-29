"""CodingPractice Judge 0.2: desktop bridge and hosted Judge0 integration."""

import json

from aqt import gui_hooks, mw
from aqt.operations import QueryOp
from aqt.qt import QMessageBox
from aqt.reviewer import Reviewer

from .bridge import VERSION, decode_message, handle_message
from .judge0 import Judge0Client, Judge0Error


def send_response(reviewer, card_id, response):
    if reviewer.state != "question" or not reviewer.card or reviewer.card.id != card_id:
        return
    payload = json.dumps(response, ensure_ascii=True)
    reviewer.web.eval(
        "document.dispatchEvent(new CustomEvent('codingpractice:response',"
        "{detail:" + payload + "}));"
    )


def run_judge(request, config):
    endpoint = config.get("judge0_endpoint", "https://ce.judge0.com").strip()
    api_key = config.get("judge0_api_key", "")
    limits = {
        "cpu_time_limit": config.get("cpu_time_limit", 2),
        "wall_time_limit": config.get("wall_time_limit", 5),
        "memory_limit": config.get("memory_limit", 128000),
    }
    try:
        result = Judge0Client(endpoint, api_key).judge( request["language"], request["code"], request["testCases"], limits)
        return {"version": 1, "requestId": request["requestId"], "status": "result", "result": result}
    except Judge0Error as error:
        return {"version": 1, "requestId": request["requestId"], "status": "error", "error": str(error)}
    except Exception:
        return {"version": 1, "requestId": request["requestId"], "status": "error", "error": "Unexpected add-on error while contacting Judge0."}


def on_message(handled, message, context):
    if handled[0] or not isinstance(context, Reviewer):
        return handled
    config = mw.addonManager.getConfig(__name__) or {}
    if not config.get("enabled", True):
        return handled
    card = context.card
    if not card or context.state != "question":
        return handled
    if card.note().note_type()["name"] != config.get("model_name", "CodingPractice"):
        return handled
    request = decode_message(message)
    if request is None:
        return handled
    card_id = card.id
    if request["operation"] == "ping":
        send_response(context, card_id, handle_message(message))
    else:
        snapshot = dict(config)
        endpoint = snapshot.get("judge0_endpoint", "https://ce.judge0.com").strip().rstrip("/")
        answer = QMessageBox.question(
            mw,
            "Send solution to Judge0?",
            "Your source code, test inputs, and expected outputs will be sent to:\n\n"
            + endpoint
            + "\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            send_response(context, card_id, { "version": 1, "requestId": request["requestId"], "status": "cancelled" })
            return (True, None)
        QueryOp(
            parent=mw,
            op=lambda _col: run_judge(request, snapshot),
            success=lambda response: send_response(context, card_id, response),
        ).without_collection().run_in_background()
    return (True, None)


gui_hooks.webview_did_receive_js_message.append(on_message)
