from flask import Flask, render_template, request, jsonify
from num2words import num2words
from text2digits import text2digits
import json
import sqlite3
import base64
import re

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'result': None, 'error': 'Missing required fields'}), 400

@app.route('/county_data', methods=['POST'])
def convert():
    try:
        if "coffee=teapot" in request.form:
            return ('I\'m a teapot', 418)
            
        data = request.get_json()
        if "zip" not in data and "measure_name" not in data:
            return jsonify({'result': None, 'error': 'Missing required fields'}), 400
        
        zip_code = data.get("zip", '')
        if len(zip_code) != 5:
            return jsonify({'result': None, 'error': 'Invalid zip code'}), 400
        zip_code = re.sub(r'[^0-9]', '', zip_code)
        measure_name = re.sub(r'[^a-zA-Z\s]', '', data.get("measure_name", '')).strip()

        if measure_name not in [
            "Violent crime rate",
            "Unemployment",
            "Children in poverty",
            "Diabetic screening",
            "Mammography screening",
            "Preventable hospital stays",
            "Uninsured",
            "Sexually transmitted infections",
            "Physical inactivity",
            "Adult obesity",
            "Premature Death",
            "Daily fine particulate matter"]:
            return jsonify({'result': None, 'error': 'Invalid measure name'}), 400,

        
        if not zip_code or not measure_name:
            return jsonify({'result': None, 'error': 'Missing required fields'}), 400

        conn = sqlite3.connect("./data.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Distinct counties for this ZIP (avoid duplicate joins)
        cur.execute(
            """
            WITH zip_cty AS (
            SELECT DISTINCT county, default_state
            FROM zip_county
            WHERE zip = ?
            )
            SELECT chr.*
            FROM county_health_rankings AS chr
            JOIN zip_cty z
            ON chr.County = z.county AND chr.State = z.default_state
            WHERE LOWER(chr.Measure_name) = LOWER(?)
            """,
            (zip_code, measure_name),
        )

        rows = [dict(r) for r in cur.fetchall()]
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({'result': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
