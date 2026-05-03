# SPLUNK Queries
#### Query sourcetypes
```
| metadata type=sourcetypes index=iam
| metadata type=sourcetypes index=iam | table sourcetype
```
#### Query API count with 1m granularity for each API in the last 10hours
```
index=iam earliest=-10h sourcetype=iam_eiil_transaction | eval fields=split(_raw,",") |   eval api=mvindex(fields,1) | eval 
rtt=mvindex(fields,2) | timechart span=1m count by api
```
#### Query security index for Loadbalancer ports going up / down events on IAM LB devices.
```
index=security *iam* host=lbnpol3* OR host=lbnpol4* 
index=security 208.54.144.161 OR 208.54.154.1 host=gtmpol1
index=security 208.54.144.161 OR 208.54.154.1 OR 208.54.96.161 OR 208.54.55.1 OR 10.188.100.25 OR	10.188.88.25 OR 10.175.100.25 OR 10.175.88.25 host=gtm* | search "UP --> DOWN"
```

index=iam host=POL*IMP* NOT Ericsson* | eval fields=split(_raw,",") | eval Client=mvindex(fields,6) | eval API=mvindex(fields,3) | eval response=mvindex(fields,14) | stats count by Client, API, response

#### EIIL Latency & error rates.
```
index=iam host=POL*LD*  sourcetype=iam_eiil_transaction  | eval fields=split(_raw,",") |  eval api=mvindex(fields,1) | eval rtt=mvindex(fields,2) | eval result=mvindex(fields,3) | eval error=mvindex(fields,4)|   eval error2=mvindex(fields,5)|eval client=mvindex(fields,10) | stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500)) AS Abnormal_Latency500ms,  count(eval(rtt > 2000)) AS Outliers2s, count(eval(result == "ERROR")) AS errors by api  | eval "Abnormal_Latency%"=round((Abnormal_Latency500ms/Totals)*100,1) | eval "error%"=round((errors/Totals)*100,1) | eval "Outliers%"=round((Outliers2s/Totals)*100,1)| sort Totals table api,Totals,errors, Normal_Latency250ms,Abnormal_Latency500ms,"Abnormal_Latency%", Outliers2s, "Outliers%", "error%"
```

#### CAC Latency by api
```
index=iam host=TTN*IC*  source!=*notification*  | eval fields=split(_raw,",") | eval client=mvindex(fields,10) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) | 
search client=EricssonMSClient OR client=EricssonSVClient|  stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500)) AS Abnormal_Latency500ms,  count(eval(rtt > 2000)) AS Outliers2s by api | eval "Abnormal_Latency%"=round((Abnormal_Latency500ms/Totals)*100,1) | eval "Outliers%"=round((Outliers2s/Totals)*100,1)| sort Totals table api,Totals,Normal_Latency250ms,Abnormal_Latency500ms,"Abnormal_Latency%", Outliers2s, "Outliers%"
```

#### CAC Latency Buckets by hour
```
index=iam source=/opt/msdp/* OR source=/opt/iamtmo/*  NOT Ericsson* QueryByBillingAccount | eval fields=split(_raw,",") | eval HH=substr(mvindex(fields,0),12,2) | eval client=mvindex(fields,10) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) |  eval result=mvindex(fields,5) |   stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500 AND rtt < 1000)) AS gt_500s,  count(eval(rtt > 999 AND rtt < 5000)) AS gt_1s, count(eval(rtt > 4999 AND rtt < 30000)) AS gt_5s, count(eval(rtt > 29999)) AS gt_30s by HH | sort HH table HH, api, Totals, Normal_Latency250ms, gt_500ms, gt_1s, gt_5s, gt_30s
```

#### CAC total, success, failure Counts by api
```
index=iam source=/opt/msdp/* OR source=/opt/iamtmo/*  NOT Ericsson*  | eval fields=split(_raw,",") | eval site=substr(host,1,3)| eval client=mvindex(fields,10) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) |  eval result=mvindex(fields,5) | eval error=mvindex(fields,6) | stats count as Totals, count(eval(result = "SUCCESS")) AS Success, count(eval(result = "ERROR")) AS Failure by api| eval "Success%"=round((Success/Totals)*100,1) |eval "Failure%"=round((Failure/Totals)*100,1) | sort api table api,Totals,Success,"Success%",Failure,"Failure%"
```

