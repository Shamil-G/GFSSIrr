from flask import g
from flask_login import login_required
from util.functions import extract_payload
from model.functions import get_org_name
from main_app import app, log
from model.functions import get_list_rayons
from functools import lru_cache


@app.route('/api/organization/', methods=['POST'])
@login_required
def view_organization_name():
    data=extract_payload()
    log.info(f"API_ORGANIZATION: {data}")
    bin = data['bin']
    return get_org_name(bin)


@lru_cache(maxsize=32)
def get_cached_rayons(rfbn_id: str):
    log.info(f"--->\nGET CACHED RAYONS for {rfbn_id}\n<---")
    rayons = get_list_rayons(rfbn_id) or {}
    return {str(k): str(v) for k, v in rayons.items()}
