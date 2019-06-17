from migrate_sql.config import SQLItem

sql_items = [
    SQLItem(
        'custrates_view',   # name of the item
        'DROP VIEW IF EXISTS custrates CASCADE; '
        ' CREATE OR REPLACE VIEW custrates AS '
        ' SELECT row_number() OVER () AS id, * FROM ('
        ' SELECT r.id AS ratecard_id, 1 AS rate_type, r.name AS ratecard_name, r.rc_type, pr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, prefix, destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r'
        ' JOIN pyfb_rating_c_prefix_rate pr ON pr.c_ratecard_id = r.id  AND pr.status <> \'disabled\''
        ' WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end'
        ' UNION ALL'
        ' SELECT r.id AS ratecard_id, 2 AS rate_type, r.name AS ratecard_name, r.rc_type, dr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r'
        ' JOIN pyfb_rating_c_destination_rate dr ON dr.c_ratecard_id = r.id  AND dr.status <> \'disabled\''
        ' WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end'
        ' UNION ALL'
        ' SELECT r.id AS ratecard_id, 3 AS rate_type, r.name AS ratecard_name, r.rc_type, ctr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, country_id, type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r'
        ' JOIN pyfb_rating_c_countrytype_rate ctr ON ctr.c_ratecard_id = r.id  AND ctr.status <> \'disabled\''
        ' WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end'
        ' UNION ALL'
        ' SELECT r.id AS ratecard_id, 4 AS rate_type, r.name AS ratecard_name, r.rc_type, cr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r'
        ' JOIN pyfb_rating_c_country_rate cr ON cr.c_ratecard_id = r.id  AND cr.status <> \'disabled\''
        ' WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end'
        ' UNION ALL'
        ' SELECT r.id AS ratecard_id, 5 AS rate_type, r.name AS ratecard_name, r.rc_type, rtr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, type_id, region_id FROM pyfb_rating_c_ratecard r'
        ' JOIN pyfb_rating_c_regiontype_rate rtr ON rtr.c_ratecard_id = r.id  AND rtr.status <> \'disabled\''
        ' WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end'
        ' UNION ALL'
        ' SELECT r.id AS ratecard_id, 6 AS rate_type, r.name AS ratecard_name, r.rc_type, rr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, region_id FROM pyfb_rating_c_ratecard r'
        ' JOIN pyfb_rating_c_region_rate rr ON rr.c_ratecard_id = r.id  AND rr.status <> \'disabled\''
        ' WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end'
        ' UNION ALL'
        ' SELECT r.id AS ratecard_id, 7 AS rate_type, r.name AS ratecard_name, r.rc_type, dr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r'
        ' JOIN pyfb_rating_c_default_rate dr ON dr.c_ratecard_id = r.id  AND dr.status <> \'disabled\''
        ' WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end'
        ' )v;',  # forward sql
        reverse_sql='DROP custrates',  # sql for removal
    ),
]


# DROP VIEW IF EXISTS custrates CASCADE; CREATE OR REPLACE VIEW custrates AS
# SELECT row_number() OVER () AS id, * FROM (
# SELECT r.id AS ratecard_id, 1 AS rate_type, r.name AS ratecard_name, r.rc_type, pr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, prefix, destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r
# JOIN pyfb_rating_c_prefix_rate pr ON pr.c_ratecard_id = r.id  AND pr.status <> 'disabled'
# WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
# UNION ALL
# SELECT r.id AS ratecard_id, 2 AS rate_type, r.name AS ratecard_name, r.rc_type, dr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r
# JOIN pyfb_rating_c_destination_rate dr ON dr.c_ratecard_id = r.id  AND dr.status <> 'disabled'
# WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
# UNION ALL
# SELECT r.id AS ratecard_id, 3 AS rate_type, r.name AS ratecard_name, r.rc_type, ctr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, country_id, type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r
# JOIN pyfb_rating_c_countrytype_rate ctr ON ctr.c_ratecard_id = r.id  AND ctr.status <> 'disabled'
# WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
# UNION ALL
# SELECT r.id AS ratecard_id, 4 AS rate_type, r.name AS ratecard_name, r.rc_type, cr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r
# JOIN pyfb_rating_c_country_rate cr ON cr.c_ratecard_id = r.id  AND cr.status <> 'disabled'
# WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
# UNION ALL
# SELECT r.id AS ratecard_id, 5 AS rate_type, r.name AS ratecard_name, r.rc_type, rtr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, type_id, region_id FROM pyfb_rating_c_ratecard r
# JOIN pyfb_rating_c_regiontype_rate rtr ON rtr.c_ratecard_id = r.id  AND rtr.status <> 'disabled'
# WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
# UNION ALL
# SELECT r.id AS ratecard_id, 6 AS rate_type, r.name AS ratecard_name, r.rc_type, rr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, region_id FROM pyfb_rating_c_ratecard r
# JOIN pyfb_rating_c_region_rate rr ON rr.c_ratecard_id = r.id  AND rr.status <> 'disabled'
# WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
# UNION ALL
# SELECT r.id AS ratecard_id, 7 AS rate_type, r.name AS ratecard_name, r.rc_type, dr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_c_ratecard r
# JOIN pyfb_rating_c_default_rate dr ON dr.c_ratecard_id = r.id  AND dr.status <> 'disabled'
# WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
# )v;