#### ECE Latency
```
index=iam host=*IMP* source=*Txlog.OAuth.Authorize*  NOT Ericsson* | eval fields=split(_raw,",") | eval api=mvindex(fields,3) |eval rtt=mvindex(fields,13)| eval client=mvindex(fields,6) | eval result=mvindex(fields,14) |  eval error=mvindex(fields,15) | eval error2=mvindex(fields,16) |  stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500)) AS Abnormal_Latency500ms,  count(eval(rtt > 2000)) AS Outliers2s by api | eval "Abnormal_Latency%"=round((Abnormal_Latency500ms/Totals)*100,1) | eval "Outliers%"=round((Outliers2s/Totals)*100,1)| sort Totals table api,Totals,Normal_Latency250ms,Abnormal_Latency500ms,"Abnormal_Latency%", Outliers2s, "Outliers%"
```

#### ECE Latency Buckets
```
index=iam host=TTN*IMP* source=*Txlog.*    | eval fields=split(_raw,",") | eval api=mvindex(fields,3) |eval rtt=mvindex(fields,13)| eval client=mvindex(fields,6) | eval result=mvindex(fields,14) |  eval error=mvindex(fields,15) | eval error2=mvindex(fields,16) |   stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500 AND rtt < 1000)) AS gt_500s,  count(eval(rtt > 999 AND rtt < 2000)) AS gt_1s, count(eval(rtt > 1999 AND rtt < 3000)) AS gt_2s, count(eval(rtt > 4999)) AS gt_5s by api | sort Totals table api, Totals, Normal_Latency250ms, gt_500ms, gt_1s, gt_2s, gt_5s
```

