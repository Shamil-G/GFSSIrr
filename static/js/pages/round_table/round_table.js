import { SaveChangeFormBinder } from '/static/js/pages/round_table/binders/SaveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/round_table/binders/SetActionBinder.js';

document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
});