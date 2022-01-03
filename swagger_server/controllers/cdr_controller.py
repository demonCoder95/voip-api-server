from typing import List

from swagger_server.models.cdr import CDR  # noqa: E501
from swagger_server.models.cdr_list import CDRList

#imports for the MySQL connector
import mysql.connector

# The CODEC lookup dictionary to convert Payload Type (PT) into
# Payload name string.
from swagger_server.controllers.common.rtp_parser import codec_lookup


# 'cdr' table schema to control the output formatting
cdr_table_schema = ("caller, called, calldate, callend, duration, "
        "connect_duration, sipcallerip, sipcallerport, sipcalledip, "
        "sipcalledport, a_payload, b_payload, a_last_rtp_from_end, "
        "b_last_rtp_from_end")

# 'cdr_next' table schema to control the output formatting
cdr_next_table_schema = ("fbasename")

# 'cdr_next_1' table schema to control the output formatting
# TODO: Add custom_header_* field information in the config of the controller.
# The current mapping is:
# custom_header_1 => IMSI-Contact
# custom_header_2 => IMSI-Request
# custom_header_3 => Cell_ID_Caller
# custom_header_4 => Cell_ID_Called
# custom_header_5 => Session-ID
cdr_next_1_table_schema = ("custom_header_1, custom_header_2, "
    "custom_header_3, custom_header_4, custom_header_5")

# put in the DB connection functionality here for reuse
def db_handle_init():
    pass

def db_handle_process_query():
    pass

def create_cdr_object(cdr_id, resp_cdr, resp_cdr_next, resp_cdr_next_1):
    return_cdr = CDR()

    # handle the case of missing CDR
    if resp_cdr is None:
        return return_cdr

    # populate an individual CDR otherwise
    return_cdr.cdr_id = str(cdr_id)
    return_cdr.caller = resp_cdr[0]
    return_cdr.called = resp_cdr[1]
    return_cdr.calldate = resp_cdr[2]
    return_cdr.callend = resp_cdr[3]
    return_cdr.duration = str(resp_cdr[4])
    return_cdr.connect_duration = str(resp_cdr[5])
    return_cdr.sipcallerip = str(resp_cdr[6])
    return_cdr.sipcallerport = str(resp_cdr[7])
    return_cdr.sipcalledip = str(resp_cdr[8])
    return_cdr.sipcalledport = str(resp_cdr[9])
    return_cdr.codec_a = codec_lookup[resp_cdr[10]]
    return_cdr.codec_b = codec_lookup[resp_cdr[11]]
    return_cdr.a_last_rtp_from_end = str(resp_cdr[12])
    return_cdr.b_last_rtp_from_end = str(resp_cdr[13])

    if resp_cdr_next is not None:
        return_cdr.call_id = resp_cdr_next[0]
    else:
        return_cdr.call_id = ""

    # The current mapping is:
    # custom_header_1 => IMSI-Contact
    # custom_header_2 => IMSI-Request
    # custom_header_3 => Cell_ID_Caller
    # custom_header_4 => Cell_ID_Called
    # custom_header_5 => Session-ID
    # handle the case of missing entry in 'cdr_next_1' table
    if resp_cdr_next_1 is None:
        resp_cdr_next_1 = ("", "", "", "", "")
        
    return_cdr.imsi_contact = str(resp_cdr_next_1[0])
    return_cdr.imsi_request = str(resp_cdr_next_1[1])
    return_cdr.cell_id_caller = str(resp_cdr_next_1[2])
    return_cdr.cell_id_called = str(resp_cdr_next_1[3])
    return_cdr.session_id = str(resp_cdr_next_1[4])

    return return_cdr



def calls_cdr_id_get(cdr_id):  # noqa: E501
    """Return a list of Call Data Records (CDRs).

    This endpoint is currently being used for getting the CDR for a specific call, by providing the CDR-ID as &#x27;/calls/{cdr-id}&#x27;. # noqa: E501

    :param cdr_id: The CDR-ID of the call for which to retrieve the CDR.
    :type cdr_id: int

    :rtype: CDR
    """
    # initiate a database connection
    # TODO: add connection parameters to config file
    db_conn = mysql.connector.connect(
        user='monitor',
        password='xflow',
        host='172.30.219.1',
        database='voipmonitor'
    )

    # Get the DB cursor
    db_cur = db_conn.cursor()

    # the query to perform on the database to fetch some of the fields
    db_query_cdr = (
        f"SELECT {cdr_table_schema} FROM cdr WHERE ID={cdr_id}"
    )
    db_query_cdr_next = (
        f"SELECT {cdr_next_table_schema} FROM cdr_next WHERE cdr_ID={cdr_id}"
    )
    db_query_cdr_next_1 = (
        f"SELECT {cdr_next_1_table_schema} FROM cdr_next_1 WHERE cdr_ID={cdr_id}"
    )

    # this function call is always used to fetch one CDR entry from the
    # database, therefore, fetchone() is used for all queries.
    db_cur.execute(db_query_cdr)
    resp_cdr = db_cur.fetchone()
    print(resp_cdr)

    db_cur.execute(db_query_cdr_next)
    resp_cdr_next = db_cur.fetchone()
    print(resp_cdr_next)

    db_cur.execute(db_query_cdr_next_1)
    resp_cdr_next_1 = db_cur.fetchone()
    print(resp_cdr_next_1)

    # all done, so close the cursor and connection with the database
    db_cur.close()
    db_conn.close()

    return create_cdr_object(cdr_id, resp_cdr, resp_cdr_next, resp_cdr_next_1)

def calls_get(offset, size):
    """Return a list of Call Data Records (CDRs).

    This endpoint will be used to retrieve CDR list using &#x27;offset&#x27; and &#x27;size&#x27; parameters. The CDR list will always have less than or equal to &#x27;size&#x27; number of entries. # noqa: E501

    :param offset: The CDR-ID offset to use for retrieving CDRs.
    :type offset: int
    :param size: The maximum number of CDRs to retrieve.
    :type size: int

    :rtype: CDRList
    """
    return_cdr_list = CDRList()

    # initiate a database connection
    # TODO: add connection parameters to config file
    db_conn = mysql.connector.connect(
        user='monitor',
        password='xflow',
        host='172.30.219.1',
        database='voipmonitor'
    )

    # Get the DB cursor
    db_cur = db_conn.cursor()

    # the query to perform on the database to fetch some of the fields
    db_query_cdr = (
        f"SELECT ID FROM cdr WHERE ID>={offset} LIMIT {size}"
    )
    
    db_cur.execute(db_query_cdr)
    resp_cdr = db_cur.fetchall()
    print(resp_cdr)
    # all done, so close the cursor and connection with the database
    db_cur.close()
    db_conn.close()

    # list object to populate all the CDR responses
    cdrs_list = list()

    # Fetch all the CDR records as per the CDR IDs and populate the list
    for each_cdr_id in resp_cdr:
        cdrs_list.append(calls_cdr_id_get(each_cdr_id[0]))

    # attach the list to the response object
    return_cdr_list.cdr = cdrs_list

    # return the populated list
    return return_cdr_list
