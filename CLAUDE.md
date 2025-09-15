# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Odoo 17 custom module for managing medical visits for athletes in Italian sports associations (ASD - Associazione Sportiva Dilettantistica). The module tracks athlete medical certificates, visit schedules, and compliance with Italian sports medicine regulations.

## Core Architecture

### Model Structure
- **medical.athlete** (`models/athlete.py`): Core athlete model with personal data, sports info, and medical status tracking
- **medical.visit** (`models/medical_visit.py`): Medical visit records with automated expiry calculations and BMI computations
- **medical.visit.type** (`models/medical_visit.py:215`): Configurable visit types
- **medical.center** (`models/medical_visit.py:227`): Medical centers/doctors registry

### Key Model Relationships
- Athlete → Medical Visits (one-to-many via `medical_visit_ids`)
- Computed fields for medical status tracking (`medical_status`, `next_medical_visit_due`)
- Automatic sequence generation for athlete codes and visit numbers

### Data Flow
1. Athletes are created with auto-generated codes (ATL{sequence})
2. Medical visits automatically calculate expiry dates based on validity_months
3. Athlete medical status is computed from active visit certificates
4. Cron job checks for expiring certificates (`cron_check_expiring_visits`)

## Development Commands

### Odoo Module Operations
```bash
# Module update (after code changes)
python3 odoo-bin --addons-path=/path/to/odoo/addons,/path/to/odoo/odoo/addons,/path/to/custom-addons -u medical_visits -d database_name

# Install module
python3 odoo-bin --addons-path=/path/to/odoo/addons,/path/to/odoo/odoo/addons,/path/to/custom-addons -i medical_visits -d database_name

# Debug mode with specific module
python3 odoo-bin --addons-path=/path/to/odoo/addons,/path/to/odoo/odoo/addons,/path/to/custom-addons -d database_name --dev=reload,qweb,werkzeug,xml
```

### Version Compatibility
- Module version must match Odoo version (18.0.x.y.z format for Odoo 18)
- Category should use standard Odoo categories (e.g., 'Productivity')

### Testing
No specific test framework is configured. Test manually through Odoo interface or create standard Odoo test files in `tests/` directory.

## Key Features Implementation

### Medical Status Computation
Athletes have computed medical status based on certificate expiry:
- `valid`: Certificate valid for >30 days
- `expiring`: Certificate expires within 30 days
- `expired`: Certificate past expiry date
- `none`: No valid certificate

### Automatic Calculations
- Age calculation from birth_date (`athlete.py:91`)
- BMI and category from height/weight (`medical_visit.py:97`)
- Expiry date from visit_date + validity_months (`medical_visit.py:140`)

### File Uploads
Binary fields for certificate and additional documents with filename tracking.

## Security Model
Permissions defined in `security/ir.model.access.csv`:
- Standard users: full access to athletes and visits
- Portal users: read-only access
- Configuration models: limited write access

## View Architecture
- Tree/form/kanban views for athletes and visits
- Dashboard with medical status indicators
- Calendar view for visit scheduling
- Smart buttons for navigation between related records

## Data Requirements
- Requires `base`, `mail`, `web` modules
- Uses Italian localization (`base.it` country default)
- Sequence configurations needed for athlete codes and visit numbers

## Custom Actions
- `action_view_medical_visits()`: Navigate to athlete's visits
- `action_create_medical_visit()`: Quick visit creation
- `action_mark_as_current()`: Set current valid certificate
- Cron job for expiry notifications

## Common Customizations
- Add sports disciplines in `athlete.py:45` selection field
- Modify certificate validity in `medical_visit.py:45` default value
- Extend medical center fields in `medical_visit.py:227`
- Module is build for Odoo 18