odoo.define('services.update_kanban', function (require) {
'use strict';

var KanbanRecord = require('web.KanbanRecord');

KanbanRecord.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _openRecord: function () {
        if (this.modelName === 'services.services' && this.$(".o_services_kanban_boxes a").length) {
            this.$('.o_services_kanban_boxes a').first().click();
        } else {
            this._super.apply(this, arguments);
        }
    },

});
});
