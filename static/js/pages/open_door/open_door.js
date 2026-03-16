import { SaveChangeFormBinder } from '/static/js/pages/open_door/binders/SaveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/open_door/binders/SetActionBinder.js';

document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
});