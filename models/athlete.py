from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date


class Athlete(models.Model):
    _name = 'medical.athlete'
    _description = 'Atleta ASD'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Dati anagrafici
    name = fields.Char(string='Nome Completo', compute='_compute_name', store=True, tracking=True)
    first_name = fields.Char(string='Nome', required=True)
    last_name = fields.Char(string='Cognome', required=True)
    
    # Codici identificativi
    athlete_code = fields.Char(string='Codice Atleta', required=True, copy=False)
    fiscal_code = fields.Char(string='Codice Fiscale', size=16)
    
    # Dati anagrafici
    birth_date = fields.Date(string='Data di Nascita', required=True)
    birth_place = fields.Char(string='Luogo di Nascita')
    age = fields.Integer(string='Età', compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Maschio'),
        ('female', 'Femmina'),
        ('other', 'Altro')
    ], string='Sesso', required=True)
    
    # Contatti
    email = fields.Char(string='Email')
    phone = fields.Char(string='Telefono')
    mobile = fields.Char(string='Cellulare')
    
    # Indirizzo
    street = fields.Char(string='Via')
    street2 = fields.Char(string='Via 2')
    city = fields.Char(string='Città')
    zip = fields.Char(string='CAP')
    state_id = fields.Many2one('res.country.state', string='Provincia')
    country_id = fields.Many2one('res.country', string='Paese', default=lambda self: self.env.ref('base.it'))
    
    # Dati sportivi
    sport_discipline = fields.Selection([
        ('football', 'Calcio'),
        ('basketball', 'Pallacanestro'),
        ('volleyball', 'Pallavolo'),
        ('tennis', 'Tennis'),
        ('athletics', 'Atletica'),
        ('swimming', 'Nuoto'),
        ('cycling', 'Ciclismo'),
        ('martial_arts', 'Arti Marziali'),
        ('other', 'Altro')
    ], string='Disciplina Sportiva', required=True)
    
    sport_category = fields.Selection([
        ('youth', 'Giovanile'),
        ('amateur', 'Amatoriale'),
        ('competitive', 'Agonistico'),
        ('professional', 'Professionistico')
    ], string='Categoria', default='amateur', required=True)
    
    registration_date = fields.Date(string='Data Iscrizione', default=fields.Date.context_today)
    active_member = fields.Boolean(string='Socio Attivo', default=True)
    
    # Visite mediche
    medical_visit_ids = fields.One2many('medical.visit', 'athlete_id', string='Visite Mediche')
    last_medical_visit = fields.Date(string='Ultima Visita', compute='_compute_last_medical_visit', store=True)
    next_medical_visit_due = fields.Date(string='Prossima Scadenza', compute='_compute_next_medical_visit', store=True)
    medical_status = fields.Selection([
        ('valid', 'Certificato Valido'),
        ('expiring', 'In Scadenza (30gg)'),
        ('expired', 'Scaduto'),
        ('none', 'Nessun Certificato')
    ], string='Stato Medico', compute='_compute_medical_status', store=True)
    
    # Contatti emergenza
    emergency_contact_name = fields.Char(string='Contatto Emergenza - Nome')
    emergency_contact_phone = fields.Char(string='Contatto Emergenza - Telefono')
    emergency_contact_relation = fields.Char(string='Contatto Emergenza - Parentela')
    
    # Note
    notes = fields.Text(string='Note')

    @api.depends('first_name', 'last_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.first_name} {record.last_name}"

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.birth_date:
                record.age = relativedelta(today, record.birth_date).years
            else:
                record.age = 0

    @api.depends('medical_visit_ids', 'medical_visit_ids.visit_date')
    def _compute_last_medical_visit(self):
        for record in self:
            if record.medical_visit_ids:
                record.last_medical_visit = max(record.medical_visit_ids.mapped('visit_date'))
            else:
                record.last_medical_visit = False

    @api.depends('medical_visit_ids', 'medical_visit_ids.expiry_date')
    def _compute_next_medical_visit(self):
        for record in self:
            valid_visits = record.medical_visit_ids.filtered(lambda v: v.result == 'suitable' and v.expiry_date)
            if valid_visits:
                # Trova la visita con scadenza più lontana nel futuro
                record.next_medical_visit_due = max(valid_visits.mapped('expiry_date'))
            else:
                record.next_medical_visit_due = False

    @api.depends('next_medical_visit_due')
    def _compute_medical_status(self):
        today = date.today()
        for record in self:
            if not record.next_medical_visit_due:
                record.medical_status = 'none'
            elif record.next_medical_visit_due < today:
                record.medical_status = 'expired'
            elif record.next_medical_visit_due <= today + relativedelta(days=30):
                record.medical_status = 'expiring'
            else:
                record.medical_status = 'valid'

    @api.model
    def create(self, vals):
        # Genera automaticamente il nome completo
        if 'first_name' in vals and 'last_name' in vals:
            vals['name'] = f"{vals['first_name']} {vals['last_name']}"
        
        # Genera codice atleta se non fornito
        if not vals.get('athlete_code'):
            sequence = self.env['ir.sequence'].next_by_code('medical.athlete.code') or '001'
            vals['athlete_code'] = f"ATL{sequence}"
        
        return super().create(vals)

    def write(self, vals):
        result = super().write(vals)

        # Aggiorna il nome completo se cambiano nome o cognome
        if 'first_name' in vals or 'last_name' in vals:
            for record in self:
                record.name = f"{record.first_name} {record.last_name}"

        return result

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        """Calcola automaticamente il nome completo"""
        for record in self:
            if record.first_name and record.last_name:
                record.name = f"{record.first_name} {record.last_name}"
            elif record.first_name:
                record.name = record.first_name
            elif record.last_name:
                record.name = record.last_name
            else:
                record.name = "Nuovo Atleta"

    def action_view_medical_visits(self):
        """Apre la vista delle visite mediche per questo atleta"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Visite Mediche - {self.name}',
            'res_model': 'medical.visit',
            'view_mode': 'tree,form',
            'domain': [('athlete_id', '=', self.id)],
            'context': {'default_athlete_id': self.id},
        }

    def action_create_medical_visit(self):
        """Crea una nuova visita medica per questo atleta"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nuova Visita Medica',
            'res_model': 'medical.visit',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_athlete_id': self.id},
        }