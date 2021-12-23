
from flask import Response
import paramiko
import mysql.connector
from paramiko.client import SSHClient
from paramiko.sftp_client import SFTPClient

def pcap_get(cdr_id, disable_rtp=None):  # noqa: E501
    """Return a PCAP with SIP and RTP of call given CDR ID.

    This endpoint retrieves Packet Capture (PCAP) of the call as identified by a provided CDR-ID. Additionally, only SIP can be retrieved by specifying &#x27;disable_rtp&#x3D;1&#x27;. # noqa: E501

    :param cdr_id: The CDR-ID to identify the call for PCAP.
    :type cdr_id: int
    :param disable_rtp: The flag to disable RTP in the PCAP.
    :type disable_rtp: int

    :rtype: Object
    """
    # need to determine the call-id and calldate of the call, from the CDR DB
    db_conn = mysql.connector.connect(
        user='monitor',
        password='xflow',
        host='172.30.219.1',
        database='voipmonitor'
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
    print(f"Calldate: {call_date}, Call-ID: {call_id}")
    
    sniffer_ip = "192.168.10.2"
    username = "root"
    password = "xflow@123"
    spool_dir = "/var/spool/voipmonitor"

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
        print("REMOTE COMMAND OUTPUT:")
        for each_line in stdout.readlines():
            print(each_line)
    else:
        print("No RTP for this CDR-ID!")

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