DROP VIEW IF EXISTS pyfb_provrates_v CASCADE; CREATE OR REPLACE VIEW pyfb_provrates_v AS
SELECT row_number() OVER () AS id, * FROM (
SELECT r.provider_id, r.id AS ratecard_id, 1 AS rate_type, r.name AS ratecard_name, r.provider_prefix, r.estimated_quality, r.rc_type, pr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, prefix, destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_p_ratecard r
JOIN pyfb_rating_p_prefix_rate pr ON pr.p_ratecard_id = r.id  AND pr.status <> 'disabled'
WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
UNION ALL
SELECT r.provider_id, r.id AS ratecard_id, 2 AS rate_type, r.name AS ratecard_name, r.provider_prefix, r.estimated_quality, r.rc_type, dr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_p_ratecard r
JOIN pyfb_rating_p_destination_rate dr ON dr.p_ratecard_id = r.id  AND dr.status <> 'disabled'
WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
UNION ALL
SELECT r.provider_id, r.id AS ratecard_id, 3 AS rate_type, r.name AS ratecard_name, r.provider_prefix, r.estimated_quality, r.rc_type, ctr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, country_id, type_id, CAST(null AS int) AS region_id FROM pyfb_rating_p_ratecard r
JOIN pyfb_rating_p_countrytype_rate ctr ON ctr.p_ratecard_id = r.id  AND ctr.status <> 'disabled'
WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
UNION ALL
SELECT r.provider_id, r.id AS ratecard_id, 4 AS rate_type, r.name AS ratecard_name, r.provider_prefix, r.estimated_quality, r.rc_type, cr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_p_ratecard r
JOIN pyfb_rating_p_country_rate cr ON cr.p_ratecard_id = r.id  AND cr.status <> 'disabled'
WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
UNION ALL
SELECT r.provider_id, r.id AS ratecard_id, 5 AS rate_type, r.name AS ratecard_name, r.provider_prefix, r.estimated_quality, r.rc_type, rtr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, type_id, region_id FROM pyfb_rating_p_ratecard r
JOIN pyfb_rating_p_regiontype_rate rtr ON rtr.p_ratecard_id = r.id  AND rtr.status <> 'disabled'
WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
UNION ALL
SELECT r.provider_id, r.id AS ratecard_id, 6 AS rate_type, r.name AS ratecard_name, r.provider_prefix, r.estimated_quality, r.rc_type, rr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, region_id FROM pyfb_rating_p_ratecard r
JOIN pyfb_rating_p_region_rate rr ON rr.p_ratecard_id = r.id  AND rr.status <> 'disabled'
WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
UNION ALL
SELECT r.provider_id, r.id AS ratecard_id, 7 AS rate_type, r.name AS ratecard_name, r.provider_prefix, r.estimated_quality, r.rc_type, dr.status, r_rate, r_block_min_duration, r_minimal_time, r_init_block, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_rating_p_ratecard r
JOIN pyfb_rating_p_default_rate dr ON dr.p_ratecard_id = r.id  AND dr.status <> 'disabled'
WHERE r.status = 'enabled' AND now() > r.date_start AND now() < r.date_end
)v;

