from flask import render_template, request, session, redirect, url_for, g, jsonify, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import upload_files, extract_payload
from regions import regions
from model.irr_functions import get_list_rayons, get_partners, add_protocol, update_protocol, list_protocol, set_action, get_org_name
from view.common_route import get_cached_rayons, category_to_english
import json
from datetime import datetime
from reports.report_meet_01 import report_01


@app.route('/meeting', methods=['GET'])
@login_required
def view_meeting():
    #list_rayons = get_cached_rayons(g.user.rfbn_id) 
    return render_template('meet.html')


@app.route('/meet/action', methods=['GET','POST'])
@login_required
def view_protocol_action():
    data = extract_payload()
    
    if data['action']=='edit' and 'page' in data and data['page']=='labor':
        log.debug(f'--->\nMEET ACTION. LABOR. data: {data}\n<---')
        # URL_FOR принимает только распаковнные параметры
        # Поэтому распаковка идет через **data 
        return redirect(url_for('view_form_meet_labor', **data))
    if data['action']=='edit' and 'page' in data and data['page']=='population':
        log.debug(f'--->\nMEET ACTION. POPULATION. data: {data}\n<---')
        return redirect(url_for('view_form_meet_population', **data))

    args = {'action': data['action'], 'prot_num': data['prot_num'], 'top_level': g.user.top_level}
    set_action('VIEW ACTION', 'begin manage.set_action(:action, :prot_num, :top_level); end;', args);

    return redirect(url_for('view_protocol_meet'))


