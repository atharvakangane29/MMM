# DATA_SCHEMA.md — Delta Lake Tables & Column Glossary

## UTC Channel Attribution MMM Platform

All tables live in the Databricks Unity Catalog under:
```
Catalog: hive_metastore
Schema:  utc_attribution
```

---

## Table Index

| Table | Rows (approx.) | Description |
|---|---|---|
| `mmm_scenario_results` | Grows ~377 rows per run | Primary output table — one row per channel per scenario |
| `raw_scenario_inputs` | 1 row per scenario run | Scenario parameters + job tracking |
| `hcp360_universe` | ~13,000 HCPs | HCP master table with all attributes |
| `hcp_longitudinal_journey` | Millions | Ordered touchpoint sequence per HCP |

---

## Table 1: `mmm_scenario_results`

The **central output table**. Every scenario run appends rows here. Identified by `scenario_id`. The frontend reads this table exclusively for chart rendering.

### Scenario Identity Columns

| Column | Type | Example | Description |
|---|---|---|---|
| `scenario_id` | STRING | `3fa85f64-5717-...` | UUID identifying the scenario run |
| `run_product` | STRING | `REMODULIN` | Product parameter used for this run |
| `run_segment` | STRING | `Cluster Level` | HCP segment filter used |
| `run_level` | STRING | `Touchpoint Level` | Attribution granularity used |
| `run_start` | DATE | `2023-01-01` | Observation window start |
| `run_end` | DATE | `2025-03-31` | Observation window end |
| `run_timestamp` | TIMESTAMP | `2026-01-17 14:05:34` | When the model completed |

### Channel Identity Columns

| Column | Type | Example | Description |
|---|---|---|---|
| `Product` | STRING | `REMODULIN` | Product being attributed (may differ from `run_product` for ALL runs) |
| `Channel` | STRING | `SALES_Live_Call` | The marketing channel / touchpoint / team being described |

### Attribution Percentage Columns (by Cluster Segment)

Each value is a float (0.0–1.0) representing the Markov-chain attribution share for that channel within that segment.

| Column | Segment Description |
|---|---|
| `Attribution_Pct_High_Performer` | HCPs in the "High Performer" prescribing cluster |
| `Attribution_Pct_Moderate_Performer` | HCPs in the "Moderate Performer" cluster |
| `Attribution_Pct_Average_Performer` | HCPs in the "Average Performer" cluster |
| `Attribution_Pct_Low_Performer` | HCPs in the "Low Performer" cluster |
| `Attribution_Pct_Near_Sleeping` | HCPs with low recent engagement |
| `Attribution_Pct_Sleeping` | HCPs with very low recent engagement |
| `Attribution_Pct_Unresponsive` | HCPs with near-zero engagement |
| `Attribution_Pct_All_HCPs` | Entire HCP universe (no segment filter) |

### Attribution Percentage Columns (by Competitor Drug)

| Column | Description |
|---|---|
| `Attribution_Pct_does_not_writes` | HCPs who do NOT prescribe competitor drugs |
| `Attribution_Pct_writes` | HCPs who DO prescribe competitor drugs (Yutrepia, Uptravi, Winrevair) |

### Attribution Percentage Columns (by Length of Business)

| Column | Description |
|---|---|
| `Attribution_Pct_0_2_Years` | HCPs with 0–2 years since first referral |
| `Attribution_Pct_2_10_Years` | HCPs with 2–10 years since first referral |
| `Attribution_Pct_10_plus_Years` | HCPs with 10+ years since first referral |

### HCP Count Columns (number of unique HCPs reached by this channel)

Same segmentation pattern as attribution %. Prefix: `no_of_hcp_`

| Column | Description |
|---|---|
| `no_of_hcp_High_Performer` | Count of High Performer HCPs reached by this channel |
| `no_of_hcp_Moderate_Performer` | ... |
| `no_of_hcp_Average_Performer` | ... |
| `no_of_hcp_Low_Performer` | ... |
| `no_of_hcp_Near_Sleeping` | ... |
| `no_of_hcp_Sleeping` | ... |
| `no_of_hcp_Unresponsive` | ... |
| `no_of_hcp_All_HCPs` | Total unique HCPs reached |
| `no_of_hcp_does_not_writes` | HCPs not writing competitor, reached by this channel |
| `no_of_hcp_writes` | HCPs writing competitor, reached by this channel |
| `no_of_hcp_0_2_Years` | HCPs with LOB 0–2 years, reached |
| `no_of_hcp_2_10_Years` | HCPs with LOB 2–10 years, reached |
| `no_of_hcp_10_plus_Years` | HCPs with LOB 10+ years, reached |

