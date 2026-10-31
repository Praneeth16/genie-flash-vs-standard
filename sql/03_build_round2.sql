-- Round 2. Schema meridian_parcel_r2 = round 1 data plus four traps the agent instructions never mention.
-- Network IDs are opaque. The mapping lives only in runner/answer_key_r2.json.
--   NW-6731 partial month reversal   NW-2290 partial month control
--   NW-9154 duplicate load reversal  NW-4486 duplicate load control
--   NW-3378 test parcels reversal    NW-7712 test parcels control
--   NW-5809 zone-mix complaint rate reversal   NW-1263 zone-mix complaint rate control
-- Run with MERIDIAN_SCHEMA=meridian_parcel_r2 so unqualified names land in the new schema.

CREATE SCHEMA IF NOT EXISTS meridian_parcel_r2;

CREATE OR REPLACE TABLE networks (
  network_id STRING COMMENT 'Distribution network identifier',
  opened_date DATE COMMENT 'Date the network started operating',
  hub_count INT COMMENT 'Number of sorting hubs in the network'
) COMMENT 'One row per Meridian Parcel distribution network';
INSERT INTO networks SELECT * FROM meridian_parcel.networks;
INSERT INTO networks VALUES
  ('NW-6731', DATE'2022-05-02', 2), ('NW-2290', DATE'2020-02-17', 3),
  ('NW-9154', DATE'2023-07-01', 2), ('NW-4486', DATE'2019-10-08', 4),
  ('NW-3378', DATE'2021-11-15', 3), ('NW-7712', DATE'2024-01-22', 1),
  ('NW-5809', DATE'2018-03-05', 5), ('NW-1263', DATE'2022-09-12', 2);

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
  shipping_fee DECIMAL(10,2) COMMENT 'Shipping fee charged to the customer, USD',
  is_test BOOLEAN COMMENT 'TRUE for internal load-test parcels that are not customer shipments',
  load_batch_id STRING COMMENT 'ID of the data load that wrote this row'
) COMMENT 'One row per parcel shipment as loaded from the operations system';
INSERT INTO shipments
SELECT *, FALSE, concat('B-', date_format(ship_date, 'yyyyMM')) FROM meridian_parcel.shipments;

