# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime

from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _


class employee_requision(osv.Model):
    _name= 'employee.requision'
    _description = 'Employee Requision'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _track = {
        'state': {
            'hr_holidays.mt_holidays_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'validate',
            'hr_holidays.mt_holidays_refused': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'refuse',
            'hr_holidays.mt_holidays_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
        },
    }

    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            # print "My ID.........",ids
            print  self.pool.get('hr.employee').browse(cr,uid,ids[0]).parent_id.name
            print  self.pool.get('hr.employee').browse(cr,uid,ids[0]).parent_id.user_id.id
            return ids[0]
        return False

    def create(self,cr,uid,vals,context=None):
    	vals['state'] = 'confirm'
    	if 'created_by' in vals and vals['created_by']:
    		emp_id=self.pool.get('hr.employee').browse(cr,uid,vals['created_by'])
    		if emp_id.parent_id and emp_id.parent_id.user_id.id:
        		vals['approve_user_id']=emp_id.parent_id.user_id.id
        		vals['user_id']=emp_id.user_id and emp_id.user_id.id or False
        res=super(employee_requision,self).create(cr,uid,vals,context=None)
        return res

    def set_recruit(self, cr, uid, ids, context=None):
        for job in self.browse(cr, uid, ids, context=context).job_line:
            no_of_recruitment = job.vacancy == 0 and 1 or job.vacancy
            self.pool.get('hr.job').write(cr, uid, [job.job_id.id], {'state': 'recruit', 'no_of_recruitment': no_of_recruitment}, context=context)
            res = self.write(cr,uid,ids,{'state' : 'recruit'},context=context)
        return res

    def set_recruit_close(self, cr, uid, ids, context=None):
        for job in self.browse(cr, uid, ids, context=context).job_line:
            no_of_recruitment = job.vacancy == 0 and 1 or job.vacancy
            self.pool.get('hr.job').write(cr, uid, [job.job_id.id], {'state': 'open', 'no_of_recruitment': 0}, context=context)
            res = self.write(cr,uid,ids,{'state' : 'open'},context=context)
        return res

    _columns={
    	'name' : fields.char('Ref Number'),
    	'department_id' : fields.many2one('hr.department','Department Name'),
    	'address_id' : fields.many2many('res.partner', 'res_partner_requision_rel', 'requision_id', 'requision_address_id', 'Location'),
    	'job_line': fields.one2many('requision.job.line','requision_id','Position'),
    	'date_request' : fields.date('Date Request'),
    	'created_by' : fields.many2one('hr.employee','Created By'),
    	'reporting_authority' : fields.many2one('hr.employee','Reporting Authority'),
    	'job_description' : fields.html('Job Description'),
    	'primary_responsibilities' : fields.html('Responsibilities'),
    	'preferred_indust' : fields.char('Preferred Industry'),
    	'type_ids' : fields.many2many('hr.recruitment.degree','education_group_rel','requision_id','education_master_id','Education Qualification'),
    	'state': fields.selection([('draft','To Submit'),('confirm','To Approve'),('refuse','Refused'),('validate1','Approval'),('validate','Approved'),('recruit', 'Recruitment in Progress'),('open', 'Recruitment Closed')],
                'Status', track_visibility='onchange',
                 help='The status is set to \'To Submit\', when a holiday request is created.\
                 \nThe status is \'To Approve\', when holiday request is confirmed by user.\
                 \nThe status is \'Refused\', when holiday request is refused by manager.\
                 \nThe status is \'Approved\', when holiday request is approved by manager.'),
    	'user_id':fields.many2one('res.users','User'),
    	'approve_user_id':fields.many2one('res.users','Approve User')
    }
    _defaults = {
		'state': 'draft',
        'date_request' : fields.date.context_today,
		'user_id': lambda obj, cr, uid, context: uid,
		'created_by': _employee_get,
	}
    def approve_requision_req(self,cr,uid,ids,context=None):
        res = self.write(cr,uid,ids,{'state' : 'validate'},context=None)
        return res 
    def reset_to_approve(self,cr,uid,ids,context=None):
        res = self.write(cr,uid,ids,{'state' : 'confirm'},context=None)
        return res 

class requision_job_line(osv.Model):
	_name="requision.job.line"
	_columns ={
		'requision_id' : fields.many2one('employee.requision','Requision Id'),
		'job_id' : fields.many2one('hr.job','Job'),
		'experiance' : fields.integer('Experiance Required'),
		'remarks' : fields.char('Remarks'),
		'vacancy' : fields.integer('No of Vacancy'),
	}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
