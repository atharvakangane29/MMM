# Channel Attribution using Markov Chains
The Channel Attribution Model applies Markov Chain–based attribution to quantify the influence of different marketing and engagement channels on an HCP’s likelihood to write a referral. By analyzing real-world sequences of touchpoints (such as Calls, Emails, Speaker Programs, or MSL interactions), the model evaluates how removing each channel affects the probability of an HCP progressing through the conversion journey.

The end result is a clear, data-driven view of **how much each channel contributes** to generating HCP referrals.

---

## Data Ingestion & Schema Strategy
The model utilizes a two-tier data architecture in which firstly raw data with all columns is ingested then the required columns are extracted with proper standardisation.

### 1. Staging (Ingestion)
Raw data must be ingested into dedicated staging schemas. 
* **Schema Naming:** Must be suffixed with **`_test`** (e.g., `dbo_test`, `raw_test`).
* **Table Naming:** Must be suffixed with **`_raw`** (e.g., `users_raw`, `dw_veeva_dbo_call_raw`).

### 2. Production (Cleaned)
The pre-processing tasks (`Task 1` and `Task 2`) read from the staging area and write to the production schemas.
* **Schema Naming:** No suffix (e.g., `dbo`, `raw`).
* **Table Naming:** No suffix (e.g., `users`, `dw_veeva_dbo_call`).

| Data Stage | Schema Example | Table Example | Purpose |
| :--- | :--- | :--- | :--- |
| **Source (Staging)** | `dbo_test` | `profile_raw` | Raw data landing zone |
| **Target (Cleaned)** | `dbo` | `profile` | Consumed by the Attribution Model |

---

## Prerequisites
Before running the project, ensure you have the following access and permissions:

* **Database Access:** You must have read/write access to the **`coe-consultant-catalog`** catalog. Specifically, verify access to the following schemas:
    * **`results`**
    * **`channel_attribution`**

  * You must have `SELECT` (Read) permission on the following tables:

    - `marketing-analytics-catalog`.raw.dw_datasets_centris_speakerprogram
    - `marketing-analytics-catalog`.raw.dw_datasets_centris_speakerprogramattendee
    - `marketing-analytics-catalog`.raw.dw_datasets_centris_speakerprogrambrandtopic
    - `marketing-analytics-catalog`.raw.dw_veeva_dbo_call
    - `marketing-analytics-catalog`.raw.dw_veeva_dbo_calldetail
    - `marketing-analytics-catalog`.raw.dw_veeva_dbo_product
    - `marketing-analytics-catalog`.raw.dw_tableau_dbo_accountallterritories
    - `ext-dw-veeva-catalog_prod`.dbo.users
    - `ext-dw-veeva-catalog_prod`.dbo.profile
    - `marketing-analytics-catalog`.raw.dw_processeddata_dbo_patientactivityhistorydetailed
    - `ext-dw-veeva-catalog_prod`.marketingcloud.individualemailresult
    - `marketing-analytics-catalog`.raw.dw_tableau_marketing_brandsegment
    - `coe-consultant-catalog`.dw.uc_veeva_custom_claims

* **Job Permissions:** Ensure you have "Run" or "Manage" permissions for the Databricks Job linked in the instructions below.

---

### Instructions to Run

#### 1. Repository Setup
1.  **Navigate to the Repository:**
    * Go to Azure DevOps section of UTC.
    * Navigate to the `business_analytics_team` folder.
    * On the left sidebar, click **Repos** and search for `channel_attribution_circulants`.
2.  **Get Clone URL:**
    * Inside the repository, click the **Clone** button (top right corner) and copy the HTTPS URL.
3.  **Clone into Databricks:**
    * Open your Databricks Workspace.
    * Click **Create** → **Git folder**.
    * Paste the copied URL into the dialog box.
    * Name the folder (e.g., `channel_attribution_model`) and click **Create Git folder**.

