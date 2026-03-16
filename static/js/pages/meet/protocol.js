import { SaveChangeFormBinder } from '/static/js/pages/meet/binders/saveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/meet/binders/setActionBinder.js';
import { setTheme } from '/static/js/functions/setTheme.js';


document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
    setTheme();
    console.log('PROTOCOL JS started');
});