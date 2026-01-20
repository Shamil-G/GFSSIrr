from flask import render_template, request, redirect, url_for, g, session, jsonify, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload


@app.route('/meet_population')
@login_required
def view_meet_poulation_pension():
    # rows, columns = get_solidary_items(scenario)
    log.info(f"------->\n\tVIEW MEET LABOR\n<-------")
    return render_template('meet_population.html')
