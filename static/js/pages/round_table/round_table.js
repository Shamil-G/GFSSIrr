import { SaveChangeFormBinder } from '/static/js/pages/round_table/binders/saveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/round_table/binders/setActionBinder.js';

document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
});