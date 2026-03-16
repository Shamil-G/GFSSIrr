import { SaveChangeFormBinder } from '/static/js/pages/print_smi/binders/SaveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/print_smi/binders/SetActionBinder.js';

document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
});