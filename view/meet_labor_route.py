from flask import render_template, request, redirect, url_for, g, session, jsonify, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload


@app.route('/meet_labor')
@login_required
def view_meet_labor_pension():
    log.info(f"VIEW MEET LABOR.")

    # rows, columns = get_solidary_items(scenario)
    return render_template('meet_labor.html')
