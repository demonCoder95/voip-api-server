
from flask import Response
import paramiko
import mysql.connector

from swagger_server.controllers.common.config_handler import ConfigHandler

import logging

# Setup logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/' + __name__ + '.log')
formatter = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Setup the config handler for this module
config_handler = ConfigHandler()

def pcap_get(cdr_id, disable_rtp=None):  # noqa: E501
    """Return a PCAP with SIP and RTP of call given CDR ID.

    This endpoint retrieves Packet Capture (PCAP) of the call as identified by a provided CDR-ID. Additionally, only SIP can be retrieved by specifying &#x27;disable_rtp&#x3D;1&#x27;. # noqa: E501

    :param cdr_id: The CDR-ID to identify the call for PCAP.
    :type cdr_id: int
    :param disable_rtp: The flag to disable RTP in the PCAP.
    :type disable_rtp: int

    :rtype: Object
    """
    db_params = config_handler.get_params("database")
    # need to determine the call-id and calldate of the call, from the CDR DB
    db_conn = mysql.connector.connect(
        user=db_params["username"],
        password=db_params["password"],
        host=db_params["host"],
        database=db_params["database"]
    )
    db_cur = db_conn.cursor()
    # The schema for Call Date and Call-ID
    db_query_schema = "calldate, fbasename"
    # The query to retrieve this information from the database
    db_query_cdr_next = (
        f"SELECT {db_query_schema} FROM cdr_next WHERE cdr_ID={cdr_id}"
    )
    # Run the query to fetch data
    db_cur.execute(db_query_cdr_next)
    # This returns a single row since CDR-ID is unique.
    db_query_resp = db_cur.fetchall()
    # if there is no CDR entry, return nothing
    # TODO: improve this with a better response
    if db_query_resp is None or len(db_query_resp) == 0:
        return Response(None, 200, {
            'Content-Disposition': 'attachment;filename="";'
            })

    call_date = db_query_resp[0][0]
    call_id = db_query_resp[0][1]
    logger.info(f"Calldate: {call_date}, Call-ID: {call_id}")
    
    # TODO: update the backend to process multiple sniffers
    sniffer_params = config_handler.get_params("sniffers")[0]
    sniffer_ip = sniffer_params["host"]
    username = sniffer_params["username"]
    password = sniffer_params["password"]
    spool_dir = sniffer_params["spool_dir"]

    # FETCH THE PCAP FROM THE SNIFFER(S) USING THE CALLDATE INFORMATION
    # Day, Month, Hour and Minute need to be 0 filled 2 digit numbers
    pcap_filename = call_id + ".pcap"
    pcap_dir = f"{spool_dir}/{call_date.year}-{call_date.month:02d}-{call_date.day:02d}/{call_date.hour:02d}/{call_date.minute:02d}"
    sip_dir = pcap_dir + "/SIP/"
    rtp_dir = pcap_dir + "/RTP/"

    ssh_command = f"ls -l {rtp_dir} | grep {pcap_filename}"
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.connect(sniffer_ip, 22, username, password)
    stdin, stdout, stderr = ssh_client.exec_command(ssh_command)
    
    # DETERMINE IF RTP WAS FOUND FOR THIS CALL
    stdout_str = stdout.readlines()
    if len(stdout_str) != 0:
        logger.info("REMOTE COMMAND OUTPUT:")
        for each_line in stdout.readlines():
            logger.info(each_line)
    else:
        logger.info("No RTP for this CDR-ID!")

    # RETRIEVE THE SIP PCAP
    sftp_client = ssh_client.open_sftp()
    sftp_client.get(sip_dir + pcap_filename, localpath=f"pcap/{pcap_filename}")
    sftp_client.close()

    # CLEANUP THE SSH CHANNELS
    stdin.close()
    stdout.close()
    stderr.close()

    pcap_data = b''
    with open(f'pcap/{pcap_filename}', 'rb') as f:
        pcap_data = f.read()

    resp = Response(pcap_data, 200, {
        'Content-Disposition': f'attachment;filename="{pcap_filename}";'})
    return resp