#### 2. Job Configuration
1.  Navigate to the [Channel Attribution Job](https://adb-7405606517013444.4.azuredatabricks.net/jobs/716602141555532?o=7405606517013444).
2.  **Configure Tasks:** Ensure the job tasks point to the correct files in your Git folder:
    * **Task 1 (`column_filter`):** Points to `Table_Column_Filtering.ipynb`. It reads from schemas (`*_test`) and tables (`*_raw`), selects only the necessary columns, and creates the corresponding tables in clean schemas.
    * **Task 2 (`datatype_conversion`):** Points to `Column_DataType_Change.ipynb`. It casts columns to correct types (Dates, Decimals, etc.) and updates the production schemas.
    * **Task 3 (`claims_notebook`):** Points to the `orchestrator` notebook located inside the `Channel Attribution Model` folder.
    * **Task 4 (`main_code`):** Points to the `main.py` file located inside the `Channel Attribution Model` folder.

#### 3. Execution
1.  To execute the model, click **Run now with different settings**.
2.  **Set Variables:** You will be prompted to enter run-time variables.
    * *Please refer to the **Job Parameters** section of this file for detailed instructions on setting these values.*

#### 4. Outputs
Once the job completes successfully, the following tables will be generated:

* **Master Result Table:** `coe-consultant-catalog.results.channel_attribution_master` (See **Schema of Master Table** section in this file for column details).
* **Intermediate Tables:**
    * `coe-consultant-catalog.channel_attribution.HCP_Longitudinal_Data`
    * `coe-consultant-catalog.channel_attribution.HCP_journeys`

**Important:**

Task Parameters (JSON Mapping): Databricks requires Task Parameters for Python script jobs to be provided as a JSON array of strings. The Job Parameters defined above must be explicitly mapped to command-line arguments using templating.
- This mapping is required for the job to run correctly.
- Do not modify or remove this JSON.
- If it is changed accidentally, replace it exactly with the JSON shown below.

```json
["--start_date","{{job.parameters.start_date}}",
 "--end_date","{{job.parameters.end_date}}",
 "--product","{{job.parameters.product}}",
 "--level","{{job.parameters.level}}",
 "--segment","{{job.parameters.segment}}"]
```

> ### Job Parameters:
> 
> | **Parameter Name** | **Datatype** | **Example** |
> | :--- | :--- | :--- | 
> | **Start Date** | String (YYYY-MM-DD) | 2023-01-01 | 
> | **End Date** | String (YYYY-MM-DD) | 2025-03-31 |
> | **Level** | String (case-insensitive) | Touchpoint Level |  
> | **Product** | String (case-insensitive) or Blank | TYVASO |
> | **Segment** | Integer (from 1-5) | 1 |
> 

* **Start and End Date:**
    * Default values applied if nothing is entered (Default Start Date = '2023-01-01', Default End Date = '2025-03-31').
    * Must match format YYYY-MM-DD.
    * Description: All the Marketing, Referrals, Competitor data will be considered from this **start date** and **end date**, and accordingly **HCP Longitudinal Data** will be prepared. HCP longitudinal data considers HCPs who have atleast one marketing or have written atleast one referral in specified time range (input).

* **Attribution Level:** Decides the granularity at which the attribution model will run.
    * User must enter one from: `Touchpoint Level`, `Channel Level`, `Team Level`.
    * Below is the categorization of each level; 


<div style="margin-left: 60px;">



| **Touchpoint Level** |
|----------------------|
| Sales Team Live Call |
| MDD Live Call        |
| Speaker Programs Live |
| MSL Live Call        |
| Sales Team Virtual Call |
| RNS Live Call        |
| MDD Phone Call       |
| RNS Phone Call       |
| MSL Conference       |
| Speaker Programs Virtual |
| Emails Clicked       |
| MDD Conference       |
| RNS Virtual Call     |
| MDD Virtual Call     |
| MSL Virtual Call     |
| MSL Phone Call       |

| **Channel Level** |
|-------------------|
| Live Call         |
| Virtual Call      |
| Live Spk Pgm      |
| Virtual Spk Pgm   |
| Email             |


| **Team Level** |
|---------------|
| SALES         |
| MDD           |
| SPK PGM       |
| MSL           |
| RNS           |
| EMAIL         |


</div>

<div style="margin-left: 60px;">

- Touchpoint Level to Team Level Mapping:

<table>
  <tr>
    <th><b> Team Level </b></th>
    <th><b> Touchpoints Level </b></th>
  </tr>

  <!-- SALES -->
  <tr>
    <td rowspan="2">SALES</td>
    <td>Sales Team Live Call</td>
  </tr>
  <tr>
    <td>Sales Team Virtual Call</td>
  </tr>

  <!-- MDD -->
  <tr>
    <td rowspan="4">MDD</td>
    <td>MDD Live Call</td>
  </tr>
  <tr>
    <td>MDD Conference</td>
  </tr>
  <tr>
    <td>MDD Virtual Call</td>
  </tr>
  <tr>
    <td>MDD Phone Call</td>
  </tr>

  <!-- RNS -->
  <tr>
    <td rowspan="3">RNS</td>
    <td>RNS Live Call</td>
  </tr>
  <tr>
    <td>RNS Virtual Call</td>
  </tr>
  <tr>
    <td>RNS Phone Call</td>
  </tr>

  <!-- MSL -->
  <tr>
    <td rowspan="4">MSL</td>
    <td>MSL Live Call</td>
  </tr>
  <tr>
    <td>MSL Conference</td>
  </tr>
  <tr>
    <td>MSL Virtual Call</td>
  </tr>
  <tr>
    <td>MSL Phone Call</td>
  </tr>

  <!-- SPK PGM -->
  <tr>
    <td rowspan="2">SPK PGM</td>
    <td>Speaker Programs Live</td>
  </tr>
  <tr>
    <td>Speaker Programs Virtual</td>
  </tr>

  <!-- EMAIL -->
  <tr>
    <td>EMAIL</td>
    <td>Emails Clicked</td>
  </tr>

</table>

- Touchpoint Level to Channel Level Mapping:
<table>
  <tr>
    <th><b> Touchpoints Level </b></th>
    <th><b> Channel Level </b></th>
  </tr>

  <!-- Live Call -->
  <tr>
    <td>Sales Team Live Call</td>
    <td rowspan="6">Live Call</td>
  </tr>
  <tr>
    <td>MDD Live Call</td>
  </tr>
  <tr>
    <td>MSL Live Call</td>
  </tr>
  <tr>
    <td>RNS Live Call</td>
  </tr>
  <tr>
    <td>MSL Conference</td>
  </tr>
  <tr>
    <td>MDD Conference</td>
  </tr>

  <!-- Virtual Call -->
  <tr>
    <td>Sales Team Virtual Call</td>
    <td rowspan="7">Virtual Call</td>
  </tr>
  <tr>
    <td>RNS Virtual Call</td>
  </tr>
  <tr>
    <td>MDD Virtual Call</td>
  </tr>
  <tr>
    <td>MSL Virtual Call</td>
  </tr>
  <tr>
    <td>MDD Phone Call</td>
  </tr>
  <tr>
    <td>RNS Phone Call</td>
  </tr>
  <tr>
    <td>MSL Phone Call</td>
  </tr>

  <!-- Speaker Programs -->
  <tr>
    <td>Speaker Programs Live</td>
    <td>Live Spk Pgm</td>
  </tr>
  <tr>
    <td>Speaker Programs Virtual</td>
    <td>Virtual Spk Pgm</td>
  </tr>

  <!-- Email -->
  <tr>
    <td>Emails Clicked</td>
    <td>Email</td>
  </tr>

</table>

</div>

* **Product Selection:** Product for which the attribution model will run.
    * User should enter one from: `TYVASO`, `REMODULIN`, `ORENITRAM`, `TREPROSTINIL`, `ALL`.
    * If nothing is entered, the code automatically runs for `TREPROSTINIL` only (default value).
    * If entered `ALL`, the code automatically selects all products and runs for each product one by one
    * Description: Determines which product's referral and marketing activity will be analyzed. 
      - If selected **TREPROSTINIL**, then **HCP Longitudinal Data** will contain Referrals of all 3 products and marketing of all 3 products.
      - If selected **TYVASO**, then **HCP Longitudinal Data** will contain Referrals of **TYVASO** and marketing of **TYVASO** and **TREPROSTINIL**, same goes for other products too.

* **Segment Selection:** Considers All HCPs or narrows down the HCP universe to consider for attribution
  * User must enter one from: `1`, `2`, `3`, `4`, `5`.
  * Entering `1` runs for All HCPs.
  * Entering `2` Compares attribution of HCPs across all clusters provided cluster for an HCP exists;

<div style="margin-left: 60px;">

| **Clusters** |
| :--- |
| High Performers |
| Moderate Performers |
| Average Performers |
| Low Performers |
| Near Sleeping |
| Sleeping |
| Unresponsive |

</div>

   - Entering `3` Compares attribution of HCPs writing referrals for **0-2 years** vs **2-10 years** vs **10+ years**;

<div style="margin-left: 60px;">

| **Length of Business (LOB)** |
| :--- |
| 0-2 years |
| 2-10 years |
| 10+ years |

</div>

   - Entering `4` Compares attribution of HCPs who **write direct competitor drug referrals** vs those who **do not**  
    - (Direct Competitor Drugs: Uptravi, Yutrepia, Winrevair):

<div style="margin-left: 60px;">

| **Direct Competitor Drug** |
| :--- |
| Writes |
| Does not Writes |

</div>

   - Entering `5` Compares attribution of HCPs who **write all competitor drug referrals** vs those who **do not** 
    - (All Competitors includes Actemra, Adcirca, Adempas, Alyq, Ambrisentan, Bosentan, Epoprostenol Sodium, Esbriet, Flolan, Letairis,Ofev, Opsumit,Opsynvi, Pirfenidone, Revatio, Sildenafil, Sildenafil Citrate, Tadalafil, Tracleer, Uptravi, Veletri, Ventavis, Winrevair)

<div style="margin-left: 60px;">

| **All Competitor Drug** |
| :--- |
| Writes |
| Does not Writes |

</div>

# Business Rules & Results Table Overview:

### HCP Longitudinal Data:
-  For each run, **HCP longitudinal data** is generated using the specified start and end dates. The output is appended to the table **`coe-consultant-catalog.channel_attribution.hcp_longitudinal_data`**, along with metadata-start date, end date, and run date (timestamp of execution), to support historical tracking.

### HCP Journeys Data:
-  For each run, **HCP Journeys data** is generated, which is appended to the table **`coe-consultant-catalog.channel_attribution.hcp_journeys`**, along with metadata - specific to that run, start date, end date, and run date (timestamp of execution), to support historical tracking.

* **Data Transformation Logic:** The business rules and mappings applied to the raw data to construct the final HCP longitudinal dataset are documented in the following images:


<div style="margin-left: 60px;">
<h3 style="margin: 0;  text-decoration: underline;">Business Filters Applied:</h3>
</div>



<div style="margin-left: 60px;">

### 1. HCP Filters (`marketing-analytics-catalog`.raw.dw_tableau_dbo_accountallterritories)

| **Rule**         | **Condition** |
|--------------|-----------|
| EPLStatusPAH | Valid     |
| IsActive     | 1         |



### 2. Call Filters (tables from schema: `marketing-analytics-catalog`.raw.)

| **Rule**                             | **Condition**                                                                 |
|----------------------------------|---------------------------------------------------------------------------|
| Call_Status                      | Submitted                                                                 |
| Isperson                         | "True"                                                                    |
| Account_id                       | Not Null                                                                  |
| Call_Date                        | Start Date to End Date                                                    |
| De Dup Calls On same day         | 1 call per rep/hcp/day (Based on rules shared)                            |
| Products                         | Excluded 'Non-Promotional'                                                |
| Sales Team                       | Exclude LBE Sales, OS Sales, System Administrator & "ILD Sales NO SS"     |
| Scientific Exchange              | Excluded all irrelevant to Treprostinil/PAH                               |



### 3. Email Filters (`ext-dw-veeva-catalog_prod`.marketingcloud.individualemailresult)

| **Rule**                | **Condition**              |
|---------------------|------------------------|
| et4ae5__DateSent__c | Start Date to End Date  |
| et4ae5__\_\_c       | TRUE                   |



### 4. Speaker Program Filters (tables from schema: `marketing-analytics-catalog`.raw.)

| **Rule**             | **Condition**                                                                 |
|------------------|----------------------------------------------------------------------------|
| Program_status   | Completed                                                                  |
| ProgramStartDate | Start Date to End Date                                                     |
| Attendee_role    | Exclude “Collaborator” OR “Employee Attendee” OR “Speaker”                 |
| Attendance Flag  | “Y”                                                                        |



### 5. Referral Filters (`marketing-analytics-catalog`.raw.dw_processeddata_dbo_patientactivityhistorydetailed)

| **Rule**            | **Condition**             |
|-----------------|------------------------|
| Referral Date   | Start Date to End Date |
| IsValidReferral | TRUE                  |

</div>

<div style="margin-left: 60px;">
<h3 style="margin: 0;  text-decoration: underline;">Business Definitions mapped from Raw columns:</h3>
</div>

<div style="margin-left: 60px;">

#### 1. Event Type Grouping

<table>
  <tr>
    <th><b>Table Name</b></th>
    <th><b>Raw Columns (Program/Interaction Type)</b></th>
    <th><b>Raw Column (Subject (veeva call))</b></th>
    <th><b>Final Column Created (Event Type)</b></th>
  </tr>

  <!-- Speaker Program -->
  <tr>
    <td rowspan="4">Speaker Program</td>
    <td>Live In Office Program, Live Out of Office Program, Support Group Program</td>
    <td>-</td>
    <td>Live</td>
  </tr>
  <tr>
    <td>- Rest</td>
    <td>-</td>
    <td>Virtual</td>
  </tr>
  <tr>
    <td>Conference, Conference/Congress</td>
    <td>-</td>
    <td>Conference</td>
  </tr>
  <tr>
    <td>Phone Call, Email</td>
    <td>-</td>
    <td>Phone Email</td>
  </tr>

  <!-- Veeva Calls -->
  <tr>
    <td rowspan="3">Veeva Calls</td>
    <td>Live Visit, Live/Offsite, Other HCP interaction, MD Interaction, NP/PA Interaction</td>
    <td>Disease State Presentation, Office Call, Presentation, Presentation with Vouchers, Vouchers Discussed – No vouchers left</td>
    <td>Live</td>
  </tr>
  <tr>
    <td>- Rest</td>
    <td>-</td>
    <td>-</td>
  </tr>
  <tr>
    <td>Virtual Meeting, Web Meeting</td>
    <td>Web Meeting</td>
    <td>Virtual</td>
  </tr>
</table>



#### 2. Team Mapping

<table>
  <tr>
    <th><b>Table</b></th>
    <th><b>Raw Column (Team)</b></th>
    <th><b>Final Column Created (Team Map)</b></th>
  </tr>

  <!-- Veeva User -->
  <tr>
    <td rowspan="4">Veeva User</td>
    <td>UT.CPL, UT.MEDICAL AFFAIRS, UT.MSL.ALD, UT.MSL.PH</td>
    <td>MSL</td>
  </tr>
  <tr>
    <td>UT.PAH SALES, UT.PAH SALES – RBD, UT.PAH SALES.RCPS, UT.ILD SALES</td>
    <td>SALES</td>
  </tr>
  <tr>
    <td>UT.PAH MDD</td>
    <td>MDD</td>
  </tr>
  <tr>
    <td>UT.RNS.COM.MGR</td>
    <td>RNS</td>
  </tr>
</table>



#### 3. Product Mapping

<table>
  <tr>
    <th><b>Table Name</b></th>
    <th><b>Raw Column (ProductName (non-MSL calls))</b></th>
    <th><b>Raw Column (Scientific Exchange (MSL calls))</b></th>
    <th><b>Final Column Created (Product Map)</b></th>
  </tr>

  <!-- Spk Program Brand Topic -->
  <tr>
    <td>Spk Program Brand Topic</td>
    <td>Disease State, Connective Tissue Disease</td>
    <td>-</td>
    <td>Treprostinil</td>
  </tr>

  <!-- Veeva Calls -->
  <tr>
    <td rowspan="4">Veeva Calls</td>
    <td>Tyvaso</td>
    <td>Treprostinil DPI, Treprostinil Nebulized</td>
    <td>Tyvaso</td>
  </tr>
  <tr>
    <td>Remodulin</td>
    <td>Remunity, Treprostinil IV, Treprostinil SC</td>
    <td>Remodulin</td>
  </tr>
  <tr>
    <td>Orenitram</td>
    <td>Treprostinil Oral</td>
    <td>Orenitram</td>
  </tr>
  <tr>
    <td>- Rest</td>
    <td>- Rest</td>
    <td>Treprostinil</td>
  </tr>

  <!-- Calls Product Mapping -->
  <tr>
    <td>Calls Product Mapping</td>
    <td>Anything except Tyvaso, Remodulin, Orenitram</td>
    <td>-</td>
    <td>Treprostinil</td>
  </tr>

  <!-- Email -->
  <tr>
    <td>Email</td>
    <td>Anything except Tyvaso, Remodulin, Orenitram</td>
    <td>-</td>
    <td>Treprostinil</td>
  </tr>
</table>

</div>


    
### Look Back Period Table:
-  There is an existing **look_forward_window** table at **`coe-consultant-catalog.channel_attribution.cutoffs`**, which defines the look-forward period for each touchpoint. The current configuration is shown below:

<div style="margin-left: 60px;">

| **Channel** | **Event Type** | **Look Forward Period (in Days)** |
| :--- | :--- | :--- |
| Speaker Program | Live | 180 |
| Speaker Program | Virtual | 180 |
| Call | Live | 60 |
| Call | Conference | 30 |
| Call | PhoneEmail | 30 |
| Call | Virtual | 30 |
| Email | Clicked | 30 |

</div>

<!-- <div style="margin-left: 60px;">

* These values can be updated in this table if cutoff logic changes in the future.

</div> -->
-  These time durations can be updated in this table if look forward logic changes in the future.



### Model Results:

The primary output of the Channel Attribution Model is appended to the **master table:**
`coe-consultant-catalog.results.channel_attribution_master`

* This table stores all historical runs, with **runtime input metadata** (start date, segment, level, etc.) captured to distinguish results.
* The table contains a superset of all possible output columns. Columns not relevant to a specific execution will be populated with `NULL` values.
* Below is the schema of **channel_attribution_master** table;

<div style="margin-left: 60px;">

### Schema of Master table (Final Attribution Output)

| **Column Name** | **Description** |
|------------|-------------|
| run_product | Product which were given at input |
| run_segment | Segment given at the input |
| run_level | Attribution Level given at the input |
| run_start | Start Date given at the input |
| run_end | End Date given at the input |
| run_timestamp | Time Stamp of the run |
| Product | Value will be filled as per selected product |
| Channel | Value will be filled as per selected level |
| Attribution_Pct_High_Performer | Attribution for high performers |
| Attribution_Pct_Moderate_Performer | Attribution for moderate performers |
| Attribution_Pct_Average_Performer | Attribution for average performers |
| Attribution_Pct_Low_Performer | Attribution for low performers |
| Attribution_Pct_Near_Sleeping | Attribution for near sleeping segment |
| Attribution_Pct_Sleeping | Attribution for sleeping segment |
| Attribution_Pct_Unresponsive | Attribution for unresponsive HCPs |
| Attribution_Pct_All_HCPs | Attribution for all HCPs |
| Attribution_Pct_does_not_writes | Attribution for HCPs who do not write competitor products |
| Attribution_Pct_writes | Attribution for HCPs who write competitor products |
| Attribution_Pct_0_2_Years | Attribution for HCPs with 0-2 years in business |
| Attribution_Pct_2_10_Years | Attribution for HCPs with 2-10 years in business |
| Attribution_Pct_10_plus_Years | Attribution for HCPs with 10+ years in business |
| no_of_hcp_High_Performer | Number of High Performer HCPs |
| no_of_hcp_Moderate_Performer | Number of Moderate Performer HCPs |
| no_of_hcp_Average_Performer | Number of Average Performer HCPs |
| no_of_hcp_Low_Performer | Number of Low Performer HCPs |
| no_of_hcp_Near_Sleeping | Number of Near Sleeping HCPs |
| no_of_hcp_Sleeping | Number of Sleeping HCPs |
| no_of_hcp_Unresponsive | Number of Unresponsive HCPs |
| no_of_hcp_All_HCPs | Number of all HCPs |
| no_of_hcp_does_not_writes | HCPs who do not write competitor products |
| no_of_hcp_writes | HCPs who write competitor products |
| no_of_hcp_0_2_Years | HCPs with 0-2 years in business |
| no_of_hcp_2_10_Years | HCPs with 2-10 years in business |
| no_of_hcp_10_plus_Years | HCPs with 10+ years in business |
| total_touchpoints_High_Performer | Total touchpoints for High Performer HCPs |
| total_touchpoints_Moderate_Performer | Total touchpoints for Moderate Performer HCPs |
| total_touchpoints_Average_Performer | Total touchpoints for Average Performer HCPs |
| total_touchpoints_Low_Performer | Total touchpoints for Low Performer HCPs |
| total_touchpoints_Near_Sleeping | Total touchpoints for Near Sleeping HCPs |
| total_touchpoints_Sleeping | Total touchpoints for Sleeping HCPs |
| total_touchpoints_Unresponsive | Total touchpoints for Unresponsive HCPs |
| total_touchpoints_All_HCPs | Total touchpoints for all HCPs |
| total_touchpoints_does_not_writes | Touchpoints for HCPs who do not write competitor products |
| total_touchpoints_writes | Touchpoints for HCPs who write competitor products |
| total_touchpoints_0_2_Years | Touchpoints for HCPs with 0-2 years in business |
| total_touchpoints_2_10_Years | Touchpoints for HCPs with 2-10 years in business |
| total_touchpoints_10_plus_Years | Touchpoints for HCPs with 10+ years in business |
| no_of_prescribers_High_Performer | Prescribers in High Performer segment |
| no_of_prescribers_Moderate_Performer | Prescribers in Moderate Performer segment |
| no_of_prescribers_Average_Performer | Prescribers in Average Performer segment |
| no_of_prescribers_Low_Performer | Prescribers in Low Performer segment |
| no_of_prescribers_Near_Sleeping | Prescribers in Near Sleeping segment |
| no_of_prescribers_Sleeping | Prescribers in Sleeping segment |
| no_of_prescribers_Unresponsive | Prescribers in Unresponsive segment |
| no_of_prescribers_All_HCPs | Total prescribers |
| no_of_prescribers_does_not_writes | Prescribers who do not write competitor products |
| no_of_prescribers_writes | Prescribers who write competitor products |
| no_of_prescribers_0_2_Years | Prescribers with 0-2 years in business |
| no_of_prescribers_2_10_Years | Prescribers with 2-10 years in business |
| no_of_prescribers_10_plus_Years | Prescribers with 10+ years in business |
| total_touchpoints_to_prescribers_High_Performer | Touchpoints to High Performer prescribers |
| total_touchpoints_to_prescribers_Moderate_Performer | Touchpoints to Moderate Performer prescribers |
| total_touchpoints_to_prescribers_Average_Performer | Touchpoints to Average Performer prescribers |
| total_touchpoints_to_prescribers_Low_Performer | Touchpoints to Low Performer prescribers |
| total_touchpoints_to_prescribers_Near_Sleeping | Touchpoints to Near Sleeping prescribers |
| total_touchpoints_to_prescribers_Sleeping | Touchpoints to Sleeping prescribers |
| total_touchpoints_to_prescribers_Unresponsive | Touchpoints to Unresponsive prescribers |
| total_touchpoints_to_prescribers_All_HCPs | Touchpoints to ALL prescribers |
| total_touchpoints_to_prescribers_does_not_writes | Touchpoints to prescribers who do not write competitor drugs |
| total_touchpoints_to_prescribers_writes | Touchpoints to prescribers who write competitor drugs |
| total_touchpoints_to_prescribers_0_2_Years | Touchpoints to prescribers with 0-2 years in business |
| total_touchpoints_to_prescribers_2_10_Years | Touchpoints to prescribers with 2-10 years in business |
| total_touchpoints_to_prescribers_10_plus_Years | Touchpoints to prescribers with 10+ years in business |

</div>

# Repository Structure:

The project directory is organized as follows:

```text
channel-attribution-model/                  # Root directory
├── main.py                                 # Main execution entry point (orchestrates the helper files)
├── _01_input.py                            # Defines Databricks widgets and input parsing
├── _02_data_setup.py                       # Handles initial data loading and configuration (using 'helpers')
├── _03_attribution.py                      # Executes the core transformation and markov calculations (using files in 'helpers')
├── _04_reporting.py                        # Appends final output to master table
├── orchestrator.ipynb                      # Contains competitor pipeline logic
├── helpers/                                # Folder containing sequential steps of the model workflow
│   ├── __init__.py                          
│   ├── _00_data_prep.py                    # Prepares the initial raw HCP longitudinal data for start and end date given
│   ├── _01_scenario_filter.py              # Filters the HCP longitudinal data based on scenario inputs (product, segment)
│   ├── _02_data_filter.py                  # Filters the data by removing post last referral events per HCP
│   ├── _03_cutoff.py                       # Applies the look-back period to retain relevant touchpoints for each conversion
│   ├── _04_reorder.py                      # Assigns new serial no for reordering
│   ├── _05_preprocess.py                   # Cleans the data (takes care of duplicates etc)
│   ├── _06_impression_conversion.py        # Marks events as impression or conversion
│   ├── _07_journey.py                      # Pivots up the data 
│   ├── _08_base_probability.py             # Calculates the base conversion rate and metrices
│   ├── _09_transition_probability.py       # Calculates the transition matrix
│   ├── _10_removal_effect.py               # Calculates channel 
│   └── _11_result.py                       # Result formatting                      
└── README.md                               # Project documentation providing an overview, setup instructions, parameters, logic, and file structure for the Channel Attribution Model
```

# Markov Model Working:

The channel attribution score is calculated using the Multi-Channel Markov Model, which determines channel contribution by measuring the drop in conversion probability when a channel is removed (the **Removal Effect**).

>The workflow proceeds in five core steps:

1. _Baseline conversion probability:_ Compute the probability that an observed journey ends in conversion (absorption).

2.  _Transition Probability Estimation (A → B):_ The model first analyzes all observed journeys to estimate the counts and then the probabilities of moving from one marketing touchpoint (**Channel A**) to the next (**Channel B**). This step forms the **Markov Transition Matrix**.

3.  _Channel Exclusion:_ For each channel, journeys are conceptually rebuilt after removing that channel entirely, and a new conversion probability is recomputed with the channel excluded.

4.  _Contribution Normalization:_ The impact of each channel exclusion is measured. These impacts are then **normalized** to derive final channel attribution percentages that sum to 100%.


# Tables Used:  

<div style="margin-left: 60px;">

| **Sr. No.** | **Table Name**                         | **Description** |
|------------:|----------------------------------------|-----------------|
| 1 | `marketing-analytics-catalog`.raw.dw_datasets_centris_speakerprogram | To get Speaker Program details (Completed etc.) |
| 2 | `marketing-analytics-catalog`.raw.dw_datasets_centris_speakerprogramattendee | To get Attendee details (AttendeeRole, Attendance Flag) |
| 3 | `marketing-analytics-catalog`.raw.dw_datasets_centris_speakerprogrambrandtopic | To get details of Product discussed in speaker program |
| 4 | `marketing-analytics-catalog`.raw.dw_veeva_dbo_call | To get all the call related details (Call date, call type, call subject etc.) |
| 5 | `marketing-analytics-catalog`.raw.dw_veeva_dbo_calldetail | To get priority details of product discussed in call |
| 6 | `marketing-analytics-catalog`.raw.dw_veeva_dbo_product | To get details of Product discussed in a call |
| 7 | `marketing-analytics-catalog`.raw.dw_tableau_dbo_accountallterritories | To get only the valid HCP accounts, NPI, NPI Speciality |
| 8 | `ext-dw-veeva-catalog_prod`.dbo.users | To join with profile table to get team name |
| 9 | `ext-dw-veeva-catalog_prod`.dbo.profile | To get name of team of calling rep |
| 10 | `marketing-analytics-catalog`.raw.dw_processeddata_dbo_patientactivityhistorydetailed | To get all valid referrals |
| 11 | `ext-dw-veeva-catalog_prod`.marketingcloud.individualemailresult | To get email campaign data |
| 12 | `marketing-analytics-catalog`.raw.dw_tableau_marketing_brandsegment | To get HCP Clustername and NPI |
| 13 | `coe-consultant-catalog`.dw.uc_veeva_custom_claims | To get competitor data for HCPs |

</div>
