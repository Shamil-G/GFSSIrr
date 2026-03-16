import { SaveChangeFormBinder } from '/static/js/pages/meet/binders/SaveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/meet/binders/SetActionBinder.js';
import { setTheme } from '/static/js/functions/setTheme.js';


document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
    setTheme();
    console.log('PROTOCOL JS started');
});