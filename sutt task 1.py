from flask import Flask, jsonify, request, abort
import sys
import re
import json

app = Flask(__name__)


try:
    file_path = sys.argv[1]
except IndexError:
    print("Error: Please provide a path to the .txt file as a command-line argument.")
    sys.exit(1)


ids = []
unique_ids = set()
try:
    with open(file_path, 'r') as file:
        for line in file:
            id_str = line.strip()
            if id_str[-4:] not in unique_ids:  # Check for unique last 4 digits
                ids.append(id_str)
                unique_ids.add(id_str[-4:])
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
    sys.exit(1)


def parse_id(bits_id):
    """
    Parse a BITS ID and extract its components like year, branch, etc.
    """
    match = re.match(r"(\d{4})([A-Z]{2})([A-Z]{2})(\d{4})([A-Z])", bits_id)
    if not match:
        return None
    year, campus, branch, uid, letter = match.groups()
    branch_name = {
        "CS": "cs", "ECE": "ece", "EEE": "eee", "ENI": "eni", "MECH": "mech",
        "CIVIL": "civil", "PHY": "phy", "CHEM": "chem", "CHM": "chemical",
        "MATH": "math", "BIO": "bio", "ECO": "eco", "PHARMA": "pharma",
        "MANU": "manu", "GEN": "genstudies"
    }.get(branch.upper(), "unknown")
    return {
        "id": bits_id,
        "uid": uid,
        "email": f"{bits_id.lower()}@domain.com",
        "branch": branch_name,
        "year": 2024 - int(year),
        "campus": campus
    }


@app.route("/", methods=["GET"])
def get_all_ids():
    if request.args.get("format") == "text":
        return "\n".join(ids), 200, {'Content-Type': 'text/plain'}
    return jsonify({"ids": ids})


@app.route("/", methods=["GET"])
def filter_by_branch():
    branch = request.args.get("branch")
    if branch:
        filtered_ids = [id_ for id_ in ids if parse_id(id_)["branch"] == branch]
        if not filtered_ids:
            return jsonify({"error": "No data found"}), 404
        return jsonify({"ids": filtered_ids})


@app.route("/", methods=["GET"])
def filter_by_year():
    year = request.args.get("year")
    if year:
        filtered_ids = [id_ for id_ in ids if parse_id(id_)["year"] == int(year)]
        if not filtered_ids:
            return jsonify({"error": "No data found"}), 404
        return jsonify({"ids": filtered_ids})


@app.route("/<bits_id>", methods=["GET"])
def get_id_details(bits_id):
    details = parse_id(bits_id)
    if not details:
        return jsonify({"error": "ID not found"}), 404
    return jsonify(details)


if __name__ == "__main__":
    app.run(port=8000)
