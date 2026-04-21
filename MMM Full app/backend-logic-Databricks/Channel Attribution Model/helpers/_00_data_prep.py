
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import ( col, when, trim, upper, lower, lit, concat, concat_ws, to_date, date_format, regexp_replace, least, array_join, array_distinct, collect_list, coalesce, max as spark_max, min as spark_min, row_number, expr, datediff, floor, months_between, add_months, lead, lag, struct, element_at, array, sum as spark_sum, countDistinct)
from pyspark.sql.window import Window
import warnings

warnings.filterwarnings("ignore")

############################################################################# EMAIL DATA #####################################################################################

def build_email_data(spark, start_date="2023-01-01", end_date="2025-03-31"):
    """
    Build the Emails DataFrame.
    """ 

    em = spark.table("`ext-dw-veeva-catalog_prod`.marketingcloud_test.individualemailresult").alias('em')
    aat = spark.table("`marketing-analytics-catalog`.raw_test.dw_tableau_dbo_accountallterritories").alias('aat')

    df = (
            em.join(aat, col('em.Person_Account_Id__c') == col('aat.AccountID'), "left")
            .where(
                    (to_date(col("em.et4ae5__DateSent__c")).between(start_date, end_date)) & 
                    (col("em.et4ae5__Clicked__c") == True) &
                    (col("aat.IsActive") == True) &
                    (col("aat.EPLstatusPAH").like("Valid%")) &
                    (col("aat.IsPersonAccount") == True)
                )
                .select(
                        col("em.id").alias("event_id"),
                        lit(None).alias('rep_id'),
                        lit(None).alias('rep_name'),
                        lit(None).alias('rep_email'),
                        lit(None).alias('team_raw'),
                        col("em.et4ae5__TriggeredSendDefinition__c").alias("marketing_id"),
                        col("em.Person_Account_Id__c").alias("hcp_id"),
                        lit("Email").alias("event_channel"),
                        lit("Clicked").alias("event_type"),
                        to_date(col("em.et4ae5__DateSent__c")).alias("event_date"),
                        col("em.et4ae5__DateSent__c").alias("event_timestamp"),
                        lit(None).alias("team"),
                        concat(lit("Email"), lit("_"), lit("Clicked")).alias("det_touchpoint"),
                        when(lower(col("em.et4ae5__FromName__c")) == "orenitram", "ORENITRAM")
                        .when(lower(col("em.et4ae5__FromName__c")) == "remodulin", "REMODULIN")
                        .when(lower(col("em.et4ae5__FromName__c")) == "tyvaso", "TYVASO")
                        .otherwise("TREPROSTINIL")
                        .alias("product_name")
                        )
            )
    
    return df

########################################################################### REFERRALS #################################################

def build_referrals_data(spark, start_date='2023-01-01', end_date='2025-03-31'):
    """
    Build the Referrals DataFrame.
    """ 

    rf = spark.table('`marketing-analytics-catalog`.raw_test.dw_processeddata_dbo_patientactivityhistorydetailed').alias('rf')
    aat = spark.table('`marketing-analytics-catalog`.raw_test.dw_tableau_dbo_accountallterritories').alias('aat')

    df = (
            rf.join(aat, col('rf.ReferralPrescriberAccountID') == col('aat.AccountID'), 'left')
            .where(
                        (col('rf.ReferralDate').between(start_date, end_date)) &
                        (col('rf.IsValidReferral') == True) &
                        (col('aat.EPLstatusPAH').like('Valid%')) &
                        (col('aat.IsActive') == True) &
                        (col('aat.IsPersonAccount') == True)
                    )
            .select(
                        col('rf.PatientSequence').alias('event_id'),
                        lit(None).alias('rep_id'),
                        lit(None).alias('rep_name'),
                        lit(None).alias('rep_email'),
                        lit(None).alias('team_raw'),
                        col('rf.PatientID').alias('marketing_id'),
                        col('rf.ReferralPrescriberAccountID').alias('hcp_id'),
                        lit('Referral').alias('event_channel'),
                        lit('Referral').alias('event_type'),
                        to_date(col('rf.ReferralDate')).alias('event_date'),
                        col('rf.ReferralDate').alias('event_timestamp'),
                        lit(None).alias('team'),
                        lit(None).alias('det_touchpoint'),
                        col('rf.Brand').alias('product_name')
                    )
          )
                                                    
    return df

####################################################################### SPEAKER PROGRAM ################################################

