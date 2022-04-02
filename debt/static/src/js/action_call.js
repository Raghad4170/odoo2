
odoo.define('debt.action_call', function (require) {
    "use strict";
    // alert("hi")
    // /**
    //  * Button 'Create' is replaced by Custom Button 
    // **/
    // var core = require('web.core');
    // var ListController = require('web.ListController');
    // ListController.include({
    //    renderButtons: function($node) {
    //        alert("ddd")
    //    this._super.apply(this, arguments);
    //        if (this.$buttons) {
    //            alert("lllllllllllllllll")
    //          this.$buttons.find('.o_list_tender_button_create').click(this.proxy('action_def'));
    //        }
    //     },
          
    //     //--------------------------------------------------------------------------
    //     // Define Handler for new Custom Button
    //     //--------------------------------------------------------------------------
    
    //     /**
    //      * @private
    //      * @param {MouseEvent} event
    //      */
    //     action_def: function (e) {
    //         var self = this;
    //         var active_id = this.model.get(this.handle).getContext()['active_ids'];
    //         var model_name = this.model.get(this.handle).getContext()['active_model'];
    //             this._rpc({
    //                     model: 'violations.violations',
    //                     method: 'violation_wizard',
    //                     args: [" "],
    //                 }).then(function (result) {
    //                     self.do_action(result);
    //                 });
    //    },
    // });



    var core = require('web.core');
    var time = require('web.time');

    var viewRegistry = require('web.view_registry');
    var ListView = require('web.ListView');
    var ListController = require('web.ListController');

    var _t = core._t;
    var QWeb = core.qweb;

    var IndexViolationButton = {
        /**
         * @override
         */
        renderButtons: function() {
            this._super.apply(this, arguments);
            // alert("kkkkkkkkkkkk")
            this.$buttons.append(this._renderIndexContractButton());
        },

        /*
            Private
        */
       _renderIndexContractButton: function() {
        // alert("jjkjkj")
        return $(QWeb.render('violation.index_button', {})).on('click', this._onIndexViolation.bind(this));

            // return $(QWeb.render('late_work_entry_button', {})).on('click', this._onIndexViolation.bind(this));
       },

        _indexViolation: function () {
            var self = this;
            var active_id = this.model.get(this.handle).getContext()['active_ids'];
            var model_name = this.model.get(this.handle).getContext()['active_model'];
            return this._rpc({
                        model: 'violations.violations',
                        method: 'violation_wizard',
                        args: [" "],
                    }).then(function (result) {
                        self.do_action(result);
                    });
            
        },

        _onIndexViolation: function (e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            this._indexViolation();
        },
    };

    var ViolationContractTreeController = ListController.extend(IndexViolationButton);

    var ViolationContractListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ViolationContractTreeController,
        }),
    });

    viewRegistry.add('action_call', ViolationContractListView);

    return ViolationContractListView;



    
    });