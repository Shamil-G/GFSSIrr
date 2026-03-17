from flask_login import login_required
from flask import render_template, session, request, g, url_for, redirect
from main_app import app, log
from reports.report_open_door_01 import report_01
from util.functions import extract_payload
from regions import regions
from model.open_door_functions import get_rows, add, upd, set_action
from datetime import datetime


@app.route('/open_door', methods=['GET', 'POST'])
@login_required
def view_open_door():
    return render_template('open_door.html')


@app.route('/open-door/report', methods=['GET'])
@login_required
def open_door_report():
    if 'period' in session:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return ''


@app.route('/open_door/action', methods=['GET'])
@login_required
def view_open_door_action():
    data = extract_payload()

    if data['action']=='edit':
        return redirect(url_for('view_form_open_door', **data))

    args = {'action': data['action'], 'prot_num': data['prot_num'], 'top_level': g.user.top_level}
    set_action('OPEN DOOR ACTION', 'begin open_door.set_action(:action, :prot_num, :top_level); end;', args);

    log.info(f'--->\n\tOPEN DOOR ACTION. \n\tARGS: {args}\n\t<---')
    return redirect(url_for('view_open_door_protocol'))


@app.route('/open_door/form', methods=['GET', 'POST'])
@login_required
def view_form_open_door():
    message = ''
    data={}
    if request.method == 'POST':
        data = dict(request.form)
        data['employee'] = g.user.fio            
        log.info(f'POST. VIEW FORM OPEN DOOR\n\tdata_post: {data}')
        if 'prot_num' in data:
            upd(data)
            return redirect(url_for('view_protocol_open_door'))
        else:
            add(data)
        message=f"Информация успешно сохранена!"
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'GET. VIEW FORM OPEN DOOR\n\tdata: {data}')

    if g.user.top_view==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions
    
    if 'event_date' in data and data['event_date']:
        try:
            data['event_date'] = datetime.strptime(data['event_date'], "%Y-%m-%d").date()
        except:
            data['event_date'] = None
    return render_template("open_door.html", active_tab="form", regions=list_regions, top=g.user.top_level, message=message, data=data)
    # return render_template('fragments/radio/_fragment_form_radio.html', regions=list_regions, top=g.user.top_level, message=message, data=data)


@app.route('/open_door/protocol', methods=['GET','POST'])
@login_required
def view_open_door_protocol():
    rows=[]
    period=''
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'OPEN_DOOR PROTOCOL. GET. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if request.method == 'POST':
        data = extract_payload()
        log.info(f'OPEN_DOOR PROTOCOL. POST. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if 'period' in session:
        period = session.get('period','') 

    log.info(f'OPEN_DOOR. period: {period}')

    if period:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'top_view': g.user.top_view, 'period': period} 
        rows = get_rows(params)

    log.info(f'RADIO/PROTOCOL. period: {period}: rows: {rows}')
    return render_template("open_door.html", active_tab="protocol", list_protocols=rows, level=g.user.top_level, period=period)
