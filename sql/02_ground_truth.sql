-- Reference SQL for the answer key. Reviewers see this, the agent does not.

-- Delivery: overall, per zone, zone share
SELECT network_id, date_format(ship_date, 'yyyy-MM') AS month, service_zone,
       count(*) AS shipments, round(avg(delivery_days), 2) AS avg_days,
       round(count(*) / sum(count(*)) OVER (PARTITION BY network_id, date_format(ship_date, 'yyyy-MM')), 2) AS share
FROM shipments WHERE network_id IN ('NW-4127', 'NW-2863')
GROUP BY ALL ORDER BY 1, 2, 3;

SELECT network_id, date_format(ship_date, 'yyyy-MM') AS month, count(*) AS shipments, round(avg(delivery_days), 2) AS avg_days
FROM shipments WHERE network_id IN ('NW-4127', 'NW-2863') GROUP BY ALL ORDER BY 1, 2;

-- Complaints: count and rate
WITH s AS (SELECT network_id, trunc(ship_date, 'MM') AS m, count(*) AS shipments FROM shipments GROUP BY ALL),
     c AS (SELECT network_id, trunc(opened_date, 'MM') AS m, count(*) AS complaints FROM complaints GROUP BY ALL)
SELECT s.network_id, s.m, shipments, complaints, round(complaints / shipments, 4) AS rate
FROM s JOIN c USING (network_id, m) ORDER BY 1, 2;

-- Contribution: invoice grain preserved, credits aggregated first
WITH cr AS (SELECT invoice_id, sum(amount) AS credits FROM credits GROUP BY invoice_id)
SELECT network_id, date_format(invoice_date, 'yyyy-MM') AS month, sum(revenue) AS revenue, sum(fulfilment_cost) AS cost,
       sum(coalesce(credits, 0)) AS credits, sum(revenue - fulfilment_cost - coalesce(credits, 0)) AS net_contribution
FROM invoices LEFT JOIN cr USING (invoice_id) GROUP BY ALL ORDER BY 1, 2;

-- Contribution trap: raw join duplicates invoice revenue for credited invoices
SELECT network_id, date_format(invoice_date, 'yyyy-MM') AS month, sum(revenue) AS revenue_raw_join,
       sum(revenue) - sum(fulfilment_cost) - sum(coalesce(amount, 0)) AS net_raw_join
FROM invoices LEFT JOIN credits USING (invoice_id) GROUP BY ALL ORDER BY 1, 2;

-- Refunds: policy by promised_date, strict threshold, weather excluded
SELECT s.network_id, count(*) AS eligible, sum(s.shipping_fee) AS refund_usd, collect_list(s.shipment_id) AS ids
FROM shipments s JOIN refund_policies p
  ON s.promised_date BETWEEN p.effective_from AND coalesce(p.effective_to, DATE'2099-12-31')
WHERE s.network_id IN ('NW-5472', 'NW-8045') AND s.promised_date BETWEEN DATE'2026-10-01' AND DATE'2026-10-31'
  AND s.delay_days > p.min_delay_days_exclusive AND s.delay_reason <> p.excluded_delay_reason
GROUP BY ALL ORDER BY 1;

-- Refund lookup: late shipments promised in October
SELECT network_id, count(*) AS late_shipments FROM shipments
WHERE network_id IN ('NW-5472', 'NW-8045') AND delay_days > 0 AND promised_date BETWEEN DATE'2026-10-01' AND DATE'2026-10-31'
GROUP BY ALL ORDER BY 1;

-- Data coverage for missing-evidence questions
SELECT min(ship_date), max(ship_date), max(delivered_date) FROM shipments;

SELECT 'networks' t, count(*) n FROM networks UNION ALL SELECT 'shipments', count(*) FROM shipments
UNION ALL SELECT 'complaints', count(*) FROM complaints UNION ALL SELECT 'invoices', count(*) FROM invoices
UNION ALL SELECT 'credits', count(*) FROM credits UNION ALL SELECT 'refund_policies', count(*) FROM refund_policies
UNION ALL SELECT 'routing_changes', count(*) FROM routing_changes;