### Total Touchpoints Columns (volume of interactions)

Same pattern as above. Prefix: `total_touchpoints_`

Counts the total number of individual touchpoint events delivered by this channel to HCPs in each segment.

| Column | Description |
|---|---|
| `total_touchpoints_High_Performer` | Sum of touchpoints to High Performer HCPs |
| `total_touchpoints_[segment]` | Same pattern for all other segments |
| `total_touchpoints_All_HCPs` | Total touchpoints across all HCPs |

### Prescriber Count Columns (HCPs who wrote a referral)

Counts only the HCPs in each segment who **actually wrote a referral** (i.e., converted). Prefix: `no_of_prescribers_`

| Column | Description |
|---|---|
| `no_of_prescribers_High_Performer` | Count of prescribers in High Performer segment |
| `no_of_prescribers_[segment]` | Same pattern for all segments |
| `no_of_prescribers_All_HCPs` | Total prescribers across universe |

### Touchpoints-to-Prescribers Columns (efficiency metric)

Touchpoint volume delivered specifically to HCPs who eventually converted. Prefix: `total_touchpoints_to_prescribers_`

This is an **efficiency signal** — high value means this channel spent many touchpoints on eventual converters.

| Column | Description |
|---|---|
| `total_touchpoints_to_prescribers_High_Performer` | Touchpoints to eventual High Performer prescribers |
| `total_touchpoints_to_prescribers_[segment]` | Same pattern |
| `total_touchpoints_to_prescribers_All_HCPs` | Total touchpoints to all eventual prescribers |

### Null Values
Columns contain `"null"` (string) when a segment was not part of the `run_segment` configuration for that scenario. For example, a run configured with `Cluster Level` will have `Attribution_Pct_0_2_Years = "null"`.

---

## Table 2: `raw_scenario_inputs`

Tracks every scenario submission. Written by FastAPI when a run is created; updated as job status changes.

| Column | Type | Description |
|---|---|---|
| `scenario_id` | STRING | UUID (PK) |
| `scenario_name` | STRING | Analyst-given name |
| `product` | STRING | Input product parameter |
| `start_date` | DATE | Input start date |
| `end_date` | DATE | Input end date |
| `attribution_level` | STRING | `touchpoint`, `channel`, or `team` |
| `hcp_segment` | STRING | `cluster`, `lob`, `competitor_drug`, or `all_hcps` |
| `status` | STRING | `QUEUED`, `RUNNING`, `SUCCESS`, `FAILED` |
| `databricks_run_id` | LONG | Databricks Jobs API run ID |
| `created_at` | TIMESTAMP | When the scenario was submitted |
| `completed_at` | TIMESTAMP | When the job finished (null until complete) |
| `error_message` | STRING | Databricks error detail if FAILED |
| `notes` | STRING | Free-text analyst notes |
| `is_deleted` | BOOLEAN | Soft-delete flag |
| `params_json` | STRING | Full parameters as JSON string (for audit) |

---

## Table 3: `hcp360_universe`

Master HCP table. Rebuilt periodically (not per scenario run). Used by the Markov model as the HCP filter.

### Identity

| Column | Description |
|---|---|
| `HCP_ID` | Internal UTC HCP identifier |
| `NPI` | National Provider Identifier |
| `Account_Name` | HCP full name |
| `Specialty` | Medical specialty |
| `Institution` | Affiliated hospital / practice |
| `Territory` | Sales territory code |

### Segmentation

| Column | Description |
|---|---|
| `Segment_Tyvaso` | Cluster segment for TYVASO (`high performer`, `moderate performer`, `average performer`, `low performer`, `near sleeping`, `sleeping`, `unresponsive`) |
| `Segment_Orenitram` | Cluster segment for ORENITRAM |
| `Segment_Remodulin` | Cluster segment for REMODULIN |
| `Segment_Treprostinil` | Overall treprostinil cluster (derived: highest priority across products) |
| `LOB_Category` | Length of Business: `0-2 Years`, `2-10 Years`, `10+ Years` |
| `Competitor_Flag` | Boolean — whether HCP writes Yutrepia, Uptravi, or Winrevair |

### Referral Activity

| Column | Description |
|---|---|
| `Total_Referrals` | All referrals written by HCP (lifetime) |
| `Referrals_Tyvaso` | Referrals for TYVASO |
| `Referrals_Orenitram` | Referrals for ORENITRAM |
| `Referrals_Remodulin` | Referrals for REMODULIN |
| `Earliest_Referral_Date` | Date of first ever referral |
| `Latest_Referral_Date` | Date of most recent referral |
| `Referrals_Pre_Obs_Period` | Referrals written before the observation window |

