from flask import render_template, request, redirect, url_for, g, session, send_from_directory, jsonify
from flask_login import login_user, login_required
import requests
import time
from main_app import app, log
from util.i18n import get_i18n_value
from app_config import styles, sso_server
from sso.sso_login import SSO_User
from util.ip_addr import ip_addr
from util.functions import extract_payload
import json

# from view.routes_overpayments import *
from view.meet_labor_route import *
from view.meet_population_route import *
from view.common_route import *

from util.functions import extract_payload
from model.functions import list_protocol, set_action

log.info("Routes стартовал...")

@app.context_processor
def utility_processor():
    if 'style' not in session:
        session['style']=styles[0]    
        log.debug(f'------- CP\n\tSET SESSION STYLE: {session['style']}\n------')

    log.debug(f"CONTEXT PROCESSOR. APP_NAME {get_i18n_value('APP_NAME')}")
    return dict(res_value=get_i18n_value)


@app.route('/about')
def about():
    return render_template("about.html")


def try_auto_login():
    req_json = {'ip_addr': f'{ip_addr()}'}
    resp = requests.post(url=f'{sso_server}/check', json=req_json)
    log.debug(f'LOGIN CHECK. \n\taddr: {sso_server}/check\n\tresp: {resp}')
    if resp.status_code == 200:
        resp_json=resp.json()
        log.debug(f'LOGIN GET. resp_json: {resp_json}')
        if 'status' in resp_json and resp_json['status'] == 200:
            json_user = resp_json['user']
            log.info(f'LOGIN GET. json_user: {json_user}')
            session['username'] = json_user['login_name']
            user = SSO_User().get_user_by_name(json_user)
            if user:
                login_user(user)
        else:
            log.info(f'---> Try auto login\n\tUSER {ip_addr()} not Registred\n<---')
            return render_template('login.html')


@app.route('/')
def view_root():
    if not g or g.user.is_anonymous:
        # LOGIN with session variable
        log.info(f'User is anonymous ...')
        try_auto_login()
    return render_template("index.html")


@app.route('/change-style')
def change_style():
    if 'style' in session:
        for style in styles:
            if style!=session['style']:
                session['style']=style
                break
    else: 
        session['style']=styles[0]
    # Получим предыдущую страницу, чтобы на неё вернуться
    current_page = request.referrer
    log.debug(f"Set style {session['style']}. Next page: {current_page}")
    if current_page is not None:
        return redirect(current_page)
    else:
        return redirect(url_for('view_root'))


@app.route('/language/<string:lang>')
def set_language(lang):
    log.debug(f"Set language. LANG: {lang}, предыдущий язык: {session['language']}")
    session['language'] = lang
    # Получим предыдущую страницу, чтобы на неё вернуться
    current_page = request.referrer
    log.debug(f"Set LANGUAGE. {current_page}")
    if current_page is not None:
        return redirect(current_page)
    else:
        return redirect(url_for('view_root'))


@app.route('/uploads/<path:filename>')
def uploaded_files(filename):
    return send_from_directory('uploads', filename)


@app.route('/list-protocols')
@login_required
def view_list_protocols():

    status, protocols, err = list_protocol(g.user.rfbn_id, g.user.boss)
    if status!='success':
        return render_template('list_protocols.html', list_protocol=[], error=err)

    SIZE_MAP = { 'large': 'большой', 'medium': 'средний', 'small': 'малый' }

    log.debug(f'list-protocols. {len(protocols)} : {protocols}')
    for p in protocols:
        for key, value in p.items(): 
            if value is None: p[key] = ''
        
        p['category'] = SIZE_MAP.get(p.get('category'), p.get('category') or '')

        if isinstance(p.get('partners'), str):
            p['partners'] = json.loads(p['partners'])
        else:
            p['partners'] = p.get('partners') or []

        if isinstance(p.get('path_photo'), str):
            p['path_photo'] = json.loads(p['path_photo'])
        else:
            p['path_photo'] = p.get('path_photo') or []


    return render_template('list_protocols.html', list_protocols=protocols, rfbn='14', boss='Y')
    # return render_template('list_protocols.html', list_protocols=protocols, rfbn=g.user.rfbn_id, boss=g.user.boss)


@app.route('/protocol/action', methods=['POST'])
@login_required
def view_action_protocols():
    data = extract_payload()

    args = {'action': data['action'], 'prot_num': data['prot_num'], 'boss': g.user.boss}
    log.info(f'--->\n\tPROTOCOL ACTION. \n\tARGS: {args}\n\t<---')
    set_action('VIEW ACTION', 'begin manage.set_action(:action, :prot_num, :boss); end;', args);
    return {'status': 'success'}, 200


@app.route('/get_protocol_excel', methods=['GET'])
@login_required
def view_get_protocol_excel():
    data = extract_payload()
    log.info(f'--->\n\tPROTOCOL ACTION. \n\tARGS: {data}\n\t<---')