def build_speaker_program_data(spark, start_date='2023-01-01', end_date='2025-03-31'):
    """
    Build the Speaker Program DataFrame.
    """ 

    spk = spark.table('`marketing-analytics-catalog`.raw_test.dw_datasets_centris_speakerprogram').alias('spk')
    att = spark.table('`marketing-analytics-catalog`.raw_test.dw_datasets_centris_speakerprogramattendee').alias('att')
    aat = spark.table('`marketing-analytics-catalog`.raw_test.dw_tableau_dbo_accountallterritories').alias('aat')
    spbt = spark.table('`marketing-analytics-catalog`.raw_test.dw_datasets_centris_speakerprogrambrandtopic').alias('spbt')

    df = (
            spk.join(att, col('spk.ProgramID') == col('att.ProgramID'), 'left')
            .join(aat, col('att.UTCustomerID') == col('aat.AccountID'), 'left')
            .join(spbt, col('spk.ProgramID') == col('spbt.ProgramID'), 'left')
            .where(
                    (col('spk.ProgramStatus').like('Completed%')) &
                    (to_date(col('spk.ProgramStartDateTime')).between(start_date, end_date)) &
                    (col('aat.Isactive') == True) &
                    (col('aat.IsPersonAccount') == True) &
                    (col('aat.EPLstatusPAH').like('Valid%')) &
                    (col('att.AttendeeRole').isin('Speaker', 'Attendee', 'Non-Reportable HCP')) &
                    (
                      upper(col("spbt.ProductName")).like("%TYVASO%") |
                      upper(col("spbt.ProductName")).like("%REMODULIN%") |
                      upper(col("spbt.ProductName")).like("%ORENITRAM%") |
                      upper(col("spbt.ProductName")).like("%DISEASE STATE%") |
                      upper(col("spbt.ProductName")).like("%CONNECTIVE%")
                    )

                  )
                    .select(
                                col('att.AttendanceID').alias('event_id'),
                                col('spk.ProgramID').alias('marketing_id'),
                                col('att.UTCustomerID').alias('hcp_id'),
                                to_date(col('ProgramStartDateTime')).alias('event_date'),
                                col('ProgramStartDateTime').alias('event_timestamp'),
                                lit(None).alias('team'),
                                lit('Speaker Program').alias('event_channel'),
                                when(col('spk.ProgramType').isin('Live In Office Program','Live Out of Office Program','Support Group Program'), 'Live')
                                .otherwise('Virtual')
                                .alias('event_type'),
                                when(upper(col('spbt.ProductName')).like('%TYVASO%'), 'TYVASO')
                                .when(upper(col('spbt.ProductName')) == 'ORENITRAM', 'ORENITRAM')
                                .when(upper(col('spbt.ProductName')) == 'REMODULIN', 'REMODULIN')
                                .when(upper(col('spbt.ProductName')).like('%DISEASE STATE%'), 'TREPROSTINIL')
                                .when(upper(col('spbt.ProductName')).like('%CONNECTIVE%'), 'TREPROSTINIL')
                                .otherwise(lit(None))
                                .alias('ProductName_grp'),
                                when(col('ProductName_grp') == 'TYVASO', 'TYVASO').otherwise(lit(None)).alias('tyvaso_flag'),
                                when(col('ProductName_grp') == 'ORENITRAM', 'ORENITRAM').otherwise(lit(None)).alias('orenitram_flag'),
                                when(col('ProductName_grp') == 'REMODULIN', 'REMODULIN').otherwise(lit(None)).alias('remodulin_flag'),
                                when(col('ProductName_grp') == 'TREPROSTINIL', 'TREPROSTINIL').otherwise(lit(None)).alias('treprostnil_flag'),
                                concat_ws(", ", col('tyvaso_flag'), col('orenitram_flag'), col('remodulin_flag'), col('treprostnil_flag')).alias('product_name'),
                                concat_ws("_", col('event_channel'), col('event_type')).alias('det_touchpoint')
                            )
                )
    
    df = df.select(
                    "event_id",
                    lit(None).alias('rep_id'),
                    lit(None).alias('rep_name'),
                    lit(None).alias('rep_email'),
                    lit(None).alias('team_raw'),
                    "marketing_id",
                    "hcp_id",
                    "event_channel",
                    "event_type",
                    "event_date",
                    "event_timestamp",
                    "team",
                    "det_touchpoint",
                    "product_name"
                  )
    return df

##################################################################### CALLS ###############################################################

