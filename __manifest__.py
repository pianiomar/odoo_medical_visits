{
    'name': 'Visite Mediche Atleti ASD',
    'version': '17.0.1.0.0',
    'category': 'Sports Management',
    'summary': 'Gestione visite mediche annuali per atleti ASD',
    'description': """
        Modulo per la gestione delle visite mediche degli atleti
        ========================================================
        
        Funzionalità principali:
        * Anagrafica atleti
        * Registrazione visite mediche
        * Scadenze e promemoria
        * Gestione documenti/certificati
        * Report e statistiche
    """,
    'author': 'Il tuo nome',
    'website': 'https://www.tuaasd.it',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/athlete_views.xml',
        'views/medical_visit_views.xml',
        'views/menu_views.xml',
        'data/medical_visit_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}