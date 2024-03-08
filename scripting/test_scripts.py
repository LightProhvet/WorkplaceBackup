from odoo import api, fields, models, tools, _
# from .util_pricelist_sql import \
#     CREATE_MATERIALIZED_VIEW_QUERY, \
#     MATERIALIZED_VIEW_INDICES_QUERY, \
#     DIRTY_FLAG_TABLE_QUERY, \
#     MODIFICATION_TRIGGERS_QUERY, \
#     REFRESH_MATERIALIZED_VIEW_QUERY, \
#     SET_CACHE_FLAG_CLEAN, \
#     CLEANUP_MODIFICATION_TRIGGERS_QUERY, \
#     CLEANUP_DIRTY_FLAG_TABLE_QUERY, \
#     CLEANUP_CREATE_MATERIALIZED_VIEW_QUERY

class Pricelist(models.Model):
    _inherit = 'product.pricelist'


    def setup_cache(self):
        self._run_pricelist_migration_to_cache_tradehouse()
        self._run_cache_initial_setup()

    def init_setup_querys(self):
        return [CREATE_MATERIALIZED_VIEW_QUERY,
                MATERIALIZED_VIEW_INDICES_QUERY,
                DIRTY_FLAG_TABLE_QUERY,
                MODIFICATION_TRIGGERS_QUERY]

    """
    I understand this is the function i need to optimize
    """
    @api.model
    def _run_pricelist_migration_to_cache_tradehouse(self):
        # Tradehouse specific migration script to transform pricelists (hardcoded)
        self.env.cr.execute("""
                UPDATE product_pricelist_item
                SET base = 'ws_list_price', base_pricelist_id = NULL
                WHERE base_pricelist_id = 2 AND base = 'pricelist';

                UPDATE product_pricelist_item
                SET base = 'list_price', base_pricelist_id = NULL
                WHERE base_pricelist_id = 1 AND base = 'pricelist';

                UPDATE product_pricelist_item
                SET base_pricelist_id = null
                WHERE base != 'pricelist';
            """)

# is_dirty flag järgi tehakse uuesti. kontroll funktsioonis "cron_check_cache_dirty".
# ja siis tehakse "rematerialize_cache() mis teeb REFRESH_MATERIALIZED_VIEW_QUERY"

    def _compute_price_rule_get_items(self, date, prod_ids):
        # see on see, mis Kristjan ütles, et ma peaks muutma - ei, see on funktsioon, kust cacheist välja võetakse asju.
        # Aga siin on query sisenditeks PL id, company id, date ja prod_ids, ehk ei saa otse queris joosta
        pass
