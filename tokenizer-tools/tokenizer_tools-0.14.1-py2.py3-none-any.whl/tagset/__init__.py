from tokenizer_tools.tagset.BMES import BMESEncoderDecoder

encoder_decoder_registry = {
    'BMES': BMESEncoderDecoder(),
    'BMES1': BMESEncoderDecoder(1),
    'BMES2': BMESEncoderDecoder(1)
}


def get_encoder_decoder(tagset):
    if tagset not in encoder_decoder_registry:
        raise ValueError("{} is not a valid tag scheme".format(tagset))

    return encoder_decoder_registry[tagset]