def build_calls_data(spark, start_date='2023-01-01', end_date='2025-03-31'):
    """
    Build the Calls DataFrame.
    """ 

    calls = spark.table('`marketing-analytics-catalog`.raw_test.dw_veeva_dbo_call').alias('calls')
    terr = spark.table('`marketing-analytics-catalog`.raw_test.dw_tableau_dbo_accountallterritories').alias('terr')
    det = spark.table('`marketing-analytics-catalog`.raw_test.dw_veeva_dbo_calldetail').alias('det')
    prod = spark.table('`marketing-analytics-catalog`.raw_test.dw_veeva_dbo_product').alias('prod')
    us = spark.table('`ext-dw-veeva-catalog_prod`.dbo_test.users').alias('us')
    prof = spark.table('`ext-dw-veeva-catalog_prod`.dbo_test.profile').alias('prof')

    calls_filtered_df = (
                            calls.join(terr, col('calls.Account_vod__c') == col('terr.AccountID'), how = 'left')
                            .where(
                                    (upper(col('calls.Status_vod__c')).like('%SUBMITTED%')) &
                                    (to_date(col('calls.Call_Date_vod__c')).between(start_date, end_date)) &
                                    (col('calls.Account_vod__c').isNotNull()) &
                                    (col('terr.isPersonAccount') == True) &
                                    (upper(col('terr.EPLstatusPAH')) == 'VALID') &
                                    (col('terr.IsActive') == True)
                                    
                                  )
                            .select(
                                     col('calls.id').alias('call_id'),
                                     col('calls.Account_vod__c').alias('account_id'),
                                     col('calls.Call_Date_vod__c').alias('call_date'),
                                     col('calls.ownerid').alias('rep_id'),
                                     col('calls.Call_Datetime_vod__c').alias('call_timestamp'),
                                     when(col('calls.Interaction_Type__c').isin('CONFERENCE', 'CONFERENCE/CONGRESS'), 'Conference')
                                    .when(col('calls.Interaction_Type__c').isin('PHONE CALL', 'EMAIL'), 'PhoneEmail')
                                    .when(col('calls.Interaction_Type__c').isin('LIVE VISIT', 'LIVE/OFFSITE', 'LIVE/ONSITE', 'OTHER HCP INTERACTION', 'MD INTERACTION', 'NP/PA INTERACTION'), 'Live')
                                    .when(col('calls.Interaction_Type__c').isin('VIRTUAL MEETING', 'WEB MEETING'), 'Virtual')
                                    .when(
                                            (col('calls.Interaction_Type__c').isNull() | (trim(col('calls.Interaction_Type__c')) == '')) &
                                            col('calls.Subject_vod__c').isin('DISEASE STATE PRESENTATION', 'OFFICE CALL', 'PRESENTATION WITH VOUCHERS', 'VOUCHERS DISCUSSED - NO VOUCHERS LEFT'),
                                            'Live'
                                         )
                                    .when(
                                            (col('calls.Interaction_Type__c').isNull() | (trim(col('calls.Interaction_Type__c')) == '')) &
                                            col('calls.Subject_vod__c').isin('PRESENTATION'),
                                            'Live'
                                         )
                                    .when(
                                            (col('calls.Interaction_Type__c').isNull() | (trim(col('calls.Interaction_Type__c')) == '')) &
                                            col('calls.Subject_vod__c').isin('WEB MEETING'),
                                            'Virtual'
                                         )
                                    # .otherwise('Null')
                                    .otherwise(None)
                                    .alias('event_type'),
                                    when(col('calls.Subject_vod__c').isin('OFFICE CALL'), 1)
                                    .when(col('calls.Subject_vod__c').isin('DISEASE STATE PRESENTATION', 'PRESENTATION', 'PRESENTATION WITH VOUCHERS', 'VOUCHERS DISCUSSED - NO VOUCHERS LEFT'), 2)
                                    .when(col('calls.Subject_vod__c').isin('WEB MEETING'), 3)
                                    .otherwise(4)
                                    .alias('Subject_Priority'),
                                    when(col('calls.Interaction_Type__c').isin('LIVE VISIT', 'LIVE/OFFSITE', 'LIVE/ONSITE', 'OTHER HCP INTERACTION', 'MD INTERACTION', 'NP/PA INTERACTION'), 1)
                                    .when(col('calls.Interaction_Type__c').isin('VIRTUAL MEETING', 'WEB MEETING'), 2)
                                    .when(col('calls.Interaction_Type__c').isin('CONFERENCE', 'CONFERENCE/CONGRESS'), 3)
                                    .when(col('calls.Interaction_Type__c').isin('PHONE CALL', 'EMAIL'), 4)
                                    .otherwise(5)
                                    .alias('Interaction_Priority'),
                                    col('calls.Scientific_Exchange__c').alias('sci_product_raw'),
                                    col('calls.CreatedDate')
                                  )
                        )

    df1 = calls_filtered_df.alias('df1')
    
    w = Window.partitionBy(col('df1.account_id'), col('df1.rep_id'), to_date(col('df1.call_date'))).orderBy(col('df1.Subject_Priority').asc(), col('df1.Interaction_Priority').asc(), col('df1.CreatedDate').desc())

    calls_filtered_df = df1.withColumn('row_number', row_number().over(w)).where(col('row_number') == 1).drop('row_number', 'CreatedDate')
    df2 = calls_filtered_df.alias('df2')

    calls_with_products_teams_sci_df = (
                                          df2.join(det, col('df2.call_id') == col('det.Call2_vod__c'), how = 'left')
                                             .join(prod, col('det.Product_vod__c') == col('prod.ID'), how = 'left')
                                             .join(us, col('df2.rep_id') == col('us.X18_Digit_User_ID__c'), how = 'left')
                                             .join(prof, col('prof.Id') == col('us.ProfileID'), how = 'left')
                                            .where(
                                                    (
                                                        (
                                                            (col('det.Product_vod__c').isNotNull()) &
                                                            (~upper(col('prof.Name')).isin('UT.LBE SALES', 'UT.OS SALES', 'UT.ILD SALES NO SS', 'SYSTEM ADMINISTRATOR')) &
                                                            (~col('prod.Name').isin('NON-PROMOTIONAL'))
                                                        )
                                                        |
                                                        (
                                                            (col('prod.Name').isNull()) &
                                                            (~upper(col('prof.Name')).isin('UT.LBE SALES', 'UT.OS SALES', 'UT.ILD SALES NO SS', 'SYSTEM ADMINISTRATOR'))
                                                        )
                                                    )
                                                    &
                                                    (upper(col('prof.Name')) != 'UT.TRAINING')
                                                )
                                             .select(
                                                        col('df2.*'),
                                                        col('us.Name').alias('Rep_Name'),                   
                                                        col('us.email').alias('rep_email'),                  
                                                        col('det.Detail_Priority_vod__c').alias('product_detail_priority'),
                                                        col('prod.Name').alias('product_raw'),
                                                        col('prof.Name').alias('team_raw'),
                                                        when(upper(col('prod.Name')).like('%TYVASO%'), 'TYVASO')
                                                        .when(upper(col('prod.Name')) == 'ORENITRAM', 'ORENITRAM')
                                                        .when(upper(col('prod.Name')) == 'REMODULIN', 'REMODULIN')
                                                        .when(upper(col('prod.Name')).isin( 'FRANCHISE', 'UNBRANDED DISEASE STATE PH-ILD', 'BRANDED DISEASE STATE PH-ILD', 'DISEASE STATE PH-ILD', 'URGENCY TO TREAT', 'DISEASE STATE PAH', 'DISEASE STATE'), 'TREPROSTINIL')
                                                        .otherwise(None).alias('product'),
                                                        when(upper(col('prof.Name')).isin('UT. PAH MDD'), 'MDD')
                                                        .when(upper(col('prof.Name')).isin('UT.CPL', 'UT.MEDICAL AFFAIRS', 'UT.MSL.ALD', 'UT.MSL.PH'), 'MSL')
                                                        .when(upper(col('prof.Name')).isin('UT.PAH SALES', 'UT.PAH SALES - RBD', 'UT.PAH SALES.RCPS', 'UT.ILD SALES'), 'SALES')
                                                        .when(upper(col('prof.Name')).isin('UT.RNS.COM.MGR'), 'RNS')
                                                        .otherwise(None).alias('team'),
                                                        when(
                                                               regexp_replace(
                                                                regexp_replace(
                                                                                upper(trim(col('df2.sci_product_raw'))),
                                                                                '(NONE|EVLP|RALINEPAG|TRANSPLANT LOGISTICS|ORGAN ALLOCATION DISTRIBUTION|LUNG TRANSPLANT\\s+\\(ALLOCATION/LOGISTICS\\)|DISEASE STATE EDUCATION TRANSPLANT)', 
                                                                                ''
                                                                              ), ';+', '; '
                                                                          ).isin('',';','; '), None)
                                                            .otherwise(
                                                                        regexp_replace(
                                                                            regexp_replace(
                                                                                            upper(trim(col('df2.sci_product_raw'))),
                                                                                            '(NONE|EVLP|RALINEPAG|TRANSPLANT LOGISTICS|ORGAN ALLOCATION DISTRIBUTION|LUNG TRANSPLANT\\s+\\(ALLOCATION/LOGISTICS\\)|DISEASE STATE EDUCATION TRANSPLANT)', 
                                                                                            ''
                                                                                          ), ';+', '; '
                                                                                    )
                                                                      )
                                                            .alias('scientific_product'),
                                                        when(
                                                                (upper(trim(col('scientific_product'))).like('%TREPROSTINIL DPI%')) |
                                                                (upper(trim(col('scientific_product'))).like('%TREPROSTINIL NEBULIZED%')) |
                                                                (upper(col('product')) == 'TYVASO'),
                                                                'TYVASO'
                                                            ).otherwise(None).alias('tyvaso_flag'),
                                                        when(
                                                                (upper(trim(col('scientific_product'))).like('%REMUNITY%')) |
                                                                (upper(trim(col('scientific_product'))).like('%TREPROSTINIL IV%')) |
                                                                (upper(trim(col('scientific_product'))).like('%TREPROSTINIL SC%')) |
                                                                (upper(col('product')) == 'REMODULIN'),
                                                                'REMODULIN'
                                                            ).otherwise(None).alias('remodulin_flag'),
                                                        when(
                                                                (upper(trim(col('scientific_product'))).like('%TREPROSTINIL ORAL%')) |
                                                                (upper(col('product')) == 'ORENITRAM'),
                                                                'ORENITRAM'
                                                            ).otherwise(None).alias('orenitram_flag'),
                                                        when(
                                                                (upper(trim(col('scientific_product'))).like('%2024 WSPH GUIDELINES%')) |
                                                                (upper(trim(col('scientific_product'))).like('%ACR GUIDELINES DISCUSSION%')) |
                                                                (upper(trim(col('scientific_product'))).like('%CADD-MS3%')) |
                                                                (upper(trim(col('scientific_product'))).like('%COMPETITIVE TRIALS/PRODUCTS/DEVICES%')) |
                                                                (upper(trim(col('scientific_product'))).like('%DEVICE EDUCATION%')) |
                                                                (upper(trim(col('scientific_product'))).like('%DISEASE STATE EDUCATION & SCREENING PH-ILD%')) |
                                                                (upper(trim(col('scientific_product'))).like('%DISEASE STATE EDUCATION CTD-ILD%')) |
                                                                (upper(trim(col('scientific_product'))).like('%DISEASE STATE EDUCATION ILD%')) |
                                                                (upper(trim(col('scientific_product'))).like('%DISEASE STATE EDUCATION PAH%')) |
                                                                (upper(trim(col('scientific_product'))).like('%EARLY PROSTACYCLIN TREATMENT%')) |
                                                                (upper(trim(col('scientific_product'))).like('%ESC/ERS PH GUIDE%')) |
                                                                (upper(trim(col('scientific_product'))).like('%ESC/ERS PH GUIDELINES%')) |
                                                                (upper(trim(col('scientific_product'))).like('%GUIDELINES%')) |
                                                                (upper(trim(col('scientific_product'))).like('%ILD%')) |
                                                                (upper(trim(col('scientific_product'))).like('%ILD GUIDELINES%')) |
                                                                (upper(trim(col('scientific_product'))).like('%INHALED TRE AE MANAGEMENT/TOLERABILITY%')) |
                                                                (upper(trim(col('scientific_product'))).like('%ISR%')) |
                                                                (upper(trim(col('scientific_product'))).like('%NON-PRODUCT SCIENTIFIC DISCUSSION%')) |
                                                                (upper(trim(col('scientific_product'))).like('%PH-COPD%')) |
                                                                (upper(trim(col('scientific_product'))).like('%PH-ILD%')) |
                                                                (upper(trim(col('scientific_product'))).like('%PRECLINICAL SCIENTIFIC DISCUSSION%')) |
                                                                (upper(trim(col('scientific_product'))).like('%SCREENING PH-ILD%')) |
                                                                (upper(trim(col('scientific_product'))).like('%TADALAFIL%')) |
                                                                (upper(trim(col('scientific_product'))).like('%THERAPEUTIC LANDSCAPE%')) |
                                                                (upper(trim(col('scientific_product'))).like('%TRE MOA%')) |
                                                                (upper(trim(col('scientific_product'))).like('%TREPROSTINIL MOA%')) |
                                                                (upper(trim(col('scientific_product'))).like('%UT CONGRESS DATA%')) |
                                                                (upper(trim(col('scientific_product'))).like('%UT PIPELINE%')) |
                                                                (upper(col('product')) == 'TREPROSTINIL'),
                                                                'TREPROSTINIL'
                                                            ).otherwise(None).alias('treprostinil_flag'),
                                                        concat_ws(", ", col('tyvaso_flag'), col('remodulin_flag'), col('orenitram_flag'), col('treprostinil_flag')).alias('concat_product_flag')
                                            
                                                    )
                                       )

    df3 = calls_with_products_teams_sci_df.alias('df3')

    calls_cumulative_table = df3.where(~((col('scientific_product').isNull()) & (col('product').isNull())))

    df4 = calls_cumulative_table.alias('df4')

    final_0_table = df4.groupBy('call_id', 'account_id', 'call_date', 'call_timestamp', 'rep_id', 'Rep_Name', 'Rep_Email', 'event_type', 'Subject_Priority', 'Interaction_Priority', 'team_raw', 'team').agg(
                               spark_max(col('tyvaso_flag')).alias('tyvaso_flag_agg'),
                               spark_max(col('remodulin_flag')).alias('remodulin_flag_agg'),
                               spark_max(col('orenitram_flag')).alias('orenitram_flag_agg'),
                               spark_max(col('treprostinil_flag')).alias('treprostinil_flag_agg'),
                               spark_max(when(col('scientific_product').isNotNull(), col('concat_product_flag'))).alias('concat_product_flag_agg')
                            )
                        
    df5 = final_0_table.alias('df5')

    final_1_table = df5.select(
                                col('df5.*'),
                                coalesce(col('concat_product_flag_agg'), concat_ws(", ", col('tyvaso_flag_agg'), col('remodulin_flag_agg'), col('orenitram_flag_agg'), col('treprostinil_flag_agg'))).alias('product_detailed')
                              )
    
    calls_final_table = final_1_table.select(
                                                col('call_id').alias('event_id'),
                                                col('rep_id').alias('rep_id'),
                                                col('Rep_Name').alias('rep_name'),
                                                col('rep_email').alias('rep_email'),
                                                col('team_raw').alias('team_raw'),
                                                col('call_id').alias('marketing_id'),
                                                col('account_id').alias('hcp_id'),
                                                lit('Call').alias('event_channel'),
                                                col('event_type').alias('event_type'),
                                                col('call_date').alias('event_date'),
                                                col('call_timestamp').alias('event_timestamp'),
                                                col('team').alias('team'),
                                                concat_ws("_", col('team'), col('event_type'), col('event_channel')).alias('det_touchpoint'),
                                                col('product_detailed').alias('product_name')
                                            )
    
    return calls_final_table