#### ECE API Case , latency, error
```
index=iam  source="/var/exposure*xlog*" AND ("10050" OR  "20206" OR  "20204" OR  "20202" OR  "20203" OR  "20201" OR  "716" OR  "715" OR  "719" OR  "702" OR  "720" OR  "703" OR  "30002" OR  "30101" OR  "10051" OR  "10054")
| makemv delim="," allowempty=true _raw
| eval API=mvindex(_raw,3), latency=mvindex(_raw,13), outcome=mvindex(_raw,14), reason=mvindex(_raw,15)
| eval API=case( API="10050","GetAllowedPasswordResetMethods", API="20206","IAM_BIOMETRIC_DEREGISTRATION", API="20204","IAM_BIOMETRIC_FINISH_AUTHENTICATION", API="20202","IAM_BIOMETRIC_FINISH_REGISTRATION",
	API="20203","IAM_BIOMETRIC_INIT_AUTHENTICATION", API="20201","IAM_BIOMETRIC_INIT_REGISTRATION", API="716","OAUTH_AUTHENTICATE_REQUEST", API="715","OAUTH_AUTHORIZE_REQUEST",
	API="719","OAUTH_CHANGE_PASSWORD", API="702","OAUTH_GET_ACCESSTOKEN", API="720","OAUTH_RESET_PASSWORD", API="703","OAUTH_VALIDATE_TOKEN", API="30002","QUERY_FEDERATION_IDENTITY",
	API="30101","RISK_ASSESSMENT", API="10051","Validate2ndFactorAnswers", API="10054","ValidateSecurityAnswers", 1==1,API)
| where outcome !=0
| table API, latency, outcome, reason
```
#### ECE total, success, failure Counts by api
```
index=iam source=*Txlog*  NOT Ericsson*  | eval fields=split(_raw,",")  | eval fields=split(_raw,",") | eval api=mvindex(fields,3) |eval rtt=mvindex(fields,13)| eval result=mvindex(fields,14) | stats count as Totals, count(eval(result = "0")) AS Success, count(eval(result = "2")) AS Failure by api| eval "Success%"=round((Success/Totals)*100,1) |eval "Failure%"=round((Failure/Totals)*100,1) | sort api table api,Totals,Success,"Success%",Failure,"Failure%"
```
#### ECE Latency for two clients (perf test)
```
index=iam host=TTN*IMP* source=*Txlog.*   | eval fields=split(_raw,",") | eval api=mvindex(fields,3) |eval rtt=mvindex(fields,13)| eval client=mvindex(fields,6)| eval result=mvindex(fields,14) | search client=EricssonMSClient OR client=EricssonSVClient| stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500)) AS Abnormal_Latency500ms,  count(eval(rtt > 2000)) AS Outliers2s by api | eval "Abnormal_Latency%"=round((Abnormal_Latency500ms/Totals)*100,1) | eval "Outliers%"=round((Outliers2s/Totals)*100,1)| sort Totals table api,Totals,Normal_Latency250ms,Abnormal_Latency500ms,"Abnormal_Latency%", Outliers2s, "Outliers%"
```
#### CAC Notification API performance
```
index=iam host="**IC*" | eval fields=split(_raw,",") | eval apiName=mvindex(fields,3) | search  apiName="NotificationConsumer"  sourcetype!="iam:outbound_transaction" | timechart span=1s count AS TPS
  | eventstats max(TPS) as peakTPS
  | eval peakTime=if(peakTPS==TPS,_time,null())
  | stats avg(TPS) as avgTPS first(peakTPS) as peakTPS first(peakTime) as peakTime
  | fieldformat peakTime=strftime(peakTime,"%x %X")
```
#### ECE GetAccessToken API avg performance by site
```
index=iam  source=*Txlog.OAuth.AccessTokenService* | eval fields=split(_raw,",") | eval Client=mvindex(fields,10) | eval API=mvindex(fields,3) | eval rtt=mvindex(fields,13) | eval site=substr(host,1,3)| timechart span=1m avg(rtt) by site
```
#### Count any wsgconapp client  traffic to inactive site
```
index=iam host=POL*IM* WSGconapp |  eval fields=split(_raw,",") | eval api=mvindex(fields,3) |eval rtt=mvindex(fields,13)| eval result=mvindex(fields,14) | search api !=ip* | timechart span=1m count by api limit=0
index=iam host=POL*IC* WSGconapp | eval fields=split(_raw,",") | eval client=mvindex(fields,10) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) |  timechart span=1m count by api limit=0
```
#### NULL values
```
index=iam sourcetype=iam_prov_trans_log | eval fields=split(_raw,",") | eval tstamp=mvindex(fields,0) | eval api=mvindex(fields,3) |  eval client=mvindex(fields,10) | eval responsemsg=mvindex(fields,6) | eval response=mvindex(fields,5) | eval msisdn=mvindex(fields,33) |eval source= mvindex(fields,35)| eval source2=if(isnull(source) OR source="" ,"source_null",source)| search client="EDA" | search api=CreateCustomerContractBillingAccount | search response=ERROR | search responsemsg=iam_provisioning_internal_error | dedup msisdn |  stats count by tstamp, msisdn, source2
```
#### sub searches
```
index=iam sourcetype=iam_pm_trans_log UpdateServicePermissionFlag [search index=iam "changetype: add" sourcetype=iam_ild | eval fields=split(_raw,",") | eval msisdn_raw=mvindex(fields,0) | eval fields2=split(msisdn_raw,"=") | eval msisdn=mvindex(fields2,1) | table msisdn |rename msisdn as search | format ] | eval fields=split(_raw,",") | eval mds=mvindex(fields,31) | eval msisdn=mvindex(fields,27) | search mds="tmVoWifiEnabled=false" | table _time,msisdn
```
#### EDA wrongly migrating with SL - find the msisdn that got downgrade and upgrade it to PAH.
```
index=iam sourcetype=iam:outbound_transaction CreateCustomerContractBillingAccount [search index=iam sourcetype=iam_prov_trans_log CreateCustomerContractBillingAccount "source=EDA_POSTPAID" | eval fields=split(_raw,",") | eval ctype=substr(mvindex(fields,28),14)| eval msisdn=substr(mvindex(fields,29),8) |eval ban=substr(mvindex(fields,35),8) | search ctype="SL" | table ban |rename ban as search | format ] | eval fields=split(_raw,",") | search OldRole| eval oldrole=mvindex(fields,28) | eval msisdn=mvindex(fields,29)| eval newrole=mvindex(fields,30) |  table msisdn,oldrole,newrole
```

#### Find Userid and email where UpdateIamProfile nullified it and subsequent tmoidmerge failed
```
index=iam sourcetype=iam_prov_trans_log UpdateIamProfile ( Email OR OldEmail )  [ search index=iam sourcetype=iam_aa_trans_log tmoIdMerge "userid_to_retain and userid_to_discard should not be the same" | eval fields=split(_raw,",") | eval uid=mvindex(fields,12) | table uid | rename uid as search | format ] | eval fields=split(_raw,",") | search "Email=" | eval uid=mvindex(fields,12) | eval email=substr(mvindex(fields,27),7,100) | table uid,email
```
#### IDV /  timeouts 
```
index=iam sourcetype=iam_idv_outbound_transaction | eval fields=split(_raw,",") | eval client=mvindex(fields,10) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) |  eval result=mvindex(fields,5) | search api="SUBMIT_DOCUMENT" | search rtt > 25000| timechart span=1m count as SUBMIT_DOCUMENT_timeouts
```

