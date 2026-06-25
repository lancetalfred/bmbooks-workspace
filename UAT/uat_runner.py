import json
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

TESTS_FILE   = os.path.join(os.path.dirname(__file__), "uat_tests.json")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "uat_results.json")
BUGS_FILE    = os.path.join(os.path.dirname(__file__), "uat_bugs.json")
PREREQS_FILE = os.path.join(os.path.dirname(__file__), "uat_prereqs.json")


def load_tests():
    with open(TESTS_FILE) as f:
        return json.load(f)


def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return {}


def save_results(results):
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


def load_bugs():
    if os.path.exists(BUGS_FILE):
        with open(BUGS_FILE) as f:
            return json.load(f)
    return []


def save_bugs(bugs):
    with open(BUGS_FILE, "w") as f:
        json.dump(bugs, f, indent=2)


def load_prereqs():
    if os.path.exists(PREREQS_FILE):
        with open(PREREQS_FILE) as f:
            return json.load(f)
    return {}


def save_prereqs(prereqs):
    with open(PREREQS_FILE, "w") as f:
        json.dump(prereqs, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/prerequisites")
def get_prerequisites():
    data    = load_tests()
    statuses = load_prereqs()
    prereqs = data.get("prerequisites", [])
    for p in prereqs:
        p["done"] = statuses.get(p["id"], False)
    total = len(prereqs)
    done  = sum(1 for p in prereqs if p["done"])
    return jsonify({"prerequisites": prereqs, "total": total, "done": done})


@app.route("/api/prerequisites/<prereq_id>", methods=["POST"])
def update_prerequisite(prereq_id):
    body    = request.get_json()
    statuses = load_prereqs()
    statuses[prereq_id] = body.get("done", False)
    save_prereqs(statuses)
    return jsonify({"ok": True})


@app.route("/api/tests")
def get_tests():
    data    = load_tests()
    results = load_results()
    bugs    = load_bugs()
    bug_map = {}
    for bug in bugs:
        bug_map.setdefault(bug["test_id"], []).append(bug)

    total = passed = failed = skipped = 0
    for section in data["sections"]:
        for test in section["tests"]:
            tid    = test["id"]
            result = results.get(tid, {})
            test["status"] = result.get("status", "pending")
            test["notes"]  = result.get("notes", "")
            test["bugs"]   = bug_map.get(tid, [])
            total += 1
            if test["status"] == "pass":   passed  += 1
            if test["status"] == "fail":   failed  += 1
            if test["status"] == "skip":   skipped += 1

    return jsonify({
        "sections": data["sections"],
        "stats": {
            "total":   total,
            "passed":  passed,
            "failed":  failed,
            "skipped": skipped,
            "pending": total - passed - failed - skipped,
        }
    })


@app.route("/api/results/<test_id>", methods=["POST"])
def update_result(test_id):
    body    = request.get_json()
    results = load_results()
    results[test_id] = {
        "status":    body.get("status"),
        "notes":     body.get("notes", ""),
        "timestamp": datetime.now().isoformat(),
    }
    save_results(results)
    return jsonify({"ok": True})


@app.route("/api/bugs", methods=["GET"])
def get_bugs():
    return jsonify(load_bugs())


@app.route("/api/bugs", methods=["POST"])
def log_bug():
    body = request.get_json()
    bugs = load_bugs()
    bug  = {
        "id":          f"BUG-{len(bugs) + 1:03d}",
        "test_id":     body.get("test_id"),
        "test_title":  body.get("test_title"),
        "title":       body.get("title"),
        "description": body.get("description"),
        "severity":    body.get("severity", "medium"),
        "status":      "open",
        "logged_at":   datetime.now().isoformat(),
    }
    bugs.append(bug)
    save_bugs(bugs)
    return jsonify(bug)


@app.route("/api/bugs/<bug_id>", methods=["PATCH"])
def update_bug(bug_id):
    body = request.get_json()
    bugs = load_bugs()
    for bug in bugs:
        if bug["id"] == bug_id:
            bug.update({k: v for k, v in body.items() if k in ("status", "title", "description", "severity")})
            break
    save_bugs(bugs)
    return jsonify({"ok": True})


@app.route("/api/reset", methods=["POST"])
def reset_results():
    save_results({})
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("\n  BookKeeper for Shopify — UAT Runner")
    print("  http://localhost:5001\n")
    app.run(port=5001, debug=True)