########################################################## NEW 02 FEB CHANGES IN CLUSTERS AND NPI #################################################################################################


def build_data_with_clusters_npi(spark, comp_table, start_date="2023-01-01", end_date='2025-03-31'):
    """
    Build the DataFrame with HCP's clusters and NPI.
    """ 

    enable_competitor = comp_table is not None

    rf = spark.table('`marketing-analytics-catalog`.raw_test.dw_processeddata_dbo_patientactivityhistorydetailed').alias('rf')

    segment = spark.table('`marketing-analytics-catalog`.raw_test.dw_tableau_marketing_brandsegment').alias('segment')

    rundate_2 = (segment.filter(col("rundate") <= end_date).orderBy(col("rundate").desc()).limit(1))    
    rundate = rundate_2.collect()[0]["rundate"]                                                      

    aat = spark.table('`marketing-analytics-catalog`.raw_test.dw_tableau_dbo_accountallterritories').alias('aat')

    ############################################################ NEW UPDATE ######################################################################

    if enable_competitor:
        comp = spark.table(comp_table)
    else:
        comp = None

    if enable_competitor: 

        max_date = (
                    comp
                    .where((col("DateStart") == start_date) & (col("DateEnd") == end_date))
                    .select(spark_max("Date_Updated").alias("max_date"))
                    .collect()[0]["max_date"]
                )

        comp = comp.where(
                            (col("DateStart") == start_date) &
                            (col("DateEnd") == end_date) &
                            (col("Date_Updated") == max_date)
                        )

        comp = comp.groupBy("NPI").agg(
                                            coalesce(spark_max(when(col("BRAND") == "Tyvaso", col("Unique_Patients"))), lit(0)).alias("Tyvaso_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Orenitram", col("Unique_Patients"))), lit(0)).alias("Orenitram_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Remodulin", col("Unique_Patients"))), lit(0)).alias("Remodulin_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "pH12 Flolan Sterile Diluent", col("Unique_Patients"))), lit(0)).alias("pH12_Flolan_Sterile_Diluent_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Epoprostenol Sodium", col("Unique_Patients"))), lit(0)).alias("Epoprostenol_Sodium_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Sildenafil", col("Unique_Patients"))), lit(0)).alias("Sildenafil_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Tadalafil", col("Unique_Patients"))), lit(0)).alias("Tadalafil_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Esbriet", col("Unique_Patients"))), lit(0)).alias("Esbriet_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Bosentan", col("Unique_Patients"))), lit(0)).alias("Bosentan_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Adcirca", col("Unique_Patients"))), lit(0)).alias("Adcirca_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Opsumit", col("Unique_Patients"))), lit(0)).alias("Opsumit_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Tracleer", col("Unique_Patients"))), lit(0)).alias("Tracleer_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Alyq", col("Unique_Patients"))), lit(0)).alias("Alyq_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Winrevair", col("Unique_Patients"))), lit(0)).alias("Winrevair_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Opsynvi", col("Unique_Patients"))), lit(0)).alias("Opsynvi_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Letairis", col("Unique_Patients"))), lit(0)).alias("Letairis_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Ofev", col("Unique_Patients"))), lit(0)).alias("Ofev_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Flolan", col("Unique_Patients"))), lit(0)).alias("Flolan_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Ambrisentan", col("Unique_Patients"))), lit(0)).alias("Ambrisentan_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Actemra", col("Unique_Patients"))), lit(0)).alias("Actemra_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Ventavis", col("Unique_Patients"))), lit(0)).alias("Ventavis_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Treprostinil", col("Unique_Patients"))), lit(0)).alias("Treprostinil_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Sterile Diluent for Treprostinil", col("Unique_Patients"))), lit(0)).alias("Sterile_Diluent_for_Treprostinil_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Veletri", col("Unique_Patients"))), lit(0)).alias("Veletri_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Adempas", col("Unique_Patients"))), lit(0)).alias("Adempas_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Revatio", col("Unique_Patients"))), lit(0)).alias("Revatio_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Sildenafil Citrate", col("Unique_Patients"))), lit(0)).alias("Sildenafil_Citrate_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Uptravi", col("Unique_Patients"))), lit(0)).alias("Uptravi_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Flolan Sterile Diluent", col("Unique_Patients"))), lit(0)).alias("Flolan_Sterile_Diluent_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Pirfenidone", col("Unique_Patients"))), lit(0)).alias("Pirfenidone_PatientCount"),
                                            coalesce(spark_max(when(col("BRAND") == "Yutrepia", col("Unique_Patients"))), lit(0)).alias("Yutrepia_PatientCount"),
                                        )
        
        comp = comp.alias('comp')

    ##############################################################################################################################################
    
    df_with_segment = segment.where(col('rundate') == rundate).groupBy(col('accountid'), col('account_name'), col('institution_name'), col('npispecialty')).agg(
                                    spark_max(when(upper(col('segment_product')) == 'TYVASO', col('cluster_name'))).alias('tyvaso_clustername'),
                                    spark_max(when(upper(col('segment_product')) == 'REMODULIN', col('cluster_name'))).alias('remodulin_clustername'),
                                    spark_max(when(upper(col('segment_product')) == 'ORENITRAM', col('cluster_name'))).alias('orenitram_clustername'),
                                    (when(col('tyvaso_clustername') == 'High Performer', 1)
                                    .when(col('tyvaso_clustername') == 'Moderate Performer', 2)
                                    .when(col('tyvaso_clustername') == 'Average Performer', 3)
                                    .when(col('tyvaso_clustername') == 'Low Performer', 4)
                                    .when(col('tyvaso_clustername') == 'Near Sleeping', 5)
                                    .when(col('tyvaso_clustername') == 'Sleeping', 6)
                                    .when(col('tyvaso_clustername') == 'Unresponsive', 7)).alias('tyvaso_priority'),
                                    (when(col('remodulin_clustername') == 'High Performer', 1)
                                    .when(col('remodulin_clustername')== 'Moderate Performer', 2)
                                    .when(col('remodulin_clustername') == 'Average Performer', 3)
                                    .when(col('remodulin_clustername') == 'Low Performer', 4)
                                    .when(col('remodulin_clustername') == 'Near Sleeping', 5)
                                    .when(col('remodulin_clustername') == 'Sleeping', 6)
                                    .when(col('remodulin_clustername') == 'Unresponsive', 7)).alias('remodulin_priority'),
                                    (when(col('orenitram_clustername') == 'High Performer', 1)
                                    .when(col('orenitram_clustername') == 'Moderate Performer', 2)
                                    .when(col('orenitram_clustername') == 'Average Performer', 3)
                                    .when(col('orenitram_clustername') == 'Low Performer', 4)
                                    .when(col('orenitram_clustername') == 'Near Sleeping', 5)
                                    .when(col('orenitram_clustername') == 'Sleeping', 6)
                                    .when(col('orenitram_clustername')   == 'Unresponsive', 7)).alias('orenitram_priority'),
                                    least(col('tyvaso_priority'), col('remodulin_priority'), col('orenitram_priority')).alias('treprostinil_priority'),
                                    (when(col('treprostinil_priority') == 1, 'High Performer')
                                    .when(col('treprostinil_priority') == 2, 'Moderate Performer')
                                    .when(col('treprostinil_priority') == 3, 'Average Performer')
                                    .when(col('treprostinil_priority') == 4, 'Low Performer')
                                    .when(col('treprostinil_priority') == 5, 'Near Sleeping')
                                    .when(col('treprostinil_priority') == 6, 'Sleeping')
                                    .when(col('treprostinil_priority') == 7, 'Unresponsive')).alias('treprostinil_clustername')
                                ).alias('df_with_segment')
    
    invalid_specialties = ["", "'", "?", "0", "0THER", "C", "G", "H", "JKL", "K", "L", "LK", "LK;", "M", "N", "OP", "NA", "NONE", "NOT SPECIFIED", "1225193303", "1548477003", "1649337510", "9784522"]

    aat_df_with_cleaned_specialty = aat.withColumn(
                                                        "cleaned_speciality_aat",
                                                        when(
                                                                upper(trim(col("npispecialty"))).isin(invalid_specialties), None
                                                            ).otherwise(col("npispecialty"))
                                                    )

    aat2 = aat_df_with_cleaned_specialty.alias('aat2')

    df_with_npi = df_with_segment.join(aat2, col('df_with_segment.accountid') == col('aat2.AccountID'), how = 'fullouter').select(
                                    coalesce(col('aat2.accountid'), col('df_with_segment.accountid')).alias('hcp_id'),
                                    col('aat2.NPI'),
                                    coalesce(col('aat2.cleaned_speciality_aat'), when(
                                                                                    trim(col("df_with_segment.npispecialty")) == "Not Specified",
                                                                                    None
                                                                                ).otherwise(trim(col("df_with_segment.npispecialty")))
                                            ).alias('npi_specialty'),
                                    col('df_with_segment.institution_name'),
                                    col('df_with_segment.treprostinil_clustername'),
                                    col('df_with_segment.tyvaso_clustername'),
                                    col('df_with_segment.remodulin_clustername'),
                                    col('df_with_segment.orenitram_clustername'),
                                )
    
    df1 = df_with_npi.alias('df1')

    df_extra =  rf.join(aat, col('rf.ReferralPrescriberAccountID') == col('aat.AccountID'), 'left').where(
                                (col('rf.IsValidReferral') == True) &
                                (col('aat.EPLstatusPAH').like('Valid%')) &
                                (col('aat.IsActive') == True) &
                                (col('aat.IsPersonAccount') == True)
                            ).groupBy(col('rf.ReferralPrescriberAccountID').alias('hcp_id'), col('rf.Brand').alias('product_name')).agg(
                                                                                                                                        spark_min(col('rf.ReferralDate')).alias('earliestdate'), 
                                                                                                                                        spark_max(col('rf.ReferralDate')).alias('latestdate'),
                                                                                                                                        datediff(col('latestdate'), col('earliestdate')).alias("totaldays")
                                                                                                                                        )
    
    df_pivoted_up = df_extra.groupBy(col('hcp_id')).agg(
                                                            spark_max(when(col('product_name') == 'TYVASO', col('totaldays'))).alias('TYVASO_loyalty_period'),
                                                            spark_max(when(col('product_name') == 'REMODULIN', col('totaldays'))).alias('REMODULIN_loyalty_period'),
                                                            spark_max(when(col('product_name') == 'ORENITRAM', col('totaldays'))).alias('ORENITRAM_loyalty_period')
                                                        )
    
    df2 = df_pivoted_up.alias('df2')

    df_extra_2 =  rf.join(aat, col('rf.ReferralPrescriberAccountID') == col('aat.AccountID'), 'left').where(
                            (col('rf.IsValidReferral') == True) &
                            (col('aat.EPLstatusPAH').like('Valid%')) &
                            (col('aat.IsActive') == True) &
                            (col('aat.IsPersonAccount') == True)
                        ).groupBy(col('rf.ReferralPrescriberAccountID').alias('hcp_id')).agg(
                                                                                                spark_min(col('rf.ReferralDate')).alias('earliestdate'), 
                                                                                                spark_max(col('rf.ReferralDate')).alias('latestdate'),
                                                                                                datediff(col('latestdate'), col('earliestdate')).alias("TREPROSTINIL_loyalty_period")
                                                                                            )

    df3 = df_extra_2.alias('df3')

    df_comb = df3.join(df2, col('df3.hcp_id') == col('df2.hcp_id'), 'left').select(
                                                                                    col('df3.*'), 
                                                                                    col('df2.TYVASO_loyalty_period'),
                                                                                    col('df2.REMODULIN_loyalty_period'),
                                                                                    col('df2.ORENITRAM_loyalty_period')
                                                                                )

    df_with_flag = df_comb.withColumn(
                                        'TREPROSTINIL_lob', when(col('TREPROSTINIL_loyalty_period').isNull(), None)
                                                        .when(col('TREPROSTINIL_loyalty_period') <= 730, lit('0_2_Years'))
                                                        .when(((col('TREPROSTINIL_loyalty_period') > 730) & (col('TREPROSTINIL_loyalty_period') <= 3650)), lit('2_10_Years'))
                                                        .when(col('TREPROSTINIL_loyalty_period') > 3650, lit('10_plus_Years'))   
                                    ).withColumn(
                                        'TYVASO_lob', when(col('TYVASO_loyalty_period').isNull(), None)
                                                        .when(col('TYVASO_loyalty_period') <= 730, lit('0_2_Years'))
                                                        .when(((col('TYVASO_loyalty_period') > 730) & (col('TYVASO_loyalty_period') <= 3650)), lit('2_10_Years'))
                                                        .when(col('TYVASO_loyalty_period') > 3650, lit('10_plus_Years'))
                                    ).withColumn(
                                        'REMODULIN_lob', when(col('REMODULIN_loyalty_period').isNull(), None)
                                                        .when(col('REMODULIN_loyalty_period') <= 730, lit('0_2_Years'))
                                                        .when(((col('REMODULIN_loyalty_period') > 730) & (col('REMODULIN_loyalty_period') <= 3650)), lit('2_10_Years'))
                                                        .when(col('REMODULIN_loyalty_period') > 3650, lit('10_plus_Years'))
                                    ).withColumn(
                                        'ORENITRAM_lob', when(col('ORENITRAM_loyalty_period').isNull(), None)
                                                        .when(col('ORENITRAM_loyalty_period') <= 730, lit('0_2_Years'))
                                                        .when(((col('ORENITRAM_loyalty_period') > 730) & (col('ORENITRAM_loyalty_period') <= 3650)), lit('2_10_Years'))
                                                        .when(col('ORENITRAM_loyalty_period') > 3650, lit('10_plus_Years'))
                                    )  
                                
    df4 = df_with_flag.alias('df4')    

    df_pre_final = df1.join(df4, col('df1.hcp_id') == col('df4.hcp_id'), how = 'left').select(
                                                                                            col('df1.*'),
                                                                                            col('df4.TREPROSTINIL_loyalty_period'),
                                                                                            col('df4.TREPROSTINIL_lob'),
                                                                                            col('df4.TYVASO_loyalty_period'),
                                                                                            col('df4.TYVASO_lob'),
                                                                                            col('df4.REMODULIN_loyalty_period'),
                                                                                            col('df4.REMODULIN_lob'),
                                                                                            col('df4.ORENITRAM_loyalty_period'),
                                                                                            col('df4.ORENITRAM_lob'),
                                                                                        )   

    df5 = df_pre_final.alias('df5')