#### Volume trend by operation
```
index=iam  sourcetype=iam_idv_outbound_transaction  | eval fields=split(_raw,",") | eval site=substr(host,1,3)| eval client=mvindex(fields,10) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) |  eval result=mvindex(fields,5) | eval error=mvindex(fields,6)|  eval dest=mvindex(fields,14)| eval ops=mvindex(fields,15) | search dest != "ECE" AND dest != "Provisioning" AND dest != "SMSF" AND dest !="CLIENT_SERVICE" AND dest !="FeatureLimitService" AND  dest !="ETS" | timechart span=1h count by ops
```
#### Load Test performance analysis 
#### ECE
```
index=iam host=TTN*IMP* source=*Txlog.*   | eval fields=split(_raw,",") | eval api=mvindex(fields,3) |eval rtt=mvindex(fields,13)| eval client=mvindex(fields,6)| eval result=mvindex(fields,14) | search client=EricssonMSClient
 OR client=EricssonSVClient| stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500 AND rtt < 2000)) AS Abnormal_Latency500ms,  count(eval(rtt > 2000)) AS Outliers2s, count(eval(result > 0)) AS errors by api | eval "Abnormal_Latency%"=round((Abnormal_Latency500ms/Totals)*100,1)
 | eval "Outliers%"=round((Outliers2s/Totals)*100,1) | eval "error%"=round((errors/Totals)*100,1) | sort api table api,Totals,Normal_Latency250ms,Abnormal_Latency500ms,"Abnormal_Latency%", Outliers2s, "Outliers%", errors, "error%"
```
#### CAC
```
index=iam host=TTN*IC*  source!=*notification*  | eval fields=split(_raw,",") | eval client=mvindex(fields,10) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) | eval result=mvindex(fields,5) | search client=EricssonMSClient OR client=EricssonSVClient|  stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500 AND rtt < 2000)) AS Abnormal_Latency500ms,  count(eval(rtt > 2000)) AS Outliers2s, count(eval(result == "ERROR")) AS errors by api | eval "Abnormal_Latency%"=round((Abnormal_Latency500ms/Totals)*100,1) | eval "Outliers%"=round((Outliers2s/Totals)*100,1) | eval "error%"=round((errors/Totals)*100,1) | sort api table api,Totals,Normal_Latency250ms,Abnormal_Latency500ms,"Abnormal_Latency%", Outliers2s, "Outliers%", errors, "error%"
```

#### some query ( sub query )
```
index=iam sourcetype=iam_pm_trans_log 
    [search index=iam UpdateIAMProfile sourcetype=iam_prov_trans_log | eval fields=split(_raw,",") | eval client=mvindex(fields,10) | eval result=mvindex(fields,5) | eval userid=mvindex(fields,12) | search client="9999" AND result="ERROR" | table userid | rename userid as search | format]
 | eval fields1=split(_raw,",") | eval type=mvindex(fields1,3) | eval email=mvindex(fields1,28) | eval user_id=mvindex(fields1,27) | search type="ChangeMail" | eval fields2=split(user_id,"=") | eval userid=mvindex(fields2,1) | table userid,email | dedup userid,email |   join userid 
[search index=iam SUBMIT_DOCUMENT sourcetype=iam_idv_transaction | eval fields=split(_raw,",") | eval client=mvindex(fields,10) | eval store_id=mvindex(fields,26) | eval rep_id=mvindex(fields,27) | eval doc_type=mvindex(fields,30) | eval userid=mvindex(fields,12) | table userid,rep_id,store_id,doc_type]  | join userid 
[search index=iam UpdateIAMProfile sourcetype=iam_prov_trans_log | eval fields=split(_raw,",") | eval client=mvindex(fields,10) |eval firstname=mvindex(fields,26) | eval lastname=mvindex(fields,27)| eval result=mvindex(fields,5) | eval userid=mvindex(fields,12) | search client="9999" AND result="ERROR" | table userid,firstname,lastname]
```

