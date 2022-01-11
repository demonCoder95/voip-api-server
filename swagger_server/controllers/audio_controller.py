from flask import Response
if __name__ != '__main__':
    from swagger_server.controllers.common.codec_processor import G711UProcessor
    from swagger_server.controllers.common.pcap_processor import PCAPProcessor
    from swagger_server.controllers.common.rtp_parser import RTPParser
else:
    from common.codec_processor import G711UProcessor
    from common.pcap_processor import PCAPProcessor
    from common.rtp_parser import RTPParser
    
import wave

def audio_cdr_id_get(cdr_id):  # noqa: E501
    """Return the Audio file of a call identified with cdrId

    This API endpoint identifies a call with the given cdrId and then provides the audio file of the decoded audio of the VoIP call in WAV format. # noqa: E501

    :param cdr_id: CDR-ID of the call to identify it.
    :type cdr_id: int

    :rtype: object
    """

    pcap_filename = 'sip-rtp-g729a.pcap'
    
    # TODO: Add PCAP fetching logic here for the module

    pcap_proc = PCAPProcessor(pcap_filename)
    packet_list = pcap_proc.dump_all_packets()

    # write the audio data in WAV object
    with wave.open('test.wav', 'wb') as f:
        f.setframerate(8000)
        f.setnchannels(1)
        f.setsampwidth(4)
        total_payload = None
        for each_packet in packet_list:    
            parser = RTPParser(each_packet)
            rtp_payload, rtp_header = parser.parse()
            total_payload += rtp_payload
        codec_proc = G711UProcessor(total_payload)
        f.writeframesraw(codec_proc.decode())

    audio_data = open('test.wav', 'rb').read()
    resp = Response(audio_data, '200', {
        'Content-Disposition': 'attachment;filename=test.wav;'
    })
    return resp
        