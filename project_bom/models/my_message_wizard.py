class MyMessageWizard(models.TransientModel):
    _name= 'my.message.wizard'
 
    message= fields.Text('message', required=True)
 
    @api.multi
    def action_ok(self):
        return {'type':'ir.actions.act_window_close'}