########################################################### COMPETITOR DATA CODE OLD ONLY 3 + ADDED ALL ##########################################################################################

    if enable_competitor:

        comp_writer_expr_3 = (
                                (col('comp.Uptravi_PatientCount') > 0) |
                                (col('comp.Yutrepia_PatientCount') > 0) |
                                (col('comp.Winrevair_PatientCount') > 0)
                            )

        comp_writer_expr_all = (
                                    (col('comp.Actemra_PatientCount') > 0) |
                                    (col('comp.Adcirca_PatientCount') > 0) |
                                    (col('comp.Adempas_PatientCount') > 0) |
                                    (col('comp.Alyq_PatientCount') > 0) |
                                    (col('comp.Ambrisentan_PatientCount') > 0) |
                                    (col('comp.Bosentan_PatientCount') > 0) |
                                    (col('comp.Epoprostenol_Sodium_PatientCount') > 0) |
                                    (col('comp.Esbriet_PatientCount') > 0) |
                                    (col('comp.Flolan_PatientCount') > 0) |
                                    (col('comp.Letairis_PatientCount') > 0) |
                                    (col('comp.Ofev_PatientCount') > 0) |
                                    (col('comp.Opsumit_PatientCount') > 0) |
                                    (col('comp.Opsynvi_PatientCount') > 0) |
                                    (col('comp.Pirfenidone_PatientCount') > 0) |
                                    (col('comp.Revatio_PatientCount') > 0) |
                                    (col('comp.Sildenafil_PatientCount') > 0) |
                                    (col('comp.Sildenafil_Citrate_PatientCount') > 0) |
                                    (col('comp.Tadalafil_PatientCount') > 0) |
                                    (col('comp.Tracleer_PatientCount') > 0) |
                                    (col('comp.Uptravi_PatientCount') > 0) |
                                    (col('comp.Veletri_PatientCount') > 0) |
                                    (col('comp.Ventavis_PatientCount') > 0) |
                                    (col('comp.Winrevair_PatientCount') > 0) |
                                    (col('comp.Yutrepia_PatientCount') > 0)
                                )

    if enable_competitor:

        df_returned = (
                            df5.join(comp, col('df5.NPI') == col('comp.NPI'), how='left')
                            .withColumn('flag_comp_3', when(comp_writer_expr_3, lit('writes')).otherwise(lit('does_not_writes')))
                            .withColumn('flag_comp_all', when(comp_writer_expr_all, lit('writes')).otherwise(lit('does_not_writes')))
                            .select(
                                    col('df5.*'),
                                    col('flag_comp_3'),
                                    col('flag_comp_all')
                            )
                        )
        
    else:

        df_returned = (
                            df5
                            .withColumn('flag_comp_3', lit(None).cast("string"))
                            .withColumn('flag_comp_all', lit(None).cast("string"))
                        )

    return df_returned, rundate

