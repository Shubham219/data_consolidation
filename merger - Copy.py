# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

# Basen dir
base_dir = r'\Data\pos_consolidation'

bos_notional_type_mapping = {'Private Equity Funds': 'Commited Capital',
                             'Commodity ETFs': 'UNIT',
                             'Commodity Funds': 'UNIT',
                             'Hedge Funds': 'UNIT',
                             'Cash and Cash EQ (10010 :  13010)': 'Amount',
                             '12050 (Equity Derivatives)': 'Quantity',
                             '14060 (IRS)': 'FAMT',
                             'Equity (all asset Class except Equity SP)': 'UNIT',
                             'Equity SP': 'FAMT',
                             'Bonds': 'FAMT',
                             'Fixed Income ETFs': 'UNIT',
                             'Fixed Income Funds': 'UNIT',
                             'Fixed Income Structured Products': 'FAMT',
                             '14050 (FX Derivative )': 'Amount',
                             '13090 (Commodity Derivative)': 'Amount',
                             '21010 (Liabiliites)': 'Amount',
                             'Other Funds': 'UNIT',
                             'Other ETFs': 'UNIT',
                             'Unclassified Assets': 'UNIT'
                             }


# Reading the files
# BOS Folder
bos_files = os.listdir(os.path.join(base_dir, 'BOS'))

bos_files_df = pd.DataFrame()

for file in bos_files:
    tmp = pd.read_csv(os.path.join(base_dir, f'BOS/{file}'),
                      sep="|")
    bos_files_df = pd.concat([bos_files_df, tmp],
                             axis=0,
                             ignore_index=False )

bos_files_df['ISIN'] = np.where(bos_files_df['ISIN'].isnull(),
                                bos_files_df['ContractNo'],
                                bos_files_df['ISIN']
                                )

bos_files_df['ISIN_Instrument_ID'] = bos_files_df['ISIN'].copy()

bos_files_df['Bank'] = "BOS"



# CIti folder
citi_files = os.listdir(os.path.join(base_dir, 'Citi'))

citi_files_df = pd.DataFrame()

for file in citi_files:
    try:
        tmp = pd.read_csv(os.path.join(base_dir, f'Citi/{file}'),
                          skiprows=1)

        citi_files_df = pd.concat([citi_files_df, tmp],
                                 axis=0,
                                 ignore_index=False )
    except Exception as exc:
        print("error in this file: ", file)


# error in this file:  Positions_31032021.xls
# error in this file:  Transaction_30032021_31032021.xls


# DBS
dbs_files = os.listdir(os.path.join(base_dir, 'DBS'))

dbs_files_df = pd.DataFrame()

for file in dbs_files:
    try:
        tmp = pd.read_csv(os.path.join(base_dir, f'DBS/{file}'),
                          delimiter="|")

        dbs_files_df = pd.concat([dbs_files_df, tmp],
                                 axis=0,
                                 ignore_index=False )
    except Exception as exc:
        print("error in this file: ", file)


# UBS
ubs_files = os.listdir(os.path.join(base_dir, 'UBS'))

ubs_files_df = pd.DataFrame()

for file in ubs_files:
    try:
        tmp = pd.read_csv(os.path.join(base_dir, f'UBS/{file}'),
                          sep=";",
                          skiprows=7)

        ubs_files_df = pd.concat([ubs_files_df, tmp],
                                 axis=0,
                                 ignore_index=False )
    except Exception as exc:
        print("error in this file: ", file)


# Reading the mapping files
# Cleaning the mapping columns and taking the columns after "-"
mapping = pd.read_csv(base_dir+'/MAPPPING_FILE_Positions schema_dbs_ubs_citi.csv')

# Stripping the attribute
mapping['Attribute'] = mapping['Attribute'].apply(lambda x : x.strip())

# Cleaning columns in the mapping files
mapping['DBS Mapping'] = mapping['DBS Mapping'
                                 ].astype(str).apply(lambda x: x.split("-"))


mapping['DBS Mapping'] = mapping['DBS Mapping'].apply(
    lambda x : x[1].strip() if len(x)>1 else x[0].strip())

# Cleaning columns in the mapping files
mapping['BoS mapping'] = mapping['BoS mapping'
                                 ].astype(str).apply(lambda x: x.split("-"))

mapping['BoS mapping'] = mapping['BoS mapping'].apply(
    lambda x : x[1].strip() if len(x)>1 else x[0].strip())

# Cleaning columns in the mapping files
mapping['UBS Mapping'] = mapping['UBS Mapping'
                                 ].astype(str).apply(lambda x: x.split("-"))

mapping['UBS Mapping'] = mapping['UBS Mapping'].apply(
    lambda x : x[1].strip() if len(x)>1 else x[0].strip())

# Cleaning columns in the mapping files
mapping['CITI Mapping'] = mapping['CITI Mapping'
                                 ].astype(str).apply(lambda x: x.split("-"))

mapping['CITI Mapping'] = mapping['CITI Mapping'].apply(
    lambda x : x[1].strip() if len(x)>1 else x[0].strip())


# Keeping files with the cols present in mapping files only
ubs_cols = mapping.loc[mapping['UBS Mapping'].isin(ubs_files_df.columns),
                       "UBS Mapping"]