CREATE OR REPLACE TABLE _spec AS
SELECT * FROM VALUES
  -- network, month, zone, n, mean days, days spread over (ship_date = month_start + i % spread), is_test, batch, copies
  -- partial month reversal: Sep 900 over 30 days, Oct 600 over 15 days (data stops 15 Oct)
  ('NW-6731', DATE'2026-09-01', 'local', 900, 4, 30, FALSE, 'B-202609', 1),
  ('NW-6731', DATE'2026-10-01', 'local', 600, 4, 15, FALSE, 'B-202610', 1),
  -- partial month control: Sep 900 over 30 days, Oct 600 over 31 days
  ('NW-2290', DATE'2026-09-01', 'local', 900, 4, 30, FALSE, 'B-202609', 1),
  ('NW-2290', DATE'2026-10-01', 'local', 600, 4, 31, FALSE, 'B-202610', 1),
  -- duplicate load reversal: Oct 1,000 shipments written twice by two loads
  ('NW-9154', DATE'2026-09-01', 'local', 1000, 4, 30, FALSE, 'B-202609', 1),
  ('NW-9154', DATE'2026-10-01', 'local', 1000, 4, 31, FALSE, 'B-202610', 2),
  -- duplicate load control: Oct 2,000 distinct shipments, one load
  ('NW-4486', DATE'2026-09-01', 'local', 1000, 4, 30, FALSE, 'B-202609', 1),
  ('NW-4486', DATE'2026-10-01', 'local', 2000, 4, 31, FALSE, 'B-202610', 1),
  -- test parcels reversal: customer parcels 5.0 -> 5.5 days, plus 1,000 one-day test parcels in Oct
  ('NW-3378', DATE'2026-09-01', 'local', 1000, 5, 30, FALSE, 'B-202609', 1),
  ('NW-3378', DATE'2026-10-01', 'local', 1000, 6, 31, FALSE, 'B-202610', 1),
  ('NW-3378', DATE'2026-10-01', 'local', 1000, 1, 31, TRUE,  'B-202610', 1),
  -- test parcels control: customer parcels 5.0 -> 4.0 days, 100 test parcels in each month
  ('NW-7712', DATE'2026-09-01', 'local', 1000, 5, 30, FALSE, 'B-202609', 1),
  ('NW-7712', DATE'2026-09-01', 'local', 100, 1, 30, TRUE,  'B-202609', 1),
  ('NW-7712', DATE'2026-10-01', 'local', 1000, 4, 31, FALSE, 'B-202610', 1),
  ('NW-7712', DATE'2026-10-01', 'local', 100, 1, 31, TRUE,  'B-202610', 1),
  -- zone-mix complaint rate reversal: mix flips from 80% local to 80% remote
  ('NW-5809', DATE'2026-09-01', 'local', 800, 2, 30, FALSE, 'B-202609', 1),
  ('NW-5809', DATE'2026-09-01', 'remote', 200, 8, 30, FALSE, 'B-202609', 1),
  ('NW-5809', DATE'2026-10-01', 'local', 200, 2, 31, FALSE, 'B-202610', 1),
  ('NW-5809', DATE'2026-10-01', 'remote', 800, 8, 31, FALSE, 'B-202610', 1),
  -- zone-mix complaint rate control: mix stays 80% local
  ('NW-1263', DATE'2026-09-01', 'local', 800, 2, 30, FALSE, 'B-202609', 1),
  ('NW-1263', DATE'2026-09-01', 'remote', 200, 8, 30, FALSE, 'B-202609', 1),
  ('NW-1263', DATE'2026-10-01', 'local', 800, 2, 31, FALSE, 'B-202610', 1),
  ('NW-1263', DATE'2026-10-01', 'remote', 200, 8, 31, FALSE, 'B-202610', 1)
AS t(network_id, month_start, service_zone, n, mean_days, spread, is_test, batch, copies);

-- delivery_days alternates mean-1 / mean+1 when mean >= 2 (5.5 is made of 5 and 6), so means are exact.
-- The promise is generous (mean + 3 days), so none of these parcels is late.
INSERT INTO shipments
SELECT concat('SH-', s.network_id, '-', date_format(s.month_start, 'yyMM'), '-', s.service_zone, CASE WHEN s.is_test THEN '-T' ELSE '' END, '-', lpad(e.i, 4, '0')),
       s.network_id, s.service_zone, date_add(s.month_start, e.i % s.spread),
       date_add(date_add(s.month_start, e.i % s.spread), s.mean_days + 3),
       date_add(date_add(s.month_start, e.i % s.spread), d.days),
       d.days, 0, NULL, CAST(CASE s.service_zone WHEN 'local' THEN 12 ELSE 20 END AS DECIMAL(10,2)),
       s.is_test,
       CASE WHEN c.k = 1 THEN s.batch ELSE concat(s.batch, '-reload') END
FROM _spec s
LATERAL VIEW explode(sequence(1, s.n)) e AS i
LATERAL VIEW explode(sequence(1, s.copies)) c AS k
LATERAL VIEW explode(array(CASE
    WHEN s.network_id = 'NW-3378' AND NOT s.is_test AND s.month_start = DATE'2026-10-01' THEN CASE WHEN e.i % 2 = 0 THEN 5 ELSE 6 END
    WHEN s.mean_days < 2 THEN s.mean_days
    WHEN e.i % 2 = 0 THEN s.mean_days + 1 ELSE s.mean_days - 1 END)) d AS days;

DROP TABLE _spec;

CREATE OR REPLACE TABLE complaints (
  complaint_id STRING COMMENT 'Complaint case identifier',
  network_id STRING COMMENT 'Network the complaint relates to',
  shipment_id STRING COMMENT 'Shipment the complaint is about',
  opened_date DATE COMMENT 'Date the customer opened the complaint',
  category STRING COMMENT 'Complaint category'
) COMMENT 'One row per customer complaint case recorded by support';
INSERT INTO complaints SELECT * FROM meridian_parcel.complaints;

