-- Meridian Parcel synthetic benchmark. Schema meridian_parcel in the catalog set by MERIDIAN_CATALOG (see sql/run_sql.py).
-- Network IDs are opaque. The mapping to case/version lives only in runner/answer_key.json.
--   NW-4127 delivery reversal     NW-2863 delivery control
--   NW-7351 complaints reversal   NW-1594 complaints control
--   NW-6208 contribution reversal NW-3916 contribution control
--   NW-5472 refunds reversal      NW-8045 refunds control

CREATE SCHEMA IF NOT EXISTS meridian_parcel;

CREATE OR REPLACE TABLE networks (
  network_id STRING COMMENT 'Distribution network identifier',
  opened_date DATE COMMENT 'Date the network started operating',
  hub_count INT COMMENT 'Number of sorting hubs in the network'
) COMMENT 'One row per Meridian Parcel distribution network';
INSERT INTO networks VALUES
  ('NW-1594', DATE'2021-03-01', 3), ('NW-2863', DATE'2019-06-15', 5),
  ('NW-3916', DATE'2022-01-10', 2), ('NW-4127', DATE'2020-09-01', 4),
  ('NW-5472', DATE'2023-04-03', 2), ('NW-6208', DATE'2018-11-20', 6),
  ('NW-7351', DATE'2021-08-30', 3), ('NW-8045', DATE'2024-02-12', 1);

-- Shipments. delivery_days alternates +/-1 around each segment mean so the means are exact.
-- Spec rows: network, month start, zone, count, mean delivery days, standard promise days.
CREATE OR REPLACE TABLE _shipment_spec AS
SELECT * FROM VALUES
  -- delivery reversal: Sep 200 local@2 + 800 remote@8 = 6.8 ; Oct 800 local@3 + 200 remote@9 = 4.2
  ('NW-4127', DATE'2026-09-01', 'local', 200, 2, 3), ('NW-4127', DATE'2026-09-01', 'remote', 800, 8, 9),
  ('NW-4127', DATE'2026-10-01', 'local', 800, 3, 3), ('NW-4127', DATE'2026-10-01', 'remote', 200, 9, 9),
  -- delivery control: Sep 200 local@2 + 800 remote@8 = 6.8 ; Oct 200 local@1 + 800 remote@7 = 5.8
  ('NW-2863', DATE'2026-09-01', 'local', 200, 2, 3), ('NW-2863', DATE'2026-09-01', 'remote', 800, 8, 9),
  ('NW-2863', DATE'2026-10-01', 'local', 200, 1, 3), ('NW-2863', DATE'2026-10-01', 'remote', 800, 7, 9),
  -- complaints reversal: volume doubles 1000 -> 2000
  ('NW-7351', DATE'2026-09-01', 'local', 600, 3, 3), ('NW-7351', DATE'2026-09-01', 'remote', 400, 8, 9),
  ('NW-7351', DATE'2026-10-01', 'local', 1200, 3, 3), ('NW-7351', DATE'2026-10-01', 'remote', 800, 8, 9),
  -- complaints control: volume flat 1000 -> 1000
  ('NW-1594', DATE'2026-09-01', 'local', 600, 3, 3), ('NW-1594', DATE'2026-09-01', 'remote', 400, 8, 9),
  ('NW-1594', DATE'2026-10-01', 'local', 600, 3, 3), ('NW-1594', DATE'2026-10-01', 'remote', 400, 8, 9)
AS t(network_id, month_start, service_zone, n, mean_days, promise_days);

CREATE OR REPLACE TABLE shipments (
  shipment_id STRING COMMENT 'Shipment identifier',
  network_id STRING COMMENT 'Network that carried the shipment',
  service_zone STRING COMMENT 'local or remote delivery zone',
  ship_date DATE COMMENT 'Date the parcel left the origin hub. The shipment month is the month of ship_date.',
  promised_date DATE COMMENT 'Delivery date promised to the customer',
  delivered_date DATE COMMENT 'Actual delivery date',
  delivery_days INT COMMENT 'Days from ship_date to delivered_date',
  delay_days INT COMMENT 'Days delivered after promised_date, 0 when on time',
  delay_reason STRING COMMENT 'Reason recorded for a late delivery, NULL when on time',
  shipping_fee DECIMAL(10,2) COMMENT 'Shipping fee charged to the customer, USD'
) COMMENT 'One row per parcel shipment';

INSERT INTO shipments
SELECT
  concat('SH-', network_id, '-', date_format(month_start, 'yyMM'), '-', service_zone, '-', lpad(i, 4, '0')),
  network_id, service_zone, ship_date,
  date_add(ship_date, promise_days),
  date_add(ship_date, d),
  d,
  greatest(d - promise_days, 0),
  CASE WHEN d > promise_days THEN 'carrier capacity' END,
  CAST(CASE service_zone WHEN 'local' THEN 12 ELSE 20 END AS DECIMAL(10,2))