#### Regex
```
index=eda 310260663443642 IAM_create or IAM_update sourcetype IN (eda_flatlog_nbia eda_application eda_nbia_mod) Operation IN (IAM_LOGIN IAM_QueryByBAN IAM_QueryByContract IAM_create IAM_delete IAM_restore IAM_suspend IAM_update) ResponseCode!="0"  Operation=IAM_create  ResponseCode=400 | rex field=_raw "((\<errorCode\>)|(\<resultCode\>))(?<result>.+)((\<\/errorCode\>)|(\<\/resultCode\>))" | rex field=_raw "((\<errorMessage\>)|(\"\"error\_code\"\"\:\s\"\")|(\<ns2\:Reason\>)|(\<sub\:errorMessage\>)|(\"\,\"java\.net\.))(?<errorMessage>.+)((\<\/errorMessage\>)|(\"\")|(\")|(\<\/ns2\:Reason\>)|(\<\/sub\:errorMessage\>))" | rex mode=sed field=errorMessage "s/\d/"*"/g" | eval result=if(isnull(result),ResponseCode,result) | eval error= result +": "+ errorMessage | eval Response=if(isnull(errorMessage),result,error) | rex field=_raw "(\<serverName\>)(?<serverName>.+)(\<\/serverName\>)" | eval IAM_Actions_Raw=case(Operation="IAM_LOGIN",_raw,Operation="IAM_QueryByBAN",_raw,Operation="IAM_QueryByContract",_raw,Operation="IAM_create",_raw,Operation="IAM_delete",_raw,Operation="IAM_restore",_raw,Operation="IAM_suspend",_raw,Operation="IAM_update",_raw) | rex mode=sed field=IAM_Actions_Raw "s/[\]\}\{\[\"]/""/g s/\n/""/g" | rex field=IAM_Actions_Raw "(.+contract\:)(?<IAM_Contract>.*?)((billingAccount)|$)" | rex mode=sed field=IAM_Contract "s/\s{2,}/""/g s/,/\n/g" | rex field=msisdn "(.+msisdn\:)(?<MSISDN>.*?)((activationDate)|$)" | rex field=IAM_Actions_Raw "((.+billingAccount\:)|(.+billingAccounts\:))(?<IAM_Billing>.*?)((customer)|$)" | rex mode=sed field=IAM_Billing "s/\s{2,}/""/g s/,/\n/g" | rex field=IAM_Actions_Raw "((.+customer\:)|(.+customers\:))(?<IAM_Customer>.*?)((HTTP)|$)" | rex mode=sed field=IAM_Customer "s/\s{2,}/""/g s/,/\n/g" | eval Time=strftime (_time, "%m-%d-%Y %H:%M:%S:%Q %Z") | spath input=rawNbJsonReqAttr output=Request_Info path=requestInfo | rex field=Request_Info "(messageId)\"\:\"(?<Request_ID>.+?)\"\,\"" | rex field=messageId "(?<Request_ID2>.+?)\:" | eval Request_ID=if(isnull(Request_ID),Request_ID2,Request_ID) | rex mode=sed field=Request_Info "s/[\]\}\{\[\"]//g s/,/\n/g" | spath input=rawNbJsonReqAttr output=Line_Info path=lineInfo | rex mode=sed field=Line_Info "s/[\]\}\{\[\"]//g s/,/\n/g" | spath input=rawNbJsonReqAttr output=Feature_Info path=featureInfo | rex field=rawNbJsonReqAttr "^.+\"featureInfo\"\:(?<featureInfo_backup>.*)\]?$" | eval Feature_Info=if(isnull(Feature_Info),featureInfo_backup,Feature_Info) | rex mode=sed field=Feature_Info "s/[\]\}\{\[\"]//g s/,/\n/g" | rex field=rawNbJsonReqAttr "^.+currentfeatureInfo\"\:(?<currentFeature_Info>.*)$" | rex mode=sed field=currentFeature_Info "s/[\]\}\{\[\"]//g s/,/\n/g" | rex field=RequestId "(?<ER_ID>.+)\-.." | eval Features=if(isnull(currentFeature_Info),Feature_Info,currentFeature_Info) | eval Event_ID=if(isnull(RootLogId),ER_ID,RootLogId) | eval Event_ID=if(isnull(Event_ID),RequestId,Event_ID) | eval Function=if(((isnull(Operation)) AND (isnull(Target)) AND (isnull(Protocol)) AND (isnull(Request_ID))), _raw, Function)
```
 
