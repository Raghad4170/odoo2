odoo.define('mutn_binary_file_preview.mutn_binary_preview', function(require) {


    var BasicFields = require('web.basic_fields');
//    var DocumentViewer = require('mail.DocumentViewer');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var mutn_file_data = undefined;
    var Viewer = require('mutn_binary_file_preview.Viewer');




    BasicFields.FieldBinaryFile.include({

        events: _.extend({}, BasicFields.FieldBinaryFile.prototype.events, {
            'click .mutn_binary_file_preview': "mutn_onAttachmentView",
        }),

        _renderReadonly: function() {
            var self = this;
            self._super.apply(this, arguments);
            if (!self.res_id) {
                self.$el.css('cursor', 'not-allowed');
            } else {
                self.$el.css('cursor', 'pointer');
                self.$el.attr('title', 'Download');
            }
            self.$el.append(core.qweb.render("mutn_preview_button"));
        },

        mutn_onAttachmentView: function(ev) {
            var self = this;
            try {
                ev.preventDefault();
                ev.stopPropagation();
                var mutn_mimetype = self.recordData.mimetype;

                function mutn_docView(mutn_file_data) {
                    if (mutn_file_data) {
                        var match = mutn_file_data.type.match("(image|video|application/pdf|text)");
                        if(match){
                            var mutn_attachment = [{
                                filename: mutn_file_data.name,
                                id: mutn_file_data.id,
                                is_main: false,
                                mimetype: mutn_file_data.type,
                                name: mutn_file_data.name,
                                type: mutn_file_data.type,
                                url: "/web/content/" + mutn_file_data.id + "?download=true",
                            }]
                            var mutn_activeAttachmentID = mutn_file_data.id;
                            var mutn_attachmentViewer = new Viewer(self,mutn_attachment,mutn_activeAttachmentID);
                            mutn_attachmentViewer.appendTo($('body'));
                        }
                        else{
                            alert('This file type can not be previewed.')
                        }
                    }
                }
                if (mutn_mimetype) {
                    mutn_file_data = {
                        'id': self.recordData.id,
                        'type': self.recordData.mimetype || 'application/octet-stream',
                        'name': self.recordData.name || self.recordData.display_name || "",
                    }
                    mutn_docView(mutn_file_data);
                } else {
                    var def = ajax.jsonRpc("/get/record/details", 'call', {
                        'res_id': self.res_id,
                        'model': self.model,
                        'size': self.value,
                        'res_field': self.name || self.field.string,
                    });
                    return $.when(def).then(function(vals) {
                        if (vals && vals.id) {
                            mutn_docView(vals);
                        } else {
                            alert('The preview of the file can not be generated as it does not exist in the Odoo file system (Attachments).')
                        }
                    });
                }
            } catch (err) {
                alert(err);
            }
        },
    });
});