# calcul de marge négative = variable kamailio = 2 min moyenne d'appel !


DROP VIEW IF EXISTS pyfb_routes_v CASCADE; CREATE OR REPLACE VIEW pyfb_routes_v AS
SELECT row_number() OVER () AS id, v.* FROM (
SELECT r.customer_id, r.routinggroup_id, 1 AS route_type, providerendpoint_id, provider_ratecard_id, route_type AS route_rule, status, weight, priority, prefix, destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_routing_c_routinggrp r
JOIN pyfb_routing_prefix_rule pr ON pr.c_route_id = r.routinggroup_id  AND pr.status <> 'disabled'
JOIN pyfb_routing_prefix_rule_provider_gateway_list pg ON pg.prefixrule_id = pr.id

UNION ALL
SELECT r.customer_id, r.routinggroup_id, 2 AS route_type, providerendpoint_id, provider_ratecard_id, route_type AS route_rule, status, weight, priority, CAST(null AS varchar) AS prefix, 0 AS destnum_length, destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_routing_c_routinggrp r
JOIN pyfb_routing_destination_rule der ON der.c_route_id = r.routinggroup_id  AND der.status <> 'disabled'
JOIN pyfb_routing_destination_rule_provider_gateway_list deg ON deg.destinationrule_id = der.id

UNION ALL
SELECT r.customer_id, r.routinggroup_id, 3 AS route_type, providerendpoint_id, provider_ratecard_id, route_type AS route_rule, status, weight, priority, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, country_id, type_id, CAST(null AS int) AS region_id FROM pyfb_routing_c_routinggrp r
JOIN pyfb_routing_countrytype_rule ctr ON ctr.c_route_id = r.routinggroup_id  AND ctr.status <> 'disabled'
JOIN pyfb_routing_countrytype_rule_provider_gateway_list ctg ON ctg.countrytyperule_id = ctr.id

UNION ALL
SELECT r.customer_id, r.routinggroup_id, 4 AS route_type, providerendpoint_id, provider_ratecard_id, route_type AS route_rule, status, weight, priority, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_routing_c_routinggrp r
JOIN pyfb_routing_countryrule cr ON cr.c_route_id = r.routinggroup_id  AND cr.status <> 'disabled'
JOIN pyfb_routing_countryrule_provider_gateway_list cg ON cg.countryrule_id = cr.id

UNION ALL
SELECT r.customer_id, r.routinggroup_id, 5 AS route_type, providerendpoint_id, provider_ratecard_id, route_type AS route_rule, status, weight, priority, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, type_id, region_id FROM pyfb_routing_c_routinggrp r
JOIN pyfb_routing_regiontype_rule rtr ON rtr.c_route_id = r.routinggroup_id  AND rtr.status <> 'disabled'
JOIN pyfb_routing_regiontype_rule_provider_gateway_list rtg ON rtg.regiontyperule_id = rtr.id

UNION ALL
SELECT r.customer_id, r.routinggroup_id, 6 AS route_type, providerendpoint_id, provider_ratecard_id, route_type AS route_rule, status, weight, priority, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, region_id FROM pyfb_routing_c_routinggrp r
JOIN pyfb_routing_region_rule rr ON rr.c_route_id = r.routinggroup_id  AND rr.status <> 'disabled'
JOIN pyfb_routing_region_rule_provider_gateway_list rg ON rg.regionrule_id = rr.id

UNION ALL
SELECT r.customer_id, r.routinggroup_id, 7 AS route_type, providerendpoint_id, provider_ratecard_id, route_type AS route_rule, status, weight, priority, CAST(null AS varchar) AS prefix, 0 AS destnum_length, CAST(null AS int) AS destination_id, CAST(null AS int) AS country_id, CAST(null AS int) AS type_id, CAST(null AS int) AS region_id FROM pyfb_routing_c_routinggrp r
JOIN pyfb_routing_default_rule dr ON dr.c_route_id = r.routinggroup_id  AND dr.status <> 'disabled'
JOIN pyfb_routing_default_rule_provider_gateway_list dg ON dg.defaultrule_id = dr.id

) v;
