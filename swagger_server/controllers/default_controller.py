import connexion
import six

from swagger_server.models.cdr import CDR  # noqa: E501
from swagger_server import util

#imports for the MySQL connector
import mysql.connector

# CODEC conversion dictionary
codec_lookup = {
    0: "PCMU",
    4: "G723",
    8: "PCMA",
    9: "G722",
    320: "AMR",
    321: "AMR-WB",
    18: "G729",
    400: "Telephone-event",
    None: ""
}

def calls_cdr_id_get(cdr_id):  # noqa: E501
    """Return a list of Call Data Records (CDRs).

    This endpoint is currently being used for getting the CDR for a specific call, by providing the CDR-ID as &#x27;/calls/{cdr-id}&#x27;. # noqa: E501

    :param cdr_id: The CDR-ID of the call for which to retrieve the CDR.
    :type cdr_id: int

    :rtype: CDR
    """
    # the CDR object to return
    return_cdr = CDR()

    # initiate a database connection
    db_conn = mysql.connector.connect(
        user='monitor',
        password='xflow',
        host='172.30.219.1',
        database='voipmonitor'
    )

    db_cur = db_conn.cursor()

    # the query to perform on the database to fetch some of the fields
    db_query_cdr = (
        "SELECT caller, called, calldate, callend, duration, "
        "connect_duration, sipcallerip, sipcallerport, sipcalledip, "
        "sipcalledport, a_payload, b_payload, a_last_rtp_from_end, "
        f"b_last_rtp_from_end FROM cdr WHERE ID={cdr_id}"
    )

    db_query_cdr_next = (
        f"SELECT fbasename FROM cdr_next WHERE cdr_ID={cdr_id}"
    )
    db_cur.execute(db_query_cdr)
    resp_cdr = db_cur.fetchone()
    print(resp_cdr)

    db_cur.execute(db_query_cdr_next)
    resp_cdr_next = db_cur.fetchone()
    print(resp_cdr_next)

    #TODO: transcode a_payload/b_payload numeric fields into strings
    # as codec_a and codec_b

    # Populating the CDR before returning
    return_cdr.cdr_id = cdr_id
    return_cdr.caller = resp_cdr[0]
    return_cdr.called = resp_cdr[1]
    return_cdr.calldate = resp_cdr[2]   # TODO: fix the datetime format
    return_cdr.callend = resp_cdr[3]    # TODO: fix the datetime format
    return_cdr.duration = resp_cdr[4]
    return_cdr.connection_duration = str(resp_cdr[5])   # TODO: fix this to 'connect_duration'
    return_cdr.sipcallerip = resp_cdr[6]
    return_cdr.sipcallerport = resp_cdr[7]
    return_cdr.sipcalledip = resp_cdr[8]
    return_cdr.sipcalledport = resp_cdr[9]
    return_cdr.codec_a = codec_lookup[resp_cdr[10]]   # TODO: translate this to CODEC string
    return_cdr.codec_b = codec_lookup[resp_cdr[11]]   # TODO: translate this to CODEC string
    return_cdr.a_last_rtp_from_end = str(resp_cdr[12])
    return_cdr.b_last_rtp_from_end = str(resp_cdr[13])

    return_cdr.call_id = resp_cdr_next[0]
    # all done, so close the cursor and connection with the database
    db_cur.close()
    db_conn.close()

    return return_cdr