```
index=iam  source=*Txlog*   | eval fields=split(_raw,",") | eval api=mvindex(fields,3) |eval rtt=mvindex(fields,13)| eval client=mvindex(fields,6) | eval result=mvindex(fields,14) |  eval error=mvindex(fields,15) |  stats count as Totals, count(eval(result == 0)) AS success, count(eval(error == "server_error")) AS cas_errors by api | eval "cas_errors%"=round((cas_errors/Totals)*100,1)| sort api table api,Totals,cas_errors,"cas_errors%"
```
#### Notification southbound latency buckets.
```
index=iam sourcetype=iam:outbound_transaction | eval fields=split(_raw,",") | eval site=substr(host,1,3)| eval HH=substr(mvindex(fields,0),12,2) | eval client=mvindex(fields,10) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) |  eval result=mvindex(fields,5) | eval error=mvindex(fields,6) | eval sb=mvindex(fields,14) |eval error=mvindex(fields,6) | search sb="SDG"  | stats count as Totals, count(eval(rtt < 250)) AS Normal_Latency250ms, count(eval(rtt > 500 AND rtt < 2000)) AS Abnormal_Latency500ms,  count(eval(rtt > 2000 AND rtt < 4000)) AS Outliers2s, count(eval(rtt > 4000 AND rtt < 5000)) AS Outliers4s, count(eval(rtt > 5000 AND rtt < 10000)) AS Outliers5s  by HH | eval "Abnormal_Latency%"=round((Abnormal_Latency500ms/Totals)*100,1) | eval "Outliers2s%"=round((Outliers2s/Totals)*100,1) | eval "Outliers4s%"=round((Outliers4s/Totals)*100,1) |eval "Outliers5s%"=round((Outliers5s/Totals)*100,1)  | sort HH table HH,Totals,Normal_Latency250ms,Abnormal_Latency500ms,"Abnormal_Latency%", Outliers2s, "Outliers2s%", Outliers4s, "Outlier4s%",Outliers5s, "Outlier5s%"
```
#### Outbound latency alarm 
```
index=iam NOT msisdn_linked_to_another_iam_account NOT msisdn_not_found NOT no_record_found NOT EricssonMSClient NOT EricssonSVClient | eval fields=split(_raw,",") | eval error_type=mvindex(fields,5) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) | stats count as Total, count(eval(rtt > 1000 AND rtt < 2000 )) AS Latency_1s, count(eval(rtt > 2000 AND rtt < 5000 )) AS Latency_2s, count(eval(rtt > 5000 AND rtt < 50000 )) AS Latency_5s, count(eval(rtt > 50000)) AS Latency_50s by api | search (api=authenticateWithTenant AND Latency_1s>25 AND Total>10) OR (api=BUILD_AUTHZ_REQUEST AND Latency_1s>3 AND Total>10) OR (api=CLEANUP_REGISTRATION_INFO AND Latency_2s>3 AND Total>5) OR (api=CheckMsisdn AND Latency_1s>3 AND Total>10) OR (api=CheckMsisdnV2 AND Latency_1s>3 AND Total>1000) OR (api=DELETE_DEVICE AND Latency_1s>3 AND Total>100) OR (api=DELETE_DOCUMENT AND Latency_1s>3 AND Total>50) OR (api=FINISH_FEDERATION_AUTHN_REQUEST AND Latency_1s>3 AND Total>10) OR (api=FINISH_ID_REGISTRATION AND Latency_5s>20 AND Total>20) OR (api=GetExternalAccessToken AND Latency_1s>3 AND Total>5) OR (api=GetProfile AND Latency_5s>50 AND Total>20000) OR (api=LinkMsisdn AND Latency_1s>3 AND Total>50) OR (api=MERGE_DOCUMENT AND Latency_50s>3 AND Total>5) OR (api=QUERY_FEDERATED_TOKENS AND Latency_1s>3 AND Total>1) OR (api=QueryAuthenticator AND Latency_1s>3 AND Total>10000) OR (api=RefreshContracts AND Latency_1s>10 AND Total>20000) OR (api=SUBMIT_DOCUMENT AND Latency_50s>5 AND Total>1000) OR (api=TIMER_TOKEN_REFRESH AND Latency_1s>3 AND Total>1) OR (api=TmoIdMerge AND Latency_1s>3 AND Total>5) OR (api=UpdateServicePermissionFlag AND Latency_5s>50 AND Total>1000) OR (api=ValidateBanPin AND Latency_5s>10 AND Total>50) OR (api=validatePortrait AND Latency_5s>2 AND Total>10)
like 1
```