-- Zone-mix complaints. NW-5809: Sep local 16 of 800 (2%), remote 16 of 200 (8%), Oct local 2 of 200 (1%), remote 56 of 800 (7%).
-- NW-1263: Sep local 16 of 800 (2%), remote 16 of 200 (8%), Oct local 24 of 800 (3%), remote 20 of 200 (10%).
INSERT INTO complaints
SELECT concat('CP-', s.network_id, '-', date_format(s.ship_date, 'yyMM'), '-', s.service_zone, '-', lpad(s.rn, 3, '0')),
       s.network_id, s.shipment_id, least(s.delivered_date, last_day(s.ship_date)), 'late delivery'
FROM (
  SELECT sh.*, row_number() OVER (PARTITION BY network_id, trunc(ship_date, 'MM'), service_zone ORDER BY shipment_id) AS rn
  FROM shipments sh WHERE network_id IN ('NW-5809', 'NW-1263')
) s
JOIN VALUES
  ('NW-5809', DATE'2026-09-01', 'local', 16), ('NW-5809', DATE'2026-09-01', 'remote', 16),
  ('NW-5809', DATE'2026-10-01', 'local', 2),  ('NW-5809', DATE'2026-10-01', 'remote', 56),
  ('NW-1263', DATE'2026-09-01', 'local', 16), ('NW-1263', DATE'2026-09-01', 'remote', 16),
  ('NW-1263', DATE'2026-10-01', 'local', 24), ('NW-1263', DATE'2026-10-01', 'remote', 20)
  AS q(network_id, month_start, service_zone, k)
  ON s.network_id = q.network_id AND trunc(s.ship_date, 'MM') = q.month_start AND s.service_zone = q.service_zone
WHERE s.rn <= q.k;

CREATE OR REPLACE TABLE invoices (
  invoice_id STRING COMMENT 'Customer invoice identifier',
  network_id STRING COMMENT 'Network that fulfilled the invoiced work',
  invoice_date DATE COMMENT 'Invoice date. The invoice month is the month of invoice_date',
  revenue DECIMAL(12,2) COMMENT 'Invoiced revenue, USD',
  fulfilment_cost DECIMAL(12,2) COMMENT 'Direct fulfilment cost for the invoiced work, USD'
) COMMENT 'One row per invoice';
INSERT INTO invoices SELECT * FROM meridian_parcel.invoices;

CREATE OR REPLACE TABLE credits (
  credit_id STRING COMMENT 'Credit note line identifier',
  invoice_id STRING COMMENT 'Invoice the credit reduces. An invoice can have several credit rows',
  credit_date DATE COMMENT 'Date the credit was issued',
  amount DECIMAL(12,2) COMMENT 'Credit amount, USD, positive number',
  reason STRING COMMENT 'Credit reason'
) COMMENT 'One row per credit note line issued against an invoice';
INSERT INTO credits SELECT * FROM meridian_parcel.credits;

CREATE OR REPLACE TABLE refund_policies (
  policy_name STRING COMMENT 'Late-delivery refund policy name',
  effective_from DATE COMMENT 'First promised_date the policy covers (inclusive)',
  effective_to DATE COMMENT 'Last promised_date the policy covers (inclusive), NULL when open-ended',
  min_delay_days_exclusive INT COMMENT 'A shipment qualifies only when delay_days is strictly greater than this value',
  excluded_delay_reason STRING COMMENT 'Delay reason that never qualifies for a refund',
  refund_basis STRING COMMENT 'What the customer gets back'
) COMMENT 'Late-delivery refund policies. The policy is selected by the shipment promised_date.';
INSERT INTO refund_policies SELECT * FROM meridian_parcel.refund_policies;

CREATE OR REPLACE TABLE routing_changes (
  network_id STRING COMMENT 'Network that changed routing',
  change_date DATE COMMENT 'Date the routing change went live',
  description STRING COMMENT 'What changed'
) COMMENT 'Log of routing changes. Each change went live for the whole network on one date.';
INSERT INTO routing_changes SELECT * FROM meridian_parcel.routing_changes;
