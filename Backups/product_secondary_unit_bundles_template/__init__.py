from . import models

from odoo import api, SUPERUSER_ID, _


def _auto_init_secondary_units_bundles(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    field_height = env['ir.model.fields'].search([('name', '=', 'product_height'), ('model', '=', 'product.product')])
    field_length = env['ir.model.fields'].search([('name', '=', 'product_length'), ('model', '=', 'product.product')])
    field_width = env['ir.model.fields'].search([('name', '=', 'product_width'), ('model', '=', 'product.product')])
    field_dimension = env['ir.model.fields'].search([('name', '=', 'dimensional_uom_id'), ('model', '=', 'product.product')])
    field_uom_id = env['ir.model.fields'].search([('name', '=', 'uom_id'), ('model', '=', 'product.product')])
    field_pcs = env['ir.model.fields'].search([('name', '=', 'pcs'), ('model', '=', 'product.product')])


    uom_unit = env.ref("uom.product_uom_unit")
    uom_meter = env.ref("uom.product_uom_meter")

    pcs_vals = {
        'name': _("Bundles"),
        'code': _('bundles'),
        'uom_id': uom_unit.id,
        'basis_uom_id': uom_meter.id,
        'dependency_type': 'dependent',
        'domain': '[]',
        'field_ids': [(4, field_dimension.id), (4, field_height.id), (4, field_length.id), (4, field_width.id),
                      (4, field_uom_id.id), (4, field_pcs.id)],
        'save_field_ids': [],

        'python_code': """result = {}
uom_unit = env.ref("uom.product_uom_unit")
uom_meter = env.ref("uom.product_uom_meter")
uom_meter_alt = env['uom.uom'].search([('category_id', '=', uom_meter.category_id.id), ('name', '=ilike', 'jm')], limit=1)
uom_square_meter = env.ref("uom.uom_square_meter")
uom_cubic_meter = env.ref("uom.product_uom_cubic_meter")
all_uom_ids = {uom_unit.id, uom_meter.id, uom_square_meter.id, uom_cubic_meter.id, uom_meter_alt.id}

for value in field_values:
    if not value.get('dimensional_uom_id'):
        continue

    from_uom = env['uom.uom'].browse(value['dimensional_uom_id'][0])
    if not from_uom:
        continue

    field_uom_id = value.get('uom_id')[0]
    if field_uom_id not in all_uom_ids:
        continue
        
    product_uom_factor = env['uom.uom'].browse(field_uom_id).factor
    
    height = record.convert_to_basis_unit(value['product_height'], from_uom)
    length = record.convert_to_basis_unit(value['product_length'], from_uom)
    width = record.convert_to_basis_unit(value['product_width'], from_uom)
    pcs = value.get('pcs')

    if not height or not width or not length or not pcs:
      continue
    if field_uom_id == uom_unit.id:
         result[value['id']] = pcs
    elif field_uom_id == uom_meter.id or field_uom_id == uom_meter_alt.id:
         result[value['id']] = length * pcs
    elif field_uom_id == uom_square_meter.id:
         result[value['id']] = length * width * pcs
    elif field_uom_id == uom_cubic_meter.id:
         result[value['id']] = length * width * height * pcs"""
    }


    to_create = []
    if not env['product.secondary.unit.template'].search([('uom_id', '=', uom_unit.id)]):
        to_create.append(pcs_vals)

    unit_templates = env['product.secondary.unit.template'].create(to_create)
    unit_templates.apply_to_products()
