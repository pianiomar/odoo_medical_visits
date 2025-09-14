from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import date


class MedicalVisit(models.Model):
    _name = 'medical.visit'
    _description = 'Visita Medica Sportiva'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'visit_date desc'

    name = fields.Char(string='Numero Visita', required=True, copy=False, readonly=True, default='/')
    
    # Relazione con atleta
    athlete_id = fields.Many2one('medical.athlete', string='Atleta', required=True, ondelete='cascade')
    athlete_name = fields.Char(related='athlete_id.name', string='Nome Atleta', store=True)
    athlete_code = fields.Char(related='athlete_id.athlete_code', string='Codice Atleta', store=True)
    
    # Dati della visita
    visit_date = fields.Date(string='Data Visita', required=True, default=fields.Date.context_today, tracking=True)
    visit_type = fields.Selection([
        ('initial', 'Visita Iniziale'),
        ('renewal', 'Rinnovo'),
        ('control', 'Controllo'),
        ('return', 'Visita di Controllo Post-Infortunio'),
        ('special', 'Visita Specialistica')
    ], string='Tipo Visita', required=True, default='renewal')
    
    # Medico e struttura
    doctor_name = fields.Char(string='Medico', required=True)
    medical_center = fields.Char(string='Centro Medico/Struttura')
    doctor_registration = fields.Char(string='Numero Albo Medico')
    
    # Risultati della visita
    result = fields.Selection([
        ('suitable', 'Idoneo'),
        ('not_suitable', 'Non Idoneo'),
        ('suitable_with_limits', 'Idoneo con Limitazioni'),
        ('pending', 'In Attesa di Esami')
    ], string='Esito', required=True, default='suitable', tracking=True)
    
    # Date di validità
    issue_date = fields.Date(string='Data Rilascio Certificato')
    expiry_date = fields.Date(string='Data Scadenza', required=True, tracking=True)
    validity_months = fields.Integer(string='Mesi di Validità', default=12)
    
    # Limitazioni e note mediche
    limitations = fields.Text(string='Limitazioni/Prescrizioni')
    medical_notes = fields.Text(string='Note Mediche')
    
    # Parametri vitali (opzionali)
    height = fields.Float(string='Altezza (cm)')
    weight = fields.Float(string='Peso (kg)')
    blood_pressure_sys = fields.Integer(string='Pressione Sistolica')
    blood_pressure_dia = fields.Integer(string='Pressione Diastolica')
    heart_rate = fields.Integer(string='Frequenza Cardiaca')
    
    # BMI calcolato
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True)
    bmi_category = fields.Selection([
        ('underweight', 'Sottopeso'),
        ('normal', 'Normale'),
        ('overweight', 'Sovrappeso'),
        ('obese', 'Obeso')
    ], string='Categoria BMI', compute='_compute_bmi_category', store=True)
    
    # Documenti allegati
    certificate_file = fields.Binary(string='Certificato PDF')
    certificate_filename = fields.Char(string='Nome File Certificato')
    additional_documents = fields.Binary(string='Documenti Aggiuntivi')
    additional_documents_filename = fields.Char(string='Nome File Documenti')
    
    # Stati e controlli
    active = fields.Boolean(string='Attivo', default=True)
    is_current = fields.Boolean(string='Certificato Corrente', compute='_compute_is_current', store=True)
    days_to_expiry = fields.Integer(string='Giorni alla Scadenza', compute='_compute_days_to_expiry')
    
    # Costi (opzionale)
    cost = fields.Float(string='Costo Visita')
    currency_id = fields.Many2one('res.currency', string='Valuta', default=lambda self: self.env.company.currency_id)
    
    # Note generali
    notes = fields.Text(string='Note')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.visit') or '/'
        
        # Calcola automaticamente la data di scadenza se non fornita
        if 'visit_date' in vals and 'validity_months' in vals and not vals.get('expiry_date'):
            visit_date = fields.Date.from_string(vals['visit_date'])
            vals['expiry_date'] = visit_date + relativedelta(months=vals['validity_months'])
        
        return super().create(vals)

    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight and record.height > 0:
                height_m = record.height / 100  # Converti cm in metri
                record.bmi = round(record.weight / (height_m * height_m), 2)
            else:
                record.bmi = 0.0

    @api.depends('bmi')
    def _compute_bmi_category(self):
        for record in self:
            if record.bmi == 0:
                record.bmi_category = False
            elif record.bmi < 18.5:
                record.bmi_category = 'underweight'
            elif record.bmi < 25:
                record.bmi_category = 'normal'
            elif record.bmi < 30:
                record.bmi_category = 'overweight'
            else:
                record.bmi_category = 'obese'

    @api.depends('expiry_date', 'result')
    def _compute_is_current(self):
        today = date.today()
        for record in self:
            record.is_current = (
                record.result == 'suitable' and 
                record.expiry_date and 
                record.expiry_date >= today
            )

    @api.depends('expiry_date')
    def _compute_days_to_expiry(self):
        today = date.today()
        for record in self:
            if record.expiry_date:
                delta = record.expiry_date - today
                record.days_to_expiry = delta.days
            else:
                record.days_to_expiry = 0

    @api.onchange('visit_date', 'validity_months')
    def _onchange_visit_date_validity(self):
        """Calcola automaticamente la data di scadenza"""
        if self.visit_date and self.validity_months:
            self.expiry_date = self.visit_date + relativedelta(months=self.validity_months)

    @api.onchange('athlete_id')
    def _onchange_athlete_id(self):
        """Precompila alcuni campi quando si seleziona un atleta"""
        if self.athlete_id:
            # Suggerisce il tipo di visita basandosi sulle visite precedenti
            previous_visits = self.search([('athlete_id', '=', self.athlete_id.id)])
            if not previous_visits:
                self.visit_type = 'initial'
            else:
                self.visit_type = 'renewal'

    def action_mark_as_current(self):
        """Marca questa visita come quella corrente per l'atleta"""
        # Disattiva tutte le altre visite per questo atleta
        other_visits = self.search([
            ('athlete_id', '=', self.athlete_id.id),
            ('id', '!=', self.id)
        ])
        other_visits.write({'is_current': False})
        
        # Attiva questa visita
        self.is_current = True
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Successo',
                'message': 'Visita marcata come corrente',
                'type': 'success',
            }
        }

    def action_send_expiry_reminder(self):
        """Invia promemoria di scadenza"""
        # Questa funzione può essere estesa per inviare email o SMS
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Promemoria',
                'message': f'Promemoria inviato per la visita in scadenza il {self.expiry_date}',
                'type': 'info',
            }
        }

    @api.model
    def cron_check_expiring_visits(self):
        """Cron job per controllare le visite in scadenza"""
        today = date.today()
        warning_date = today + relativedelta(days=30)  # Avviso 30 giorni prima
        
        expiring_visits = self.search([
            ('expiry_date', '<=', warning_date),
            ('expiry_date', '>=', today),
            ('result', '=', 'suitable'),
            ('active', '=', True)
        ])
        
        # Log delle visite in scadenza
        if expiring_visits:
            self.env['mail.thread'].message_post(
                subject='Visite Mediche in Scadenza',
                body=f'Trovate {len(expiring_visits)} visite mediche in scadenza nei prossimi 30 giorni.',
            )
        
        return True


class MedicalVisitType(models.Model):
    """Tipi di visite mediche personalizzabili"""
    _name = 'medical.visit.type'
    _description = 'Tipo Visita Medica'

    name = fields.Char(string='Nome', required=True)
    code = fields.Char(string='Codice', required=True)
    description = fields.Text(string='Descrizione')
    default_validity_months = fields.Integer(string='Validità Default (mesi)', default=12)
    active = fields.Boolean(string='Attivo', default=True)


class MedicalCenter(models.Model):
    """Centri medici/medici convenzionati"""
    _name = 'medical.center'
    _description = 'Centro Medico'

    name = fields.Char(string='Nome Centro/Medico', required=True)
    address = fields.Text(string='Indirizzo')
    phone = fields.Char(string='Telefono')
    email = fields.Char(string='Email')
    website = fields.Char(string='Sito Web')
    contact_person = fields.Char(string='Referente')
    specializations = fields.Text(string='Specializzazioni')
    notes = fields.Text(string='Note')
    active = fields.Boolean(string='Attivo', default=True)