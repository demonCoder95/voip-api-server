# swagger_client.DefaultApi

All URIs are relative to */v1alpha1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**calls_cdr_id_get**](DefaultApi.md#calls_cdr_id_get) | **GET** /calls/{cdr-id} | Return a list of Call Data Records (CDRs).

# **calls_cdr_id_get**
> CDR calls_cdr_id_get(cdr_id)

Return a list of Call Data Records (CDRs).

This endpoint is currently being used for getting the CDR for a specific call, by providing the CDR-ID as '/calls/{cdr-id}'.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
cdr_id = 789 # int | The CDR-ID of the call for which to retrieve the CDR.

try:
    # Return a list of Call Data Records (CDRs).
    api_response = api_instance.calls_cdr_id_get(cdr_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->calls_cdr_id_get: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cdr_id** | **int**| The CDR-ID of the call for which to retrieve the CDR. | 

### Return type

[**CDR**](CDR.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

