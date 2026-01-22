from flask import render_template, request, redirect, url_for, g, session, jsonify, abort, send_file
from flask_login import login_required
from main_app import app, log
from util.functions import extract_payload, upload_files
from regions import regions
from model.functions import get_list_rayons


@app.route('/meet_labor', methods=['GET', 'POST'])
@login_required
def view_meet_labor_pension():
    # log.info(f"VIEW MEET LABOR. METHOD: {request.method}")
    list_regions=[]
    message=''
    data={}

    if request.method == 'POST':
        data = dict(request.form)
    
        files = request.files
        
        meet_date = data.get('meet_date','')
        region = data.get('region','')
        district = data.get('district','')
        participants_total = data.get('participants_total','')
        participants_women = data.get('participants_women','')
        speaker_fio = data.get('speaker_fio','')
        meeting_format = data.get('meeting_format','')
        partners = request.form.getlist('partners')
        business_category = data.get('business_category','')
        bin_org = data.get('bin','')
        name_organization = data.get('organization_name','')
        photos = files.getlist("photo_report")

        if len(photos) < 2: 
            data["partners"] = partners
            log.info(f'POST. MEET LABOR\n\tpartners: {partners}\n\tdata: {data}')
            message="Нужно загрузить минимум 2 файла"
            if g.user.top_control==0:
                list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
            else:
                list_regions=regions

            list_rayons=get_list_rayons(g.user.rfbn_id)
            return render_template('meet_labor.html', regions=list_regions, districts=list_rayons, top=g.user.top_control, message=message, data=data)
        else:
            log.info(f'POST. MEET LABOR\n\tdata: {data}')
            log.info(f'POST. MEET LABOR\n\tmeet_date: {meet_date}\n\tregion: {region}\n\tdistrict: {district}\n\tparticipants_total: {participants_total}')
            log.info(f'POST. MEET LABOR\n\tparticipants_women: {participants_women}\n\tspeaker-fio: {speaker_fio}\n\tmeeting_format: {meeting_format}')
            log.info(f'POST. MEET LABOR\n\partners: {partners}\n\tcategory_subject: {business_category}\n\tbin_organization: {bin_org}')
            log.info(f'POST. MEET LABOR\n\tname_organization: {name_organization}\n\tfiles: {photos}')

            list_path=upload_files(region, photos)
            log.info(f'POST. MEET LABOR\n\tList_files_path: {list_path}')

    # rows, columns = get_solidary_items(scenario)
    if g.user.top_control==0:
        list_regions = { g.user.rfbn_id: regions[g.user.rfbn_id] }
    else:
        list_regions=regions

    list_rayons=get_list_rayons(g.user.rfbn_id)

    # log.info(f"------->\n\tVIEW MEET POPULATION\n\tRFBN_ID: {g.user.rfbn_id}\n\tTOP_CONTROL: {g.user.top_control}\n<-------")
    return render_template('meet_labor.html', regions=list_regions, districts=list_rayons, top=g.user.top_control, message=message, data=data)