ubs_files_new_df = ubs_files_df[ubs_cols].reset_index(drop=True)


# Keeping files with the cols present in mapping files only
bos_cols = mapping.loc[mapping['BoS mapping'].isin(bos_files_df.columns),
                       "BoS mapping"]

bos_files_new_df = bos_files_df[bos_cols].reset_index(drop=True)


# Keeping files with the cols present in mapping files only
dbs_cols = mapping.loc[mapping['DBS Mapping'].isin(dbs_files_df.columns),
                       "DBS Mapping"]

dbs_files_new_df = dbs_files_df[dbs_cols].reset_index(drop=True)


# Keeping files with the cols present in mapping files only
citi_cols = mapping.loc[mapping['CITI Mapping'].isin(citi_files_df.columns),
                       "CITI Mapping"]

citi_files_new_df = citi_files_df[citi_cols].reset_index(drop=True)

citi_files_new_df['Concat("CITI" + Account Number)'] = "CITI" + citi_files_new_df['Account Number']

citi_files_new_df['ISIN_Instrument_ID'] = citi_files_new_df['ISIN'].copy()


# Mapping the columns with mapping file
# Preprocessin
bos_files_new_df['Commited Capital'] = bos_files_df['SubAssetDescription'
                                                ].reset_index(drop=True).map(bos_notional_type_mapping)

bos_files_new_df['USD for all'] = "USD"

bos_mapping = {k:v for k,v in zip(mapping['BoS mapping'], mapping['Attribute'])}
bos_files_new_df = bos_files_new_df.rename(columns=bos_mapping)

bos_files_new_df['Bank'] = 'BOS'
bos_files_new_df = bos_files_new_df.loc[:,~bos_files_new_df.columns.duplicated()]
bos_files_new_df = bos_files_new_df.dropna(how='all').reset_index(drop=True)



# Mapping and Preprocessing
# Creating DBS - BOS
dbs_files_new_df['UNIT'] = dbs_files_df['DBS_ASSET_TYPE'].reset_index(drop=True
                                                      ).map({'Equity':'UNIT'})


dbs_files_new_df['USD'] = "USD"
dbs_files_new_df['USD for all'] = "USD"

dbs_files_new_df['MARKET_VALUE_REF_CCY/MARKET_VALUE_POS_CCY'
                 ] = (dbs_files_df['MARKET_VALUE_REF_CCY'
                                      ].str.replace(",","").astype(float)/dbs_files_df['MARKET_VALUE_POS_CCY'
                                      ].str.replace(",","").astype(float)).reset_index(drop=True)

dbs_mapping = {k:v for k,v in zip(mapping['DBS Mapping'], mapping['Attribute'])}
dbs_files_new_df = dbs_files_new_df.rename(columns=dbs_mapping)
dbs_files_new_df['Bank'] = 'DBS'

dbs_files_new_df = dbs_files_new_df.dropna(how='all').reset_index(drop=True)
dbs_files_new_df = dbs_files_new_df.loc[:,~dbs_files_new_df.columns.duplicated()]




# UBS Key
ubs_mapping = {k:v for k,v in zip(mapping['UBS Mapping'], mapping['Attribute'])}
ubs_files_new_df['UNIT'] = 'UNIT'
ubs_files_new_df['USD for all'] = "USD"
ubs_files_new_df = ubs_files_new_df.rename(columns=ubs_mapping)
ubs_files_new_df['Bank'] = 'UBS'
ubs_files_new_df = ubs_files_new_df.loc[:,~ubs_files_new_df.columns.duplicated()]
ubs_files_new_df = ubs_files_new_df.dropna(how='all').reset_index(drop=True)




# CITI Key
citi_mapping = {k:v for k,v in zip(mapping['CITI Mapping'], mapping['Attribute'])}
citi_files_new_df['UNIT'] = 'UNIT'
citi_files_new_df['USD for all'] = "USD"
citi_files_df.columns = citi_files_df.columns.str.strip()
citi_files_new_df['Market Value (Reporting Currency)/ Market Value (Nominal Currency)'
                 ] = (citi_files_df['Market Value (Reporting Currency)'
                                      ].str.replace(",","").astype(float)/citi_files_df['Market Value (Nominal Currency)'
                                      ].str.replace(",","").astype(float)).reset_index(drop=True)

citi_files_new_df = citi_files_new_df.rename(columns=citi_mapping)
citi_files_new_df['Bank'] = 'CITI'
citi_files_new_df = citi_files_new_df.loc[:,~citi_files_new_df.columns.duplicated()]
citi_files_new_df = citi_files_new_df.dropna(how='all').reset_index(drop=True)



all_merged_df = pd.concat([bos_files_new_df,
                           dbs_files_new_df,
                           ubs_files_new_df,
                           citi_files_new_df
                           ], axis=0, ignore_index=True)


all_merged_df['Exchange_rate_Ref_ccy'] = all_merged_df['Exchange_rate_Report'
                                                       ].copy()

if ('Maturity/Exp_Date' not in all_merged_df.columns) & \
    ('Accrued_interest' not in all_merged_df.columns) :

    all_merged_df['Maturity/Exp_Date'] = np.nan
    all_merged_df['Accrued_interest'] = np.nan


all_merged_df.to_csv('/Output/all_merged_v0.5.csv',
                     index=False)
