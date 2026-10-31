-- Reference SQL for round 2 traps. Run with MERIDIAN_SCHEMA=meridian_parcel_r2.

-- Partial month: rows, date coverage, shipments per covered day
SELECT network_id, date_format(ship_date, 'yyyy-MM') AS month, count(*) AS shipments,
       min(ship_date) AS first_day, max(ship_date) AS last_day,
       round(count(*) / (datediff(max(ship_date), min(ship_date)) + 1), 1) AS per_day
FROM shipments WHERE network_id IN ('NW-6731', 'NW-2290') GROUP BY ALL ORDER BY 1, 2;

-- Duplicate load: rows vs distinct shipment_id, loads
SELECT network_id, date_format(ship_date, 'yyyy-MM') AS month, count(*) AS row_count,
       count(DISTINCT shipment_id) AS distinct_shipments, collect_set(load_batch_id) AS loads
FROM shipments WHERE network_id IN ('NW-9154', 'NW-4486') GROUP BY ALL ORDER BY 1, 2;

-- Test parcels: overall average vs customer-only average
SELECT network_id, date_format(ship_date, 'yyyy-MM') AS month, count(*) AS all_rows,
       sum(CASE WHEN is_test THEN 1 ELSE 0 END) AS test_rows,
       round(avg(delivery_days), 2) AS avg_all,
       round(avg(CASE WHEN NOT is_test THEN delivery_days END), 2) AS avg_customer
FROM shipments WHERE network_id IN ('NW-3378', 'NW-7712') GROUP BY ALL ORDER BY 1, 2;

-- Zone-mix complaint rate: overall and per zone, with zone share
WITH s AS (SELECT network_id, trunc(ship_date, 'MM') AS m, service_zone, count(*) AS shipments
           FROM shipments WHERE network_id IN ('NW-5809', 'NW-1263') GROUP BY ALL),
     c AS (SELECT c.network_id, trunc(c.opened_date, 'MM') AS m, sh.service_zone, count(*) AS complaints
           FROM complaints c JOIN shipments sh USING (shipment_id)
           WHERE c.network_id IN ('NW-5809', 'NW-1263') GROUP BY ALL)
SELECT s.network_id, s.m, s.service_zone, shipments, complaints, round(complaints / shipments, 3) AS rate,
       round(shipments / sum(shipments) OVER (PARTITION BY s.network_id, s.m), 2) AS share
FROM s JOIN c USING (network_id, m, service_zone) ORDER BY 1, 2, 3;

WITH s AS (SELECT network_id, trunc(ship_date, 'MM') AS m, count(*) AS shipments FROM shipments
           WHERE network_id IN ('NW-5809', 'NW-1263') GROUP BY ALL),
     c AS (SELECT network_id, trunc(opened_date, 'MM') AS m, count(*) AS complaints FROM complaints
           WHERE network_id IN ('NW-5809', 'NW-1263') GROUP BY ALL)
SELECT network_id, m, shipments, complaints, round(complaints / shipments, 3) AS rate
FROM s JOIN c USING (network_id, m) ORDER BY 1, 2;

-- Round 1 networks are unchanged in the copy
SELECT (SELECT count(*) FROM shipments WHERE network_id IN (SELECT network_id FROM meridian_parcel.networks)) AS r2_rows,
       (SELECT count(*) FROM meridian_parcel.shipments) AS r1_rows;
