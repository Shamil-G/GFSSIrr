import * as meet from '/static/js/functions/meet.js'
import { setTheme } from '/static/js/functions/setTheme.js'

function init_meet_labor(targetZone){
    meet.bindRegionDistrict(targetZone);
    meet.bindPhotoReport(targetZone);
    meet.bindBinOrganization(targetZone);
    setTheme();
}

document.addEventListener('DOMContentLoaded', () => {
    const zone = document.getElementById('form_meet_labor');
    init_meet_labor(zone);
});