### Call Activity

| Column | Description |
|---|---|
| `Veeva_Detailing_SalesTeam` | Count of SALES team calls received |
| `Veeva_Detailing_MDDTeam` | Count of MDD team calls received |
| `Veeva_Detailing_MSLTeam` | Count of MSL team calls received |
| `Veeva_Detailing_RNSTeam` | Count of RNS team calls received |

### Speaker Program

| Column | Description |
|---|---|
| `Role_Speaker` | Flag: HCP has been a speaker |
| `Role_Attendee` | Flag: HCP has attended a speaker program |
| `Role_NonReportableHCP` | Flag: HCP is non-reportable |

---

## Table 4: `hcp_longitudinal_journey`

Ordered sequence of all marketing touchpoints per HCP over time. The input to the Markov chain model.

| Column | Type | Description |
|---|---|---|
| `hcp_id` | STRING | HCP identifier |
| `touchpoint_date` | DATE | Date of the interaction |
| `touchpoint_type` | STRING | Derived interaction type (VIRTUAL, LIVE, PHONE_EMAIL, CONFERENCE, etc.) |
| `channel` | STRING | Specific channel (e.g., `MDD_Live_Call`) |
| `team` | STRING | Team responsible (SALES, MDD, MSL, RNS, SPK PGM, EMAIL) |
| `product` | STRING | Product discussed |
| `interaction_category` | STRING | High-level category |
| `source_table` | STRING | Origin (veeva_calls, speaker_program, email_marketing) |

---

## Channel Reference

All possible `Channel` values in `mmm_scenario_results`:

### Touchpoint Level
| Channel Value | Team | Modality |
|---|---|---|
| `SALES_Live_Call` | SALES | Live |
| `SALES_Virtual_Call` | SALES | Virtual |
| `MDD_Live_Call` | MDD | Live |
| `MDD_Virtual_Call` | MDD | Virtual |
| `MDD_PhoneEmail_Call` | MDD | Phone/Email |
| `MDD_Conference_Call` | MDD | Conference |
| `MSL_Live_Call` | MSL | Live |
| `MSL_Virtual_Call` | MSL | Virtual |
| `MSL_PhoneEmail_Call` | MSL | Phone/Email |
| `MSL_Conference_Call` | MSL | Conference |
| `RNS_Live_Call` | RNS | Live |
| `RNS_Virtual_Call` | RNS | Virtual |
| `RNS_PhoneEmail_Call` | RNS | Phone/Email |
| `Speaker Program_Live` | SPK PGM | Live |
| `Speaker Program_Virtual` | SPK PGM | Virtual |
| `Email_Clicked` | EMAIL | Email |

### Channel Level
| Channel Value | Description |
|---|---|
| `Live Call` | All live in-person calls (all teams) |
| `Virtual Call` | All virtual/web calls (all teams) |
| `Live Spk Pgm` | Live speaker programs |
| `Virtual Spk Pgm` | Virtual speaker programs |
| `Email` | Email clicked interactions |

### Team Level
| Channel Value | Description |
|---|---|
| `SALES` | Field sales team |
| `MDD` | Medical District Directors |
| `MSL` | Medical Science Liaisons |
| `RNS` | Reimbursement Navigation Specialists |
| `SPK PGM` | Speaker Programs |
| `EMAIL` | Email marketing |

---

## HCP Segment Reference

### Cluster Segments (by prescribing performance)

| Segment | Business Definition |
|---|---|
| `High Performer` | Top-tier prescribers; high referral volume, high recency |
| `Moderate Performer` | Above-average prescribers |
| `Average Performer` | Mid-tier prescribers |
| `Low Performer` | Below-average prescribers |
| `Near Sleeping` | Historically active but declining |
| `Sleeping` | Little to no recent activity |
| `Unresponsive` | No response to marketing touchpoints |

### Length of Business (LOB)
Time between HCP's first and latest referral across their lifetime.

| Segment | Definition |
|---|---|
| `0–2 Years` | New prescribers |
| `2–10 Years` | Established prescribers |
| `10+ Years` | Long-term prescribers |

### Competitor Drug
| Segment | Competitor Drugs |
|---|---|
| `Writes Competitor` | Prescribes Yutrepia, Uptravi, or Winrevair |
| `Does Not Write Competitor` | Has not prescribed any competitor drug |
