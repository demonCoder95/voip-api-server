import connexion
import six

from swagger_server.models.cdr import CDR  # noqa: E501
from swagger_server.models.cdr_list import CDRList  # noqa: E501
from swagger_server import util


def calls_cdr_id_get(cdr_id):  # noqa: E501
    """Return a list of Call Data Records (CDRs).

    This endpoint is currently being used for getting the CDR for a specific call, by providing the CDR-ID as &#x27;/calls/{cdr-id}&#x27;. # noqa: E501

    :param cdr_id: The CDR-ID of the call for which to retrieve the CDR.
    :type cdr_id: int

    :rtype: CDR
    """
    return 'do some magic!'


def calls_get(offset, size):  # noqa: E501
    """Return a list of Call Data Records (CDRs).

    This endpoint will be used to retrieve CDR list using &#x27;offset&#x27; and &#x27;size&#x27; parameters. The CDR list will always have less than or equal to &#x27;size&#x27; number of entries. # noqa: E501

    :param offset: The CDR-ID offset to use for retrieving CDRs.
    :type offset: int
    :param size: The maximum number of CDRs to retrieve.
    :type size: int

    :rtype: CDRList
    """
    return 'do some magic!'


def pcap_get(cdr_id, disable_rtp=None):  # noqa: E501
    """Return a PCAP of a call

    This endpoint returns the Packet Capture (PCAP) of a call identified by the given CDR-ID. It contains both SIP and RTP by default. It accepts a flag &#x27;disable_rtp&#x27; to provide only SIP in the PCAP. # noqa: E501

    :param cdr_id: The CDR-ID of the call for which to retrieve the PCAP.
    :type cdr_id: int
    :param disable_rtp: The flag to disable RTP component in the PCAP of the call.
    :type disable_rtp: int

    :rtype: object
    """
    return 'do some magic!'
