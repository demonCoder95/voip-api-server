# CDR

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cdr_id** | **str** | The CDR ID of the retrieved CDR. | [optional] 
**caller** | **str** | The MSISDN of the Caller from SIP &#x27;From&#x27; header | [optional] 
**called** | **str** | The MSISDN of the Callee from SIP &#x27;To&#x27; header | [optional] 
**calldate** | **str** | Start date and time of call in ISO 8601 format, with the configured timezone. It will be the time since the first SIP INVITE packet. | [optional] 
**callend** | **str** | End date and time of call in ISO 8601 format, with the configured timezone. It will be the time of the last received packet. | [optional] 
**call_id** | **str** | Call ID of the CDR in the database. | [optional] 
**duration** | **str** | Total duration of the call. (The interval between &#x27;callend&#x27; - &#x27;calldate&#x27; as number of seconds) | [optional] 
**connection_duration** | **str** | Number of seconds the call was connected (seconds between SIP 200 OK and callend). Value will be &#x27;null&#x27; if no SIP 200 OK packet is sent by the callee. Value will be &#x27;0&#x27; if SIP 200 OK is sent by the callee but no RTP packets were exchanged. | [optional] 
**sipcallerip** | **str** | IP address of the SIP caller. | [optional] 
**sipcallerport** | **str** | Port number of the SIP caller. | [optional] 
**sipcalledip** | **str** | IP address of the SIP callee. | [optional] 
**sipcalledport** | **str** | Port number of the SIP callee. | [optional] 
**codec_a** | **str** | CODEC of the caller for RTP stream. | [optional] 
**codec_b** | **str** | CODEC of the callee for RTP stream. | [optional] 
**a_last_rtp_from_end** | **str** | Last RTP packet arrival time for caller (in seconds) before the call was closed. | [optional] 
**b_last_rtp_from_end** | **str** | Last RTP packet arrival time for callee (in seconds) before the call was closed. | [optional] 
**cell_id_caller** | **str** | Cell ID of the caller. | [optional] 
**cell_id_called** | **str** | Cell ID of the callee. | [optional] 
**imsi_contact** | **str** | IMSI of the caller/callee from the Contact URI User Part parameter. | [optional] 
**imsi_request** | **str** | IMSI of the caller/callee from the Request URI User Part parameter. | [optional] 
**session_id** | **str** | Session-ID of the call | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

