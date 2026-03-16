from flask import g, request, render_template, redirect, url_for
from flask_login import login_required
from util.functions import upload_files, extract_payload
from main_app import app, log
from functools import lru_cache
from regions import regions
import json
from datetime import datetime
from model.irr_functions import get_org_name, get_list_rayons, load_protocol, get_partners, update_protocol


@app.route('/api/organization/', methods=['POST'])
@login_required
def view_organization_name():
    data=extract_payload()
    log.info(f"API_ORGANIZATION: {data}")
    # bin = data['bin']
    return get_org_name(data)


@lru_cache(maxsize=32)
def get_cached_rayons(rfbn_id: str):
    log.info(f"--->\nGET CACHED RAYONS for {rfbn_id}\n<---")
    rayons = get_list_rayons(rfbn_id) or []
    return {item['rfbn_id']: item['name'] for item in rayons}


def category_to_english(nm: str)->str:
    match nm:
        case 'большой': return 'large' 
        case 'средний': return 'middle' 
        case 'малый': return 'small' 
        case _: return nm


@app.route('/edit-protocol/<prot_num>', methods=['GET', 'POST']) 
@login_required
def protocol_form(prot_num): 
    list_regions=[]
    message=''
    load_data={}
    list_partners=get_partners()

    # rows, columns = get_solidary_items(scenario)
    if g.user.top_level==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions

    list_rayons = get_cached_rayons(g.user.rfbn_id) 

    if request.method=='GET':
        load_data = load_protocol(prot_num) # твоя функция 
    
    if request.method=='POST':
        load_data = dict(request.form)
        
        files = request.files
        
        rfbn_id = load_data.get('rfbn_id','')
        meeting_place = load_data.get('meeting_place','')
        bin = load_data.get('bin','')
        partners = request.form.getlist('partners')
        photos = files.getlist("path_photo")

        if len(partners)<1:
            message=f"Необходимо выбрать не менее чем одну организацию. "
        if len(meeting_place)==0 and len(bin)==0:
            message=f'{message}Необходимо выбрать либо адрес проведения ИРР, либо организацию. '
        if not any(p.filename for p in photos): 
            message=f"{message}{'\n' if message else ''}Необходимо выбрать не менее 1 файла."

        if len(message)>0:
            load_data["partners"] = partners
            load_data['date_irr']=datetime.strptime(load_data['date_irr'], "%Y-%m-%d").date()

            return render_template('edit_protocol.html', data=load_data, regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners)

        else:
            log.info(f'EDIT PROTOCOL. POST. \n\tload_data: {load_data}\n\t{request}\n\tREQUEST FORM: {request.form}')

            list_path=upload_files(rfbn_id, photos)

            load_data['path_photo'] = json.dumps(list_path, ensure_ascii=False)
            load_data['partners'] = json.dumps(partners, ensure_ascii=False)
            load_data['employee'] = g.user.fio    
            load_data['prot_num'] = prot_num

            log.info(f'EDIT PROTOCOL. POST. \n\tList_files_path: {list_path}')

            update_protocol(load_data)
        
        return redirect(url_for('view_list_protocols'))

    log.info(f'--->\n\tEDIT PROTOCOL:\n\tMETHOD: {request.method}\n\tPROT_NUM: {prot_num}\n\tDATA: {load_data}\n<---')
    
    return render_template('edit_protocol.html',  data=load_data, regions=list_regions, districts=list_rayons, top=g.user.top_level, message=message, list_partners=list_partners)