FROM (
  SELECT s.*, e.i,
         date_add(s.month_start, e.i % 20) AS ship_date,
         s.mean_days + CASE WHEN s.mean_days < 2 THEN 0 WHEN e.i % 2 = 0 THEN 1 ELSE -1 END AS d
  FROM _shipment_spec s
  LATERAL VIEW posexplode(sequence(1, s.n)) e AS pos, i
);

DROP TABLE _shipment_spec;

-- Refund networks: 40 on-time shipments each, plus 8 delayed shipments designed per policy rules.
INSERT INTO shipments
SELECT concat('SH-', n, '-OT-', lpad(i, 3, '0')), n, 'local',
       date_add(DATE'2026-10-01', i % 28), date_add(DATE'2026-10-04', i % 28), date_add(DATE'2026-10-03', i % 28),
       2, 0, NULL, CAST(20 AS DECIMAL(10,2))
FROM (SELECT explode(array('NW-5472', 'NW-8045')) AS n) LATERAL VIEW explode(sequence(1, 40)) e AS i;

-- delay_days = delivered_date - promised_date; ship_date = promised_date - 3.
INSERT INTO shipments
SELECT shipment_id, network_id, 'local', date_add(promised, -3), promised, date_add(promised, delay),
       3 + delay, delay, reason, CAST(20 AS DECIMAL(10,2))
FROM VALUES
  -- reversal: eligible = R02, R04, R07 -> 3 shipments, $60
  ('SH-NW-5472-L-R01', 'NW-5472', DATE'2026-10-12', 4, 'carrier capacity'), -- old policy, 4 <= 5, delivered after new policy start
  ('SH-NW-5472-L-R02', 'NW-5472', DATE'2026-10-08', 6, 'carrier capacity'), -- old policy, eligible
  ('SH-NW-5472-L-R03', 'NW-5472', DATE'2026-10-10', 5, 'hub backlog'),      -- old policy, 5 is not > 5
  ('SH-NW-5472-L-R04', 'NW-5472', DATE'2026-10-20', 4, 'hub backlog'),      -- new policy, eligible
  ('SH-NW-5472-L-R05', 'NW-5472', DATE'2026-10-22', 7, 'weather'),          -- new policy, weather excluded
  ('SH-NW-5472-L-R06', 'NW-5472', DATE'2026-10-25', 3, 'carrier capacity'), -- new policy, 3 is not > 3
  ('SH-NW-5472-L-R07', 'NW-5472', DATE'2026-10-18', 5, 'carrier capacity'), -- new policy, eligible
  ('SH-NW-5472-L-R08', 'NW-5472', DATE'2026-10-06', 8, 'weather'),          -- old policy, weather excluded
  -- control: every promised date falls under the new policy; eligible = C01..C06 -> 6 shipments, $120
  ('SH-NW-8045-L-C01', 'NW-8045', DATE'2026-10-16', 4, 'carrier capacity'),
  ('SH-NW-8045-L-C02', 'NW-8045', DATE'2026-10-17', 5, 'hub backlog'),
  ('SH-NW-8045-L-C03', 'NW-8045', DATE'2026-10-19', 6, 'carrier capacity'),
  ('SH-NW-8045-L-C04', 'NW-8045', DATE'2026-10-21', 4, 'hub backlog'),
  ('SH-NW-8045-L-C05', 'NW-8045', DATE'2026-10-23', 7, 'carrier capacity'),
  ('SH-NW-8045-L-C06', 'NW-8045', DATE'2026-10-26', 8, 'carrier capacity'),
  ('SH-NW-8045-L-C07', 'NW-8045', DATE'2026-10-24', 6, 'weather'),          -- weather excluded
  ('SH-NW-8045-L-C08', 'NW-8045', DATE'2026-10-27', 3, 'hub backlog')       -- 3 is not > 3
AS t(shipment_id, network_id, promised, delay, reason);

-- Complaints: Sep 40, Oct 60 in both complaint networks, attached to shipments of that month.
CREATE OR REPLACE TABLE complaints (
  complaint_id STRING COMMENT 'Complaint case identifier',
  network_id STRING COMMENT 'Network the complaint relates to',
  shipment_id STRING COMMENT 'Shipment the complaint is about',
  opened_date DATE COMMENT 'Date the customer opened the complaint',
  category STRING COMMENT 'Complaint category'
) COMMENT 'One row per customer complaint case recorded by support';

INSERT INTO complaints
SELECT concat('CP-', network_id, '-', lpad(row_number() OVER (PARTITION BY network_id ORDER BY shipment_id), 3, '0')),
       network_id, shipment_id, delivered_date,
       element_at(array('late delivery', 'damaged parcel', 'missing item', 'courier conduct'), (rn % 4) + 1)
