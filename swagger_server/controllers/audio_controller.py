from flask import Response
if __name__ != '__main__':
    from swagger_server.controllers.common.codec_processor import CODECProcessor
    from swagger_server.controllers.common.pcap_processor import PCAPProcessor
else:
    from common.codec_processor import CODECProcessor
    from common.pcap_processor import PCAPProcessor

import logging
# Logger setup for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/' + __name__ + ".log")
formatter = logging.Formatter(
    '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def audio_call_id_get(call_id):  # noqa: E501
    """Return the Audio file of a call identified with callId

    This API endpoint identifies a call with the given callId and then provides the audio file of the decoded audio of the VoIP call in WAV format. # noqa: E501

    :param call_id: Call-ID of the call to identify it.
    :type call_id: str

    :rtype: object
    """
    # Use the Call-ID to identify the PCAP to be fetched for the call


def audio_cdr_id_get(cdr_id):  # noqa: E501
    """Return the Audio file of a call identified with cdrId

    This API endpoint identifies a call with the given cdrId and then provides the audio file of the decoded audio of the VoIP call in WAV format. # noqa: E501

    :param cdr_id: CDR-ID of the call to identify it.
    :type cdr_id: int

    :rtype: object
    """

    pcap_filename = 'g722-only.pcap'
    
    # TODO: Add PCAP fetching logic here for the module
 
    # 3. Parse the PCAP to extract the RTP payload from it.    
    pcap_proc = PCAPProcessor(pcap_filename)
    rtp_payload = pcap_proc.get_all_payload()
    logger.info("Got all payload from the PCAP.")

    # 4. Identify the Payload type
    payload_type = pcap_proc.get_payload_type()
    if payload_type is not None:
        logger.info("Got paylaod type!")
    else:
        logger.error("Couldn't get payload type!")

    # 5. Decode the encoded audio data and get the WAVeform file
    audio_filename = 'g722-only.wav'
    CODECProcessor(rtp_payload, payload_type, audio_filename).decode_payload()
    logger.info("Finished decoding payload.")

    # 6. Read the audio file into a buffer
    audio_data = open(audio_filename, 'rb').read()
    logger.info("Reading audio file to stream...")

    # 7. Return the response to the API call
    resp = Response(audio_data, '200', {
        'Content-Disposition': 'attachment;filename=test.wav;'
    })
    logger.info("Returning response.")
    return resp
        