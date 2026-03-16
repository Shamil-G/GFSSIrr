from flask_login import login_required
from flask import render_template, session, request, g, url_for, redirect
from main_app import app, log
from reports.report_radio_01 import report_01
from util.functions import extract_payload
from regions import regions
from model.radio_functions import get_rows, add, set_action, upd
from datetime import datetime


@app.route('/radio', methods=['GET'])
@login_required
def view_radio():
    return render_template('radio.html')


@app.route('/radio/report', methods=['GET'])
@login_required
def radio_report():
    if 'period' in session:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return ''


@app.route('/radio/action', methods=['GET'])
@login_required
def view_radio_action():
    data = extract_payload()

    if data['action']=='edit':
        return redirect(url_for('view_form_radio', **data))

    args = {'action': data['action'], 'prot_num': data['prot_num'], 'top_level': g.user.top_level}
    set_action('RADIO ACTION', 'begin radio.set_action(:action, :prot_num, :top_level); end;', args);

    log.info(f'--->\n\tRADIO ACTION. \n\tARGS: {args}\n\t<---')
    return redirect(url_for('view_protocol_radio'))


@app.route('/radio/form', methods=['GET', 'POST'])
@login_required
def view_form_radio():
    message = ''
    data={}
    if request.method == 'POST':
        data = dict(request.form)
        data['employee'] = g.user.fio            
        log.info(f'POST. FORM RADIO\n\tdata_post: {data}')
        if 'prot_num' in data:
            upd(data)
            return redirect(url_for('view_protocol_radio'))
        else:
            add(data)
        message=f"Информация успешно сохранена!"
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'VIEW FORM  RADIO. data: {data}')

    if g.user.top_view==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions
    
    if 'event_date' in data and data['event_date']:
        try:
            data['event_date'] = datetime.strptime(data['event_date'], "%Y-%m-%d").date()
        except:
            data['event_date'] = None

    return render_template("radio.html", active_tab="form", regions=list_regions, top=g.user.top_level, message=message, data=data)
    # return render_template('fragments/radio/_fragment_form_radio.html', regions=list_regions, top=g.user.top_level, message=message, data=data)


@app.route('/radio/protocol', methods=['GET','POST'])
@login_required
def view_radio_protocol():
    rows=[]
    period=''
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'RADIO PROTOCOL. GET. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if request.method == 'POST':
        data = extract_payload()
        log.info(f'RADIO PROTOCOL. POST. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if 'period' in session:
        period = session.get('period','') 

    log.info(f'RADIO PROTOCOL 2. period: {period}')

    if period:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'top_view': g.user.top_view, 'period': period} 
        rows = get_rows(params)

    log.info(f'RADIO/PROTOCOL. period: {period}')
    return render_template("radio.html", active_tab="protocol", list_protocols=rows, level=g.user.top_level, period=period)
