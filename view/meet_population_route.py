from flask import render_template, request, redirect, url_for, g, session, jsonify, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import upload_files
from regions import regions
from model.functions import get_list_rayons, get_partners, add_protocol
from view.common_route import get_cached_rayons
import json
from datetime import datetime


@app.route('/meet_population', methods=['GET', 'POST'])
@login_required
def view_meet_poulation_pension():
    list_regions=[]
    message=''
    data={}
    list_partners=get_partners()
    if g.user.top_level==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions

    list_rayons = get_cached_rayons(g.user.rfbn_id)

    if request.method == 'POST':
        data = dict(request.form)
        files = request.files
        
        rfbn_id = data.get('rfbn_id','')
        partners = request.form.getlist('partners')
        photos = files.getlist("path_photo")

        log.info(f"-->\n\tPOST. MEET POPULATION. PARTNERS: {partners}\n\tPHOTOS: {photos}\n\tFILES: {files}\n<---")
        if len(partners)<1:
            message="Необходимо выбрать не менее чем одну организацию"
        if len(photos) == 0: 
            message=f"{message}{'\n' if message else ''}\nНеобходимо выбрать не менее 1 файла"

        if len(message)>0:
            data["partners"] = partners
            data['date_irr']=datetime.strptime(data['date_irr'], "%Y-%m-%d").date()

            log.info(f'POST. MEET POPULATION. \n\tERROR: {message}')

            return render_template('meet_population.html', regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners, data=data)
        else:
            list_path=upload_files(rfbn_id, photos)

            data['path_photo'] = json.dumps(list_path, ensure_ascii=False)
            data['partners'] = json.dumps(partners, ensure_ascii=False)
            data['employee'] = g.user.fio            

            log.info(f'POST. MEET POPULATION\n\tphoto_path: {data['path_photo']}\n\tdata.partners: {data['partners']}\n\tpartners: {partners}')

            add_protocol(data)

    # log.info(f"------->\n\tVIEW MEET POPULATION\n\tRFBN_ID: {g.user.rfbn_id}\n\ttop_level: {g.user.top_level}\n<-------")
    return render_template('meet_population.html', regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners, data=data)