#### Outbound Error alarm 
```
index=iam NOT msisdn_linked_to_another_iam_account NOT msisdn_not_found NOT no_record_found NOT EricssonMSClient NOT EricssonSVClient NOT invalid_request | eval fields=split(_raw,",") | eval error_type=mvindex(fields,5) | eval api=mvindex(fields,3) | eval rtt=mvindex(fields,4) | stats count as Total, count(eval(error_type="SUCCESS")) AS SuccessCount, count(eval(error_type!="SUCCESS")) AS ErrorCount by api | eval "error%"=round((ErrorCount/Total)*100,1) | search (api=authenticateWithTenant AND error%>80.0 AND Total>10) OR (api=BUILD_AUTHZ_REQUEST AND error%>10.0 AND Total>10) OR (api=CLEANUP_REGISTRATION_INFO AND error%>10.0 AND Total>5) OR (api=CheckMsisdn AND error%>10.0 AND Total>10) OR (api=CheckMsisdnV2 AND error%>10.0 AND Total>1000) OR (api=DELETE_DEVICE AND error%>100.0 AND Total>100) OR (api=DELETE_DOCUMENT AND error%>75.0 AND Total>50) OR (api=FINISH_FEDERATION_AUTHN_REQUEST AND error%>10.0 AND Total>10) OR (api=FINISH_ID_REGISTRATION AND error%>25.0 AND Total>25) OR (api=GetExternalAccessToken AND error%>10.0 AND Total>5) OR (api=GetProfile AND error%>10.0 AND Total>20000) OR (api=LinkMsisdn AND error%>75.0 AND Total>50) OR (api=MERGE_DOCUMENT AND error%>10.0 AND Total>5) OR (api=QUERY_FEDERATED_TOKENS AND error%>10.0 AND Total>1) OR (api=QueryAuthenticator AND error%>10.0 AND Total>10000) OR (api=RefreshContracts AND error%>10.0 AND Total>20000) OR (api=SUBMIT_DOCUMENT AND error%>10.0 AND Total>1000) OR (api=TIMER_TOKEN_REFRESH AND error%>10.0 AND Total>1) OR (api=TmoIdMerge AND error%>50.0 AND Total>5) OR (api=UpdateServicePermissionFlag AND error%>10.0 AND Total>1000) OR (api=ValidateBanPin AND error%>90.0 AND Total>50) OR (api=validatePortrait AND error%>10.0 AND Total>10)
```

#### Platform TPM count
```
index=iam sourcetype!=iam17_federation_outbound_log sourcetype!=iam17_rba-QueryUserActivity sourcetype!=iam17_rba-assessment
sourcetype!=iam17_rba-use sourcetype!=iam17_smsf_log sourcetype!=iam:outbound_transaction sourcetype!=iam_alert
sourcetype!=iam_client_configuration_readService sourcetype!=iam_idv_outbound_transaction sourcetype!=iam_ild
sourcetype!=iam_listener sourcetype!=iam_notification_trans_log sourcetype!=iam_ttn-alert sourcetype!=iam_ttn-listener
sourcetype!=mediaservice-transaction
NOT Client-Service NOT DP-Authentication-Traffic NOT DP-IDF NOT DP-IdentityManagement-Traffic NOT DP-OAuth-Traffic NOT DP-TMO-AA-Traffic
NOT DP-WebConsole-Traffic NOT EricssonMSCCIDClient NOT EricssonMSClient NOT EricssonMSClient_ NOT EricssonMSPhone20Client
NOT EricssonMSUprisingClient NOT EricssonInternalCall NOT IAM-AA-Adapter NOT cac2ece | timechart span=1m count 
```

#### IAM portal report
```
index=iam (source="/opt/iamtmo/ca/*" AND ("CheckMsisdn" OR  "FINISH_ID_REGISTRATION" OR  "GetVaultSummary" OR  "INIT_ID_REGISTRATION" OR  "LinkMsisdn" OR  "QUERY_FEDERATED_TOKENS" OR  "QueryTMOProfilesByBAN" OR  "RevokePermission" OR  "SUBMIT_DOCUMENT" OR  "UpdatePermissionState" OR  "UpdateProfile" OR  "UserInfoV1" OR  "UserInfoV2")) OR 
    (source="/var/exposure*xlog*" AND ("10050" OR  "20206" OR  "20204" OR  "20202" OR  "20203" OR  "20201" OR  "716" OR  "715" OR  "719" OR  "702" OR  "720" OR  "703" OR  "30002" OR  "30101" OR  "10051" OR  "10054")) OR
    (sourcetype="iam_eiil_transaction" AND ("add" OR "delete" OR "moddn" OR "modify" OR "search"))
| eval class=case(sourcetype="iam_eiil_transaction","EIIL",
                source like "/var/exposure/%xlog%","ECE",
                source like "/opt/iamtmo/ca/%","CAC",
                1==1, "other")
``` CAC looks like this:   API=mvindex(_raw,3), latency=mvindex(_raw,4), outcome=mvindex(_raw,5), reason=mvindex(_raw,6))
    ECE looks like this:   API=mvindex(_raw,3), latency=mvindex(_raw,13), outcome=mvindex(_raw,14), reason=mvindex(_raw,15)  
    EIIL looks like this:  API=mvindex(_raw,1), latency=mvindex(_raw,2), outcome=mvindex(_raw,3), reason=mvindex(_raw,4)``

