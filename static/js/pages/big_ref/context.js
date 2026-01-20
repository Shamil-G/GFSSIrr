import { MenuBinder } from '/static/js/pages/big_ref/binders/menuBinder.js';
import { HelperBinder } from '/static/js/binders/standart/helperBinder.js';
import { EditRowTableBinder } from '/static/js/pages/big_ref/binders/editRowTableBinder.js';
import { FilterActiveCloseRefundBinder } from '/static/js/binders/filters/filterActiveCloseRefundBinder.js';


export const bigRefTabContext = {
    // Значения zone определяют id=""
    zones: {
        mainTableHelper: '#big_ref_mainTableHelper',
        fragment: '#big_ref_mainBody',
        filters: '#big_ref_FilterZone'
    },

    binders: {
        mainTableHelper: [HelperBinder],
        fragment: [EditRowTableBinder], //RowClickBinder, 
        filters: [FilterActiveCloseRefundBinder, MenuBinder],
    },

    request: {
        fragment: {
            method: 'POST',
            url: ref_name => `/filter-ref-name`
        },
        filters: {
            method: 'POST',
            url: '/big_ref_filters',
            params: () => ({}) // 👈 пустой объект, если нет orderNum
        },
        save_row_big_ref: {
            method: 'POST',
            url: (id, year, field) => `/save-ref-value`,
            params: (id, year, field, value) => ({ id, year, field, value })
        }
    },

    bindScope: {
        filters: 'global'    // искать в document, независимо от fragment
    },

    loadStrategy: {
        filters: 'eager'
    }
};

export default bigRefTabContext;