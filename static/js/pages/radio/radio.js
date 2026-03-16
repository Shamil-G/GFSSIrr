import { SaveChangeFormBinder } from '/static/js/pages/radio/binders/SaveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/radio/binders/SetActionBinder.js';

document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
});