########################################################################### HCP LONG CREATION ##########################################

def build_hcp_long(start, end, comp_table):
    """
    Build the HCP Longitudinal DataFrame.
    """ 

    spark = SparkSession.builder.getOrCreate()

    email_df = build_email_data(spark, start, end)
    referrals_df = build_referrals_data(spark, start, end)
    speaker_program_df = build_speaker_program_data(spark, start, end)
    calls_df = build_calls_data(spark, start, end)

    final_all_four = (
                        calls_df
                        .unionAll(speaker_program_df)
                        .unionAll(email_df)
                        .unionAll(referrals_df)
                    ).withColumn("event_datetime", date_format(col("event_timestamp").cast("timestamp"), "yyyy-MM-dd HH:mm:ss")).drop("event_timestamp").orderBy("hcp_id", "event_date")

    w1 = Window.orderBy(
                        upper(col("hcp_id")),
                        col("event_date"),
                        when(col("event_channel") == "Referral", 1).otherwise(0),
                        col('det_touchpoint'),                       
                        col("event_datetime"),                     
                        col("event_id")
                    )

    df_with_serial_no = (final_all_four.withColumn("serial_no", row_number().over(w1)))

    ########################################## ADDING REFERRALS COUNT ##########################################################################

    df1 = df_with_serial_no.alias('df1')

    #############################################################################################################################################

    hcp_clusters_and_npi, date2 = build_data_with_clusters_npi(spark, comp_table, start, end)
    df2 = hcp_clusters_and_npi.alias('df2')

    df_final = (
                df1.join(df2, col('df1.hcp_id') == col('df2.hcp_id'), how = 'left')
                    .select(
                            col('df1.*'),
                            (when(col('df1.det_touchpoint') == 'Email_Clicked', 'Email')
                            .when(col('df1.det_touchpoint').isin('MDD_Conference_Call', 'MSL_Conference_Call', 'MSL_Live_Call', 'MDD_Live_Call', 'SALES_Live_Call', 'RNS_Live_Call'), 'Live Call')
                            .when(col('df1.det_touchpoint').isin('MDD_PhoneEmail_Call', 'MDD_Virtual_Call', 'MSL_PhoneEmail_Call', 'MSL_Virtual_Call', 'RNS_PhoneEmail_Call', 'RNS_Virtual_Call', 'SALES_PhoneEmail_Call', 'SALES_Virtual_Call'), 'Virtual Call')
                            .when(col('df1.det_touchpoint') == 'Speaker Program_Live', 'Live Spk Pgm')
                            .when(col('df1.det_touchpoint') == 'Speaker Program_Virtual', 'Virtual Spk Pgm'))
                            .alias('channel_5'),

                            (when(col('df1.event_channel') == 'Call', col('df1.team'))
                            .when(col('df1.event_channel') == 'Email', 'EMAIL')
                            .when(col('df1.event_channel').like('%Speaker Program%'), lit('SPK PGM')))
                            .alias('channel_6'),

                            col('df2.treprostinil_clustername'),
                            col('df2.tyvaso_clustername'),
                            col('df2.remodulin_clustername'),
                            col('df2.orenitram_clustername'),
                            col('df2.NPI'),
                            col('df2.npi_specialty'),
                            col('df2.TREPROSTINIL_loyalty_period'),
                            col('df2.TREPROSTINIL_lob'),
                            col('df2.TYVASO_loyalty_period'),
                            col('df2.TYVASO_lob'),
                            col('df2.REMODULIN_loyalty_period'),
                            col('df2.REMODULIN_lob'),
                            col('df2.ORENITRAM_loyalty_period'),
                            col('df2.ORENITRAM_lob'),
                            col('df2.flag_comp_3').alias('TREPROSTINIL_competitor_drug_3'),
                            col('df2.flag_comp_3').alias('TYVASO_competitor_drug_3'),
                            col('df2.flag_comp_3').alias('REMODULIN_competitor_drug_3'),
                            col('df2.flag_comp_3').alias('ORENITRAM_competitor_drug_3'),
                            col('df2.flag_comp_all').alias('TREPROSTINIL_competitor_drug_all'),
                            col('df2.flag_comp_all').alias('TYVASO_competitor_drug_all'),
                            col('df2.flag_comp_all').alias('REMODULIN_competitor_drug_all'),
                            col('df2.flag_comp_all').alias('ORENITRAM_competitor_drug_all'),
                        ).orderBy(col('df1.serial_no'))
                )

    return df_final.orderBy("serial_no"), spark