FROM (
  SELECT s.*, row_number() OVER (PARTITION BY network_id, trunc(ship_date, 'MM') ORDER BY shipment_id) AS rn
  FROM shipments s WHERE network_id IN ('NW-7351', 'NW-1594')
)
WHERE (trunc(ship_date, 'MM') = DATE'2026-09-01' AND rn % 25 = 0 AND rn <= 1000)   -- 40
   OR (trunc(ship_date, 'MM') = DATE'2026-10-01' AND network_id = 'NW-7351' AND rn % 33 = 0 AND rn <= 1980) -- 60
   OR (trunc(ship_date, 'MM') = DATE'2026-10-01' AND network_id = 'NW-1594' AND rn % 16 = 0 AND rn <= 960); -- 60

-- Invoices: Sep 10 x $10,000 revenue, $7,000 cost ; Oct 12 x $10,000 revenue, cost 8 x $6,500 + 4 x $7,000.
CREATE OR REPLACE TABLE invoices (
  invoice_id STRING COMMENT 'Customer invoice identifier',
  network_id STRING COMMENT 'Network that fulfilled the invoiced work',
  invoice_date DATE COMMENT 'Invoice date. The invoice month is the month of invoice_date',
  revenue DECIMAL(12,2) COMMENT 'Invoiced revenue, USD',
  fulfilment_cost DECIMAL(12,2) COMMENT 'Direct fulfilment cost for the invoiced work, USD'
) COMMENT 'One row per invoice';

INSERT INTO invoices
SELECT concat('IN-', n, '-09-', lpad(i, 2, '0')), n, date_add(DATE'2026-09-02', i * 2), 10000, 7000
FROM (SELECT explode(array('NW-6208', 'NW-3916')) AS n) LATERAL VIEW explode(sequence(1, 10)) e AS i
UNION ALL
SELECT concat('IN-', n, '-10-', lpad(i, 2, '0')), n, date_add(DATE'2026-10-01', i * 2), 10000,
       CASE WHEN i <= 8 THEN 6500 ELSE 7000 END
FROM (SELECT explode(array('NW-6208', 'NW-3916')) AS n) LATERAL VIEW explode(sequence(1, 12)) e AS i;

-- Credits: two rows per credited invoice. Reversal: 4 invoices x 2 x $2,500 = $20,000. Control: 2 x 2 x $1,250 = $5,000.
CREATE OR REPLACE TABLE credits (
  credit_id STRING COMMENT 'Credit note line identifier',
  invoice_id STRING COMMENT 'Invoice the credit reduces. An invoice can have several credit rows',
  credit_date DATE COMMENT 'Date the credit was issued',
  amount DECIMAL(12,2) COMMENT 'Credit amount, USD, positive number',
  reason STRING COMMENT 'Credit reason'
) COMMENT 'One row per credit note line issued against an invoice';

INSERT INTO credits
SELECT concat('CR-', invoice_id, '-', k), invoice_id, date_add(invoice_date, 3), amt,
       CASE k WHEN 1 THEN 'service failure' ELSE 'goodwill' END
FROM (
  SELECT invoice_id, invoice_date, CASE network_id WHEN 'NW-6208' THEN 2500 ELSE 1250 END AS amt
  FROM invoices
  WHERE (network_id = 'NW-6208' AND invoice_id IN ('IN-NW-6208-10-03', 'IN-NW-6208-10-05', 'IN-NW-6208-10-09', 'IN-NW-6208-10-11'))
     OR (network_id = 'NW-3916' AND invoice_id IN ('IN-NW-3916-10-04', 'IN-NW-3916-10-10'))
) LATERAL VIEW explode(array(1, 2)) e AS k;

CREATE OR REPLACE TABLE refund_policies (
  policy_name STRING COMMENT 'Late-delivery refund policy name',
  effective_from DATE COMMENT 'First promised_date the policy covers (inclusive)',
  effective_to DATE COMMENT 'Last promised_date the policy covers (inclusive), NULL when open-ended',
  min_delay_days_exclusive INT COMMENT 'A shipment qualifies only when delay_days is strictly greater than this value',
  excluded_delay_reason STRING COMMENT 'Delay reason that never qualifies for a refund',
  refund_basis STRING COMMENT 'What the customer gets back'
) COMMENT 'Late-delivery refund policies. The policy is selected by the shipment promised_date.';
INSERT INTO refund_policies VALUES
  ('Late refund v1', DATE'2025-01-01', DATE'2026-10-14', 5, 'weather', 'full shipping_fee'),
  ('Late refund v2', DATE'2026-10-15', NULL, 3, 'weather', 'full shipping_fee');

CREATE OR REPLACE TABLE routing_changes (
  network_id STRING COMMENT 'Network that changed routing',
  change_date DATE COMMENT 'Date the routing change went live',
  description STRING COMMENT 'What changed'
) COMMENT 'Log of routing changes. Each change went live for the whole network on one date.';
INSERT INTO routing_changes VALUES
  ('NW-2863', DATE'2026-10-01', 'New hub-sequencing routing for all outbound parcels');
