from flask_login import login_required
from flask import render_template, session, request, g, url_for, redirect
from main_app import app, log
from reports.report_round_table_01 import report_01
from util.functions import extract_payload
from regions import regions
from model.round_table_functions import get_rows, add, set_action, upd
from datetime import datetime


@app.route('/round_table')
@login_required
def view_round_table():
    return render_template('round_table.html')


@app.route('/round-table/report', methods=['GET'])
@login_required
def round_table_report():
    if 'period' in session:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return ''


@app.route('/round_table/action', methods=['GET'])
@login_required
def view_round_table_action():
    data = extract_payload()

    if data['action']=='edit':
        return redirect(url_for('view_form_round_table', **data))

    args = {'action': data['action'], 'prot_num': data['prot_num'], 'top_level': g.user.top_level}
    set_action('ROUND TABLE ACTION', 'begin round_table.set_action(:action, :prot_num, :top_level); end;', args);

    log.info(f'--->\n\tROUND TABLE ACTION. \n\tARGS: {args}\n\t<---')
    return redirect(url_for('view_round_table_protocol'))


@app.route('/round_table/form', methods=['GET', 'POST'])
@login_required
def view_form_round_table():
    message = ''
    data={}
    if request.method == 'POST':
        data = dict(request.form)
        data['employee'] = g.user.fio            
        log.info(f'POST. FORM ROUND TABLE\n\tdata_post: {data}')
        if 'prot_num' in data:
            upd(data)
            return redirect(url_for('view_protocol_round_table'))
        else:
            add(data)
        message=f"Информация успешно сохранена!"
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'VIEW FORM  ROUND TABLE. data: {data}')

    if g.user.top_view==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions
    
    if 'event_date' in data and data['event_date']:
        try:
            data['event_date'] = datetime.strptime(data['event_date'], "%Y-%m-%d").date()
        except:
            data['event_date'] = None
    return render_template("round_table.html", active_tab="form", regions=list_regions, top=g.user.top_level, message=message, data=data)
    # return render_template('fragments/radio/_fragment_form_radio.html', regions=list_regions, top=g.user.top_level, message=message, data=data)


@app.route('/round_table/protocol', methods=['GET','POST'])
@login_required
def view_round_table_protocol():
    rows=[]
    period=''
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'RADIO ROUND TABLE. GET. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if request.method == 'POST':
        data = extract_payload()
        log.info(f'RADIO ROUND TABLE. POST. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if 'period' in session:
        period = session.get('period','') 

    log.info(f'RADIO ROUND TABLE 2. period: {period}')

    if period:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'top_view': g.user.top_view, 'period': period} 
        rows = get_rows(params)

    log.info(f'ROUND TABLE PROTOCOL. period: {period}')
    return render_template("round_table.html", active_tab="protocol", list_protocols=rows, level=g.user.top_level, period=period)