def build_hcp_long_for_model(start, end, comp_table):
    """
    Build the HCP Longidunal that will be used for the run.
    """ 

    df, spark = build_hcp_long(start, end, comp_table)

    df = df.alias('df')
    att = spark.table('`marketing-analytics-catalog`.raw_test.dw_datasets_centris_speakerprogramattendee').alias('att')
    
    df = df.join(
                    att,
                    col("df.event_id") == col("att.AttendanceID"),
                    how = "left"
                ).select(
                            col('df.*'),
                            col('att.attendeeRole'),
                            col('att.attendanceflag')
                            ).alias('df')

    referral_hcps = (
                        df.where(col("event_channel") == "Referral")
                        .select(col("hcp_id").alias("hcp_id_ref"))
                        .distinct()
                    ).alias('rh')

    df = (
            df.join(referral_hcps, col("df.hcp_id") == col("rh.hcp_id_ref"), "left").select(
                                                                                                col("df.*"),
                                                                                                when(col("rh.hcp_id_ref").isNull(), lit(False))
                                                                                                    .otherwise(True)
                                                                                                    .alias("is_ref_writer")
                                                                                            ).drop("hcp_id_ref")      
        )

    df = df.where(
                    ((col('df.det_touchpoint') != 'SALES_PhoneEmail_Call') | col('df.det_touchpoint').isNull()) &
                    ((col('df.attendeeRole') != 'Speaker') | col('df.attendeeRole').isNull()) &
                    ((col('df.AttendeeRole').isNull()) | (col('df.attendanceflag') != 'N')) &
                    (
                        # KEEP REFERRAL WRITERS ALWAYS
                        (col("is_ref_writer") == True)
                        |
                        # NON-REF WRITERS MUST HAVE VALID NPI
                        (col('npi').isNotNull() & (trim(col('npi')) != ''))
                        &
                        # AND VALID SPECIALITY
                        (~trim(upper(col("npi_specialty")))
                            .isin('PHARMACIST', 'NURSE ANESTHETIST, CERTIFIED REGISTERED', 'OTHER', 'NOT SPECIFIED'))
                    )
                )

    df = df.select("df.*")

    return df.orderBy(col('serial_no'))

# if __name__ == '__main__':
#     start = '2023-01-01'
#     end = '2025-03-31'
#     comp_table = "`coe-consultant-catalog`.dw.competitor_data"  
#     df1 = build_hcp_long_for_model(start, end, comp_table)

#     comp_table_2 = None
#     df2 = build_hcp_long_for_model(start, end, comp_table_2)