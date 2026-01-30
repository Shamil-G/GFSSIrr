from flask import render_template, request, redirect, url_for, g, session, jsonify, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import  upload_files
from regions import regions
from model.functions import get_list_rayons, get_partners, add_protocol
from view.common_route import get_cached_rayons
import json
from datetime import datetime


@app.route('/meet_labor', methods=['GET', 'POST'])
@login_required
def view_meet_labor_pension():
    list_regions=[]
    message=''
    data={}
    list_partners=get_partners()
    
    if g.user.top_level==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions

    list_rayons = get_cached_rayons(g.user.rfbn_id) 

    log.info(f'MEET LABOR. LIST_PARTNERS: {list_partners}')
    if request.method == 'POST':
        data = dict(request.form)
    
        files = request.files
        
        rfbn_id = data.get('rfbn_id','')
        organization_name = data.get('organization_name','')
        bin = data.get('organization_name','')
        partners = request.form.getlist('partners')
        photos = files.getlist("path_photo")

        if len(partners)<1:
            message=f"Необходимо выбрать не менее чем одну организацию. "
        if len(organization_name)==0 and len(bin)==0:
            message=f'{message}Необходимо выбрать либо адрес проведения ИРР, либо организацию. '
        if len(photos) < 2: 
            message=f"{message}{'\n' if message else ''}Необходимо выбрать не менее 2 файлов."

        if len(message)>0:
            data["partners"] = partners
            data['date_irr']=datetime.strptime(data['date_irr'], "%Y-%m-%d").date()

            return render_template('meet_labor.html', regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners, data=data)
        else:

            list_path=upload_files(rfbn_id, photos)
            log.info(f'POST. MEET LABOR\n\tList_files_path: {list_path}')

            data['path_photo'] = json.dumps(list_path, ensure_ascii=False)
            data['partners'] = json.dumps(partners, ensure_ascii=False)
            data['employee'] = g.user.fio            
            
            log.info(f'POST. MEET LABOR\n\tphoto_path: {data['photo_path']}\n\tpartners: {data['partners']}')

            add_protocol(data)

    return render_template('meet_labor.html', regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners, data=data)

