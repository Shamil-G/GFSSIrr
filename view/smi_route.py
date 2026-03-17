from flask_login import login_required
from flask import render_template, session, request, g, url_for, redirect
from main_app import app, log
from reports.report_smi_01 import report_01
from util.functions import extract_payload
from regions import regions
from model.smi_functions import get_rows, add, upd, set_action
from datetime import datetime


# Показываем Табы
@app.route('/print_smi')
@login_required
def view_print_smi():
    return render_template('print_smi.html')


## Выбираем сам протокол
@app.route('/print-smi/report', methods=['GET','POST'])
@login_required
def print_smi_report():
    if 'period' in session:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return '' ## 


@app.route('/print-smi/action', methods=['GET'])
@login_required
def view_print_smi_action():
    data = extract_payload()

    if data['action']=='edit':
        return redirect(url_for('view_form_print_smi', **data))

    args = {'action': data['action'], 'prot_num': data['prot_num'], 'top_level': g.user.top_level}
    set_action('PRINT_SMI ACTION', 'begin smi.set_action(:action, :prot_num, :top_level); end;', args);

    log.info(f'--->\n\tPRINT SMI ACTION. \n\tARGS: {args}\n\t<---')
    return redirect(url_for('view_print_smi_protocol'))


@app.route('/print_smi/form', methods=['GET', 'POST'])
@login_required
def view_form_print_smi():
    message = ''
    data={}
    if request.method == 'POST':
        data = dict(request.form)
        data['employee'] = g.user.fio            
        log.info(f'POST. FORM PRINT_SMI\n\tdata_post: {data}')
        if 'prot_num' in data:
            upd(data)
            return redirect(url_for('view_protocol_print_smi'))
        else:
            add(data)
        message=f"Информация успешно сохранена!"
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'VIEW FORM  PRINT SMI. data: {data}')

    if g.user.top_view==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions
    
    if 'event_date' in data and data['event_date']:
        try:
            data['event_date'] = datetime.strptime(data['event_date'], "%Y-%m-%d").date()
        except:
            data['event_date'] = None
    return render_template("print_smi.html", active_tab="form", regions=list_regions, top=g.user.top_level, message=message, data=data)


@app.route('/print_smi/protocol', methods=['GET','POST'])
@login_required
def view_print_smi_protocol():
    rows=[]
    period=''
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'PRINT_SMI PROTOCOL. GET. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if request.method == 'POST':
        data = extract_payload()
        log.info(f'PRINT_SMI PROTOCOL. POST. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if 'period' in session:
        period = session.get('period','') 

    log.info(f'PRINT_SMI PROTOCOL 2. period: {period}')

    if period:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'top_view': g.user.top_view, 'period': period} 
        rows = get_rows(params)

    log.info(f'PRINT_SMI/PROTOCOL. period: {period}')
    return render_template("print_smi.html", active_tab="protocol", list_protocols=rows, level=g.user.top_level, period=period)