@app.route('/meet/report', methods=['GET'])
@login_required
def meet_report():
    if 'period' in session:
        params = {'rfbn_id': g.user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return ''


@app.route('/meet_labor/form', methods=['GET', 'POST'])
@login_required
def view_form_meet_labor():
    list_regions=[]
    message=''
    data={}
    list_partners=get_partners()
    log.debug(f'-->\nMEET LABOR. LIST_PARTNERS: {list_partners}\n<---')
    
    if g.user.top_view==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions

    log.info(f'--->\nMEET LABOR FORM\n\ttop_view: {g.user.top_view}\n\tLIST_regions:\n{list_regions}\n<---')

    list_rayons = get_cached_rayons(g.user.rfbn_id) 
    log.info(f'--->\nMEET LABOR. LIST_RAYONS: {list_rayons}\n<---')

    if request.method == 'POST':
        data = dict(request.form)
    
        files = request.files
        
        rfbn_id = data.get('rfbn_id','')
        organization_name = data.get('organization_name','')
        bin = data.get('organization_name','')
        partners = request.form.getlist('partners')

        photos = files.getlist("path_photo")
        real_new_photos = [p for p in photos if p.filename]

        # old_photos = json.loads(request.form.get("old_photos", "[]"))
        # data.pop('old_photos')

        log.info(f"-->POST. MEET LABOR\n\tNEW_PHOTOS: {photos}\n\tREAL_NEW_PHOTOS:{photos}\n\tFILES: {files}\n<---")

        log.info(f"-->POST. MEET LABOR\n\tPARTNERS: {partners}\n<---")

        if len(partners)<1:
            message=f"Необходимо выбрать не менее чем одну организацию-партнера. "
        if len(organization_name)==0 and len(bin)==0:
            message=f'{message}Необходимо выбрать БИН организации. '
        # ЕСЛИ НОВЫЙ ДОКУМЕНТ, НЕ ИМЕЕТ НОМЕРА, ТО
        if  'prot_num' not in data and not real_new_photos: 
            message=f"{message}{'\n' if message else ''}Необходимо выбрать не менее 1 файла."

        if len(message)>0:
            data["partners"] = partners
            data['date_irr']=datetime.strptime(data['date_irr'], "%Y-%m-%d").date()

            log.info(f'POST. MEET LABOR. \n\tERROR: {message}')

            return render_template('meet.html', active_tab="form_labor", data=data, regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners)
        else:
            # если есть новые файлы - сохраним путь к ним в data['path_photo']
            # иначе используем старый список
            # 2. Если есть реальные новые файлы — сохраняем 
            if real_new_photos: 
                new_paths = upload_files(rfbn_id, real_new_photos) 
                data['path_photo'] = json.dumps(new_paths, ensure_ascii=False)
            else:
                data['path_photo']=''

            data['partners'] = json.dumps(partners, ensure_ascii=False)
            data['employee'] = g.user.fio            
            
            log.info(f'--->\nPOST. MEET LABOR\n\tPHOTO_PATH: {data['path_photo']}\n\tPARTNERS: {data['partners']}\n<---')
            if 'prot_num' in data:
                update_protocol(data)
                data.pop('prot_num')
                message=f"Протокол встречи с населением успешно обновлен!"

            else:
                add_protocol(data)
                message=f"Протокол встречи с населением успешно добавлен!"

            data['bin']=''
            data['date_irr']=''

            message=f"Протокол встречи с коллективом успешно сохранен!"

    if request.method == 'GET':
        data = dict(request.args)

        # Преобразуем дату из строки в date
        if 'date_irr' in data and data['date_irr']:
            try:
                data['date_irr'] = datetime.strptime(data['date_irr'], "%Y-%m-%d").date()
            except:
                data['date_irr'] = None
        # если есть page то это запрос на корректировку
        if  'page' in data:
            data['category'] = category_to_english(data['category'])
            data['organization_name'] = get_org_name({'bin': data['bin']}).get('name', '')

            if 'partners' in data and data['partners']:
                try:
                    data['partners'] = json.loads(data['partners'])
                except Exception as e:
                    print("Error parsing partners:", e)
                    data['partners'] = []
            log.debug(f'-->\n1. VIEW FORM LABOR GET\ndata: {data}<---')
            if 'path_photo' in data and data['path_photo']:
                try:
                    data['path_photo'] = json.loads(data['path_photo'])
                except Exception as e:
                    log.info(f"!!! Error parsing path_photo: {e}")
                    data['path_photo'] = []

            log.debug(f'-->\n2. VIEW FORM LABOR GET\ndata: {data}<---')
    
    log.debug(f'-->\nVIEW FORM LABOR. data: {data}\nlist_regions: {list_regions}\n<---')
    return render_template('meet.html', active_tab="form_labor", data=data, regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners)


@app.route('/meet_population/form', methods=['GET', 'POST'])
@login_required
def view_form_meet_population():
    list_regions=[]
    message=''
    data={}
    list_partners=get_partners()
    if g.user.top_view==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions

    list_rayons = get_cached_rayons(g.user.rfbn_id)
    log.debug(f'MEET POPULATION. LIST_RAYONS: {list_rayons}')

    if request.method == 'POST':
        data = dict(request.form)
        files = request.files
        
        rfbn_id = data.get('rfbn_id','')
        partners = request.form.getlist('partners')
        photos = files.getlist("path_photo")
        real_new_photos = [p for p in photos if p.filename]


        log.info(f"-->\n\tPOST. MEET POPULATION. PARTNERS: {partners}\n\tPHOTOS: {real_new_photos}\n\tFILES: {files}\n<---")
        if len(partners)<1:
            message="Необходимо выбрать не менее чем одну организацию"
        # ЕСЛИ НОВЫЙ ДОКУМЕНТ, НЕ ИМЕЕТ НОМЕРА, ТО
        if  'prot_num' not in data and not real_new_photos: 
            message=f"{message}{'\n' if message else ''}Необходимо выбрать не менее 1 файла !"

        if len(message)>0:
            data["partners"] = partners
            data['date_irr']=datetime.strptime(data['date_irr'], "%Y-%m-%d").date()

            log.info(f'POST. MEET POPULATION. \n\tERROR: {message}')

            return render_template('meet.html', data=data, active_tab="form_population", regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners)
        else:
            if real_new_photos: 
                new_paths = upload_files(rfbn_id, real_new_photos) 
                data['path_photo'] = json.dumps(new_paths, ensure_ascii=False)
            else:
                data['path_photo']=''

            data['partners'] = json.dumps(partners, ensure_ascii=False)
            data['employee'] = g.user.fio            

            log.info(f'POST. MEET POPULATION\n\tphoto_path: {data['path_photo']}\n\tdata.partners: {data['partners']}\n\tpartners: {partners}')
            if 'prot_num' in data:
                update_protocol(data)
                data.pop('prot_num')
                message=f"Протокол встречи с населением успешно обновлен!"
            else:
                add_protocol(data)
                message=f"Протокол встречи с населением успешно добавлен!"

            data['meeting_place']=''
            data['date_irr']=''


    if request.method == 'GET':
        data=dict(request.args)

        # Преобразуем дату из строки в date
        if 'date_irr' in data and data['date_irr']:
            try:
                data['date_irr'] = datetime.strptime(data['date_irr'], "%Y-%m-%d").date()
            except:
                data['date_irr'] = None
        # если есть page то это запрос на корректировку
        if  'page' in data:
            if 'partners' in data and data['partners']:
                try:
                    data['partners'] = json.loads(data['partners'])
                except Exception as e:
                    print("Error parsing partners:", e)
                    data['partners'] = []
            log.debug(f'-->\n1. VIEW FORM LABOR GET\ndata: {data}<---')
            if 'path_photo' in data and data['path_photo']:
                try:
                    data['path_photo'] = json.loads(data['path_photo'])
                except Exception as e:
                    log.info(f"!!! Error parsing path_photo: {e}")
                    data['path_photo'] = []

            log.debug(f'-->\n2. VIEW FORM LABOR GET\ndata: {data}<---')
    
    log.info(f'-->\nVIEW FORM POPULATION. data: {data}\n<---')
    return render_template('meet.html', active_tab="form_population", data=data, regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners)


@app.route('/meet/protocol', methods=['GET','POST'])
@login_required
def view_meet_protocol():
    rows=[]
    period=''
    if request.method == 'GET':
        data=dict(request.args)
        log.info(f'MEET PROTOCOL. GET. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if request.method == 'POST':
        data = extract_payload()
        log.info(f'MEET PROTOCOL. POST. data: {data}')
        if 'period' in data:
            session['period'] = data['period']

    if 'period' in session:
        period = session.get('period','') 

    params = {'rfbn_id': g.user.rfbn_id[0:2], 'top_view': g.user.top_view, 'period': period} 
    rows = list_protocol(params)

    if len(rows)==0:
        render_template('meet.html', data=rows, level=g.user.top_level)

    if g.user.top_view==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions

    SIZE_MAP = { 'large': 'большой', 'medium': 'средний', 'small': 'малый' }

    log.info(f'MEET PROTOCOL. {len(rows)} : period: {period}, data: {data}')
    for p in rows:
        p['category'] = SIZE_MAP.get(p.get('category'), p.get('category') or '')

        if isinstance(p.get('partners'), str):
            p['partners'] = json.loads(p['partners'])
        else:
            p['partners'] = p.get('partners') or []

        if isinstance(p.get('path_photo'), str):
            p['path_photo'] = json.loads(p['path_photo'])
        else:
            p['path_photo'] = p.get('path_photo') or []

    return render_template('meet.html', active_tab="protocol", rows=rows, level=g.user.top_level, regions=list_regions, period=period)