| makemv delim="," allowempty=true _raw 
| eval API=case(class="EIIL","ldap".mvindex(_raw,1),
                class="ECE" ,mvindex(_raw,3),
                class="CAC",mvindex(_raw,3),
                1==1, "N/A"),
       latency=case(class="EIIL",mvindex(_raw,2),
                class="ECE" ,mvindex(_raw,13),
                class="CAC",mvindex(_raw,4),
                1==1, "N/A"),
       outcome=case(class="EIIL",mvindex(_raw,3),
                class="ECE" ,mvindex(_raw,14),
                class="CAC",mvindex(_raw,5),
                1==1, "N/A"),
       reason=case(class="EIIL",mvindex(_raw,4),
                class="ECE",mvindex(_raw,15),
                class="CAC",mvindex(_raw,6),
                1==1, "N/A") 
|eval API=case(
			API="10050","GetAllowedPasswordResetMethods",
			API="20206","IAM_BIOMETRIC_DEREGISTRATION",
			API="20204","IAM_BIOMETRIC_FINISH_AUTHENTICATION",
			API="20202","IAM_BIOMETRIC_FINISH_REGISTRATION",
			API="20203","IAM_BIOMETRIC_INIT_AUTHENTICATION",
			API="20201","IAM_BIOMETRIC_INIT_REGISTRATION",
			API="716","OAUTH_AUTHENTICATE_REQUEST",
			API="715","OAUTH_AUTHORIZE_REQUEST",
			API="719","OAUTH_CHANGE_PASSWORD",
			API="702","OAUTH_GET_ACCESSTOKEN",
			API="720","OAUTH_RESET_PASSWORD",
			API="703","OAUTH_VALIDATE_TOKEN",
			API="30002","QUERY_FEDERATION_IDENTITY",
			API="30101","RISK_ASSESSMENT",
			API="10051","Validate2ndFactorAnswers",
			API="10054","ValidateSecurityAnswers",
			1==1,API)
``` END API Evaluation ```
| eval Comp = case(in(API, "CheckMsisdn", "FINISH_ID_REGISTRATION", "GetVaultSummary","getVaultSummary", "INIT_ID_REGISTRATION", "LinkMsisdn","LinkMSISDN", "QueryTMOProfilesByBAN", "RevokePermission", "SUBMIT_DOCUMENT",       "UpdatePermissionState", "UpdateProfile", "UserInfoV1", "UserInfoV2"), "CAC",
     in(API, "IAM_BIOMETRIC_DEREGISTRATION", "IAM_BIOMETRIC_FINISH_AUTHENTICATION", "IAM_BIOMETRIC_FINISH_REGISTRATION", "IAM_BIOMETRIC_INIT_AUTHENTICATION", "IAM_BIOMETRIC_INIT_REGISTRATION", "OAUTH_AUTHENTICATE_REQUEST", "OAUTH_AUTHORIZE_REQUEST", "OAUTH_CHANGE_PASSWORD", "OAUTH_GET_ACCESSTOKEN", "OAUTH_RESET_PASSWORD", "OAUTH_VALIDATE_TOKEN", "QUERY_FEDERATION_IDENTITY", "RISK_ASSESSMENT", "Validate2ndFactorAnswers", "ValidateSecurityAnswers"), "ECE",
    in(API,"ldapadd", "ldapdelete", "ldapmoddn", "ldapmodify","ldapsearch"),"EIIL",
    1==1,"other"
)
| where Comp != "other"
| lookup iam_api_errors_map #----API----- as API, ------error----- as reason OUTPUTNEW "-----error_experience--------" as ErrorExperience
| eval ErrorExperience=if(outcome=="SUCCESS" OR outcome=="0","success",ErrorExperience)
| fillnull ErrorExperience value="n/a"
| eval S_Count=if(ErrorExperience=="success", 1, 0),
       Exp_Count=if(ErrorExperience=="experience_error", 1, 0),
       Sys_Count=if(ErrorExperience=="system_error", 1, 0),
       Use_Count=if(ErrorExperience=="user_error", 1, 0),
       Unk_Count=if(ErrorExperience=="n/a", 1, 0)
| stats count as Volume, avg(latency) as Latency, sum(S_Count) as Success,sum(Exp_Count) as Experience,sum(Sys_Count) as System,sum(Use_Count) as User, sum(Unk_Count) as Unknown  by Comp, API
| eval Error=Volume-Success, Error_pct=round(Error/Volume*100,0), Latency=round(Latency,0)
| addcoltotals labelfield=API label="Totals" Volume,Success, Experience, System, User, Unknown, Error
| table Comp, API, Volume, Latency, Success, Experience, System, User, Unknown, Error,  Error_